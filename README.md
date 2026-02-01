# Local LLM Agent on Raspberry Pi 4B  
## Telegram Bot · Local LLM · Google Calendar · Docker · (Optional) Tailscale

## Project Overview

This project implements a local, tool-first AI agent running entirely on a Raspberry Pi 4B (4GB RAM). The agent exposes a conversational interface through Telegram, uses a local LLM only as a language interface, and executes deterministic, explicitly confirmed actions such as creating real Google Calendar events.

The focus of this project is not raw AI capability, but architecture, control, and reliability on constrained hardware:

- Running LLM-based agents on low-resource devices.
- Deterministic-first agent design with LLM-assisted parsing and explicit fallback.
- Secure API access (Telegram, Google Calendar) from a headless environment.
- Clean separation between infrastructure, tools, and agent logic.
- Containerized deployment with Docker.
- Deterministic execution of real-world actions.
- Safe failure modes and explicit human confirmation.

---

## Design Philosophy: Tool-First, LLM as Fallback (Not LLM-Driven)

The agent follows a tool-first architecture with very strict boundaries around the LLM.

Core principles:

1. User input is analyzed using deterministic rules and intent detection.
2. The LLM never decides whether an action should happen.
3. If the intent matches a known capability (e.g. calendar queries), the agent executes explicit Python code.
4. The LLM is only used to extract structured data from natural language or as a fallback if no action is required.

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
    |--Intent Detection (deterministic)
    |--Tool Router
    |--LLM Parser if required (JSON extraction only)
    |--Deterministic Logic (dates, validation)
    |--Tool Execution (Google Calendar API)
    |--LLM Fallback if required (Ollama → local model)
           │
           ▼
    User receives agent response

The agent operates as follows:

- Detect user intent.
- If intent matches a known tool → execute deterministic code.
- If create event action is detected, LLM extracts data and provides JSON.
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

## Google Calendar Integration (Read & Create)

The agent supports real Google Calendar interaction, including event creation.

### Event creation flow
1. User requests an action (e.g. "mañana a las 7 reunión con Ainhoa").
2. Intent CALENDAR_CREATE is detected.
3. The LLM extracts structured fields:
   - title
   - time
   - relative references (tomorrow, weekday, etc.)
4. All dates are resolved deterministically in Python using the system date.
5. The agent asks for explicit confirmation (yes / no).
6. The event is created only after confirmation.

### Calendar Query Flow (LLM Bypassed)
1. The user requests today’s agenda, either:
   - Explicitly, using the /today Telegram command.
   - Implicitly, using natural language (e.g. “¿qué eventos tengo hoy?”).
2. The intent CALENDAR_TODAY is detected using deterministic rules
   (command matching and keyword-based intent detection).
3. The LLM is completely bypassed for this flow.
4. The agent executes deterministic Python logic in order to resolve “today” using the system date and query Google Calendar for events within today’s time window.
5. Retrieved events are formatted and sent back to the user.
This allows the agent to respond correctly to messages like:
- “Eventos hoy”  
- “¿Qué tengo en la agenda?”  

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
- LLM-assisted structured parsing (JSON only)
- Explicit user confirmation
- Google Calendar event creation
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
- Scheduled tasks (daily summaries, reminders).
- Event duration support.
- Calendar availability queries
- Weather and news integrations.

### Infrastructure
- Streaming responses to Telegram.
- Background task queue.
- Optional monitoring dashboard.

---

## Examples of interactions with the agent

### Answering "/today" command.

Below is a real example of the agent running on a Raspberry Pi, interacting through Telegram.
The agent correctly responds both to the `/today` command and to natural language queries such as “Eventos hoy”, using intent detection instead of relying on the LLM.

<img width="348" height="756" alt="image" src="https://github.com/user-attachments/assets/35672da0-1a8b-4ee3-ab71-446a6626e708" />

### From Message to Real Event

1. Telegram interaction (user request and explicit confirmation):
    User requests the action in natural language and explicitly confirms before execution.
<img width="348" height="751" alt="creacion" src="https://github.com/user-attachments/assets/25a6e4eb-da28-48ac-8572-4d22d9bd85b1" />

2. Raw LLM structured output (parsing only):
    LLM output used exclusively for structured data extraction, never for decision-making.
   
<img width="900" height="207" alt="llm_raw" src="https://github.com/user-attachments/assets/f20b3986-5344-4bfb-bebc-1d88074b8004" />

3. Resulting Google Calendar event:
    Deterministic tool execution creates the real calendar event after confirmation.
   
<img width="450" height="322" alt="reunion_final" src="https://github.com/user-attachments/assets/3ba5f40f-4cf3-4610-bdde-aa22e92b2480" />

---
## About This Project

This is an evolving personal project focused on learning, experimentation, and architectural exploration.
The repository and documentation will continue to evolve as new features and improvements are implemented.
So, be patient... ;)

