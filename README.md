# Local LLM Agent on Raspberry Pi 4B  
## Telegram Bot · Local LLM · Google Calendar · Docker · (Optional) Tailscale

## Project Overview

This project implements a local AI agent running entirely on a Raspberry Pi 4B (4GB RAM).
The agent exposes a conversational interface through a Telegram bot, processes messages using a local LLM, and executes deterministic tools such as Google Calendar queries. The goal of the project is not raw performance, but to explore the real limits, trade-offs, and architectural patterns required to run an autonomous agent on constrained embedded hardware.

This repository is about:

- Running LLM-based agents on low-resource devices.
- Hybrid decision logic: deterministic rules + intent detection + LLM fallback.
- Secure API access (Telegram, Google Calendar) from a headless environment.
- Clean separation between infrastructure, tools, and agent logic.
- Containerized deployment with Docker.

---

## Design Philosophy: Tool-First, LLM as Fallback

This project intentionally avoids delegating all decisions to the LLM and follows a tool-first architecture for the agent.

1. User input is analyzed using deterministic rules and intent detection.
2. If the intent matches a known capability (e.g. calendar queries), the agent executes explicit Python code.
3. Only when no known intent is detected, the request is forwarded to the local LLM.

With this approach, a predictable and controllable behavior is achieved with low latency and reduced memory pressure which is critic in constrained hardware enviroments. The LLM is treated as a language interface, not as a decision oracle.

---

## Technical Stack & Architecture

### Hardware
- Raspberry Pi 4 Model B (4GB RAM)
- External NVMe SSD (USB 3.0)
- Active cooling (fan + heatsink)

### Software & Runtime
- Python 3.11
- Docker & Docker Compose
- Virtualenv for local testing
- Ollama (running natively on the host)

### LLM Backend
- Ollama running on the Raspberry Pi
- Models tested:
  - `gemma2:2b`
  - `qwen2.5:1.5b` (currently used)

During testing, `gemma2:2b` became unstable under memory pressure when running alongside other services.
For this reason, `qwen2.5:1.5b` was selected as a better trade-off between response quality and resource usage.

Model size and quantization are critical constraints on 4GB devices.

### Core Libraries
- `python-telegram-bot`
- `google-api-python-client`
- `google-auth`
- `httpx`
- `pydantic-settings`
- `python-dotenv`

---

## High-Level Architecture

    Telegram User
           │
           ▼
    Telegram Bot API
           │
           ▼
    Local Agent (Raspberry Pi 4B)
    ├─ Intent Router (rules / keywords)
    ├─ Tool Layer (Google Calendar)
    └─ LLM Fallback (Ollama → local model)
           │
           ▼
    User receives agent response

The agent operates as follows:

- Detect user intent.
- If intent matches a known tool → execute deterministic code.
- Otherwise → fallback to the local LLM.

---

## Hardware Optimization: NVMe for Performance & Stability

Running LLMs on a Raspberry Pi requires fast disk access and careful memory management.
The SD card provides very low I/O throughput, making it unsuitable for local LLM workloads.

This project applies two complementary optimizations using an external NVMe SSD:

### 1. High-Speed Model Storage
The LLM model files are stored on NVMe, enabling:
- High IOPS for memory-mapped model loading.
- Reduced cold-start latency.
- Improved stability for quantized models.

### 2. NVMe-Backed Swap Space
A swap file on the NVMe SSD provides:
- Additional virtual memory beyond the Pi’s physical 4GB RAM.
- Protection against out-of-memory crashes during inference.

While swap does not increase raw inference speed, it is essential for system stability under load.

---

## Google Calendar Integration (Headless & Secure)

The agent can read **today’s Google Calendar events** in two ways:

- Explicitly, using the `/today` Telegram command.
- Implicitly, through intent detection when the user writes natural language messages containing calendar-related keywords such as:
  - “hoy”
  - “eventos”
  - “agenda”
  - “calendario”

This allows the agent to respond correctly to messages like:
> “Eventos hoy”  
> “¿Qué tengo en la agenda?”  

without requiring a strict command-based interaction.

### Authentication (Headless)

Authentication is performed **without any graphical environment** on the Raspberry Pi:

- The OAuth flow is executed once on a host machine with a browser.
- Credentials and tokens are securely stored on disk.
- OAuth tokens are mounted read-only inside the Docker container.
- The running agent never performs OAuth flows.

This design ensures:

- No browser dependency on the Raspberry Pi.
- Minimal attack surface.
- Deterministic and reliable tool execution.

  ---

## Development & Deployment Workflow

1. **Local Development (PC)**  
   Code is developed and tested using VSCode and a Python virtual environment.

2. **Version Control**  
   Changes are committed and pushed to a remote Git repository.

3. **Raspberry Pi Validation**  
   Tests are executed directly on the Raspberry Pi using `venv`.

4. **Production Execution**  
   The agent runs inside Docker using Docker Compose.

---

## Security and Configuration Management

Sensitive configuration values are handled via a `.env` file:

- Telegram bot token and runtime configuration.
- Loaded and validated using `pydantic-settings`.
- Excluded from version control using `.gitignore`.

Secrets such as Google OAuth tokens are stored locally and mounted read-only inside the container.

---

## Connectivity: Telegram & (Optional) Tailscale

The agent is primarily accessed via **Telegram**, enabling:

- Remote usage from any device.
- No exposed ports on the Raspberry Pi.

Tailscale is available as an **optional component** for:
- Secure SSH access.
- Future local APIs or dashboards.

Tailscale setup is outside the scope of this repository.

---

## Current Capabilities

- Telegram-based conversational interface.
- Local LLM inference on Raspberry Pi.
- Deterministic Google Calendar queries (`/today`).
- Keyword-based intent detection for calendar-related queries (e.g. “hoy”, “eventos”, “agenda”), without requiring explicit commands.
- Intent-based routing with deterministic tools first and LLM fallback.
- Fully containerized deployment (Docker).
- Secure secret handling and read-only credentials inside containers.

---

## Future Roadmap & Possible Enhancements  
*(Subject to hardware and LLM limitations)*

### LLM & Agent Improvements
- Improved prompt structuring.
- Extended intent detection.
- Additional lightweight models.

### Tooling
- Create / delete calendar events.
- Scheduled tasks (daily summaries, reminders).
- Weather and news integrations.

### Infrastructure
- Streaming responses to Telegram.
- Background task queue.
- Optional monitoring dashboard.

---

## Example Interaction

Below is a real example of the agent running on a Raspberry Pi, interacting through Telegram.
The agent correctly responds both to the `/today` command and to natural language queries such as “Eventos hoy”, using intent detection instead of relying on the LLM.

<img width="348" height="756" alt="image" src="https://github.com/user-attachments/assets/35672da0-1a8b-4ee3-ab71-446a6626e708" />


---

## About This Project

This is an evolving personal project focused on **learning, experimentation, and architectural exploration**.
The repository and documentation will continue to evolve as new features and improvements are implemented.
So, be patient... ;)

