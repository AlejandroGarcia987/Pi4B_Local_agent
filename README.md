# Local LLM Agent on Raspberry Pi 4B with Telegram Bot & Tailscale

## Project Overview

This project implements a secure, reproducible, and self-contained local AI agent running entirely on a Raspberry Pi 4B (4GB).
The agent exposes a conversational interface through a Telegram bot, processes messages using a lightweight local LLM, and is remotely accessible through a Tailscale VPN tunnel.

This project demonstrates good practices in:

* Containerized Python service deployment.
* Secure configuration management.
* Structured development workflow.
* Running LLMs on constrained embedded hardware.

## Technical Stack & Architecture

* Hardware: Raspberry Pi 4 Model B (4GB RAM).
* Storage: NVMe SSD (for high-speed model loading and swap if required).
* Language Runtime: Python 3.11 (Docker base image: python:3.11-slim).
* LLM Backend: Ollama running natively on the host. Runs Gemma2:2B.
* Agent Container: Docker Compose service for the Python local agent.
* Libraries:
  * python-telegram-bot.
  * httpx.
  * pydantic-settings.
  * python-dotenv.
* Networking: Tailscale VPN for encrypted remote access to the Pi.

# Hardware Optimization: NVMe for Performance

Running LLMs on a Raspberry Pi requires fast disk access and careful memory management due to the device’s limited RAM.
The Pi’s SD card provides very low I/O throughput, making it unsuitable for loading multi-GB model weights or handling aggressive memory-mapped operations.

To overcome these limitations, the project applies two complementary optimizations on an external NVMe SSD:

  1. High-speed model storage (Memory-Mapped Model Files)
     The LLM is stored directly on the NVMe, enabling:
     *  High IOPS performance for memory-mapped model loading.
     *  Significantly reduced cold-start latency.
     *  Better stability for larger quantized models, avoiding the Raspberry Pi being stuck.
  2. NVMe-backed swap space (Extended Virtual Memory)
     An additional swap file on the NVMe SSD provides:
     * Extra virtual memory beyond the Pi’s physical 4 GB RAM.
     * Protection against out-of-memory crashes during inference.

 While NVMe-backed swap does not increase raw inference speed, it plays a crucial role in maintaining system stability and preventing process termination under heavy load.
 These optimizations make it feasible to run LLMs such as Gemma2:2B on a Raspberry Pi 4B while maintaining reasonable performance and reliability.

## Development & Deployment Workflow

  1. Local Development (PC).
     Code is developed and tested on a personal machine using VSCode.
  2. Version Control.
     Commits are pushed to a remote Git repository.
  3. Deployment on Raspberry Pi.
     More test are performed on the Raspberry Pi to verify functionality using a virtual enviroment (venv)
  4. Final execution runs inside Docker.

## Security and Configuration Management

  All sensitive configuration values are handled via a .env file:
  * Contains the TELEGRAM_BOT_TOKEN and other configurable settings.
  * Loaded and validated using pydantic-settings.
  * Excluded from version control using .gitignore

This ensures secure handling of secrets while keeping deployments reproducible.

## Connectivity: Remote Access via Telegram + Tailscale

  The local agent is controlled through a Telegram Bot, enabling:
    * Natural conversations with LLM
    * Remote access from any device
    * Zero port exposure thanks to Tailscale VPN, which routes traffic privately and securely
  This setup ensures that the Pi remains completely isolated from the public internet.
  Note: Tailscale was set up for a previous project, and the installation and configuration are not covered here. Please refer to https://tailscale.com/ for more information about using it on Raspberry Pi or different devices.

## System Execution Architecture

  Ollama runs natively on the Raspberry Pi for maximum performance.
  The Python AI agent runs in Docker, using network_mode: host.

## Current Capabilities

  * End-to-end LLM interaction from Telegram.
  * Configurable model parameters and timeouts.
  * Clean config loading via .env
  * Full Docker-based deployment of the agent.
  * Secure remote usage via VPN.

## Future Roadmap & Possible Enhancements (subject to verification and potential limitations of the Raspberry Pi hardware and the selected LLM model)
  1. LLM Extensions:
     * Improved prompt formatting and structured responses.
     * Different LLM models to improve performance.
  2. Tooling & Actions:
     * Google Calendar integration.
     * Programmed Tasks for daily reminders, weather information or news.
  3. Infrastructure Enhancements:
     * Streaming token-by-token responses to Telegram.
     * Worker queue for parallel tasks (non-blocking handlers).
     * Optional web dashboard for logs, metrics, and model monitoring.
