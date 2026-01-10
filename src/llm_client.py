import asyncio
import json
from typing import AsyncIterator, Optional

import httpx

from src.config import settings

OLLAMA_URL = settings.LLM_URL
MODEL_NAME = settings.LLM_MODEL
LLM_TIMEOUT = settings.LLM_TIMEOUT_S
LLM_SEMAPHORE = asyncio.Semaphore(settings.LLM_MAX_CONCURRENCY)

async def _stream_generate(prompt: str, timeout_s: int = LLM_TIMEOUT) -> AsyncIterator[str]:
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": True}
    async with LLM_SEMAPHORE:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            async with client.stream("POST", OLLAMA_URL, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    for part in line.splitlines():
                        part = part.strip()
                        if not part:
                            continue
                        try:
                            j = json.loads(part)
                        except Exception:
                            continue
                        chunk = j.get("response") or j.get("text") or j.get("output") or ""
                        if chunk is not None:
                            yield chunk

async def ask_llm_stream(prompt: str, timeout_s: int = LLM_TIMEOUT, min_wait: float = 0.1) -> AsyncIterator[str]:
    buffer = []
    last_yield = 0.0
    async for piece in _stream_generate(prompt, timeout_s=timeout_s):
        buffer.append(piece)
        now = asyncio.get_event_loop().time()
        if now - last_yield >= min_wait or "\n" in piece:
            out = "".join(buffer)
            buffer = []
            last_yield = now
            yield out
    if buffer:
        yield "".join(buffer)


async def ask_llm(prompt: str, timeout_s: int = LLM_TIMEOUT) -> Optional[str]:
    try:
        async with LLM_SEMAPHORE:
            async with httpx.AsyncClient(timeout=timeout_s) as client:
                payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
                r = await client.post(OLLAMA_URL, json=payload)
                r.raise_for_status()
                data = r.json()
                if "response" in data and isinstance(data["response"], str):
                    return data["response"]
                if "output" in data and isinstance(data["output"], str):
                    return data["output"]
                if "choices" in data and isinstance(data["choices"], list):
                    choice = data["choices"][0]
                    return (choice.get("message", {}) or {}).get("content") or choice.get("text")
                return str(data)
    except Exception as e:
        print("ask_llm error: ",e)
        return None
