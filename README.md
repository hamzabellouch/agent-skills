# Agent Skills

<h3 align="center">One Standard. Multiple AI Assistants. Instant Domain Expertise.</h3>

<p align="center">
Equip Claude Code, Gemini CLI, Cursor, and Codex CLI with 380+ production-grade, standard-compliant agent skills.
</p>


<img width="1374" height="767" alt="Agent-Skills" src="https://github.com/user-attachments/assets/78972f3e-b1dd-4476-a386-14153c24367e" />

## Overview

A curated, categorized collection of 380+ production-grade **Agent Skills** adhering to the open [Agent Skills Specification](https://agentskills.io/). This library empowers AI coding agents and LLM assistants with domain-specific capabilities, workflows, quality gates, and tool integrations.


### Repository Structure & Categories

The skills in this repository are organized into 26 clean domain categories:

```text
agent-skills/
├── AI API and Agent Platform/             # Gemini API, Vertex AI, Agent Platform, Claude API, MCP Builder
├── AI and Vector Databases/               # Qdrant, Milvus, Pinecone, Unsloth QLoRA, Axolotl Fine-tuning
├── Academic and Scientific Research/      # Nature writing/figures, Deep academic research, BioInformatics
├── Advanced Frontend Frameworks/          # Vue 3 / Nuxt 3, Svelte 5 Runes & SvelteKit, WebGL & Three.js 3D
├── Content and Writing/                   # AI humanizer, natural writing style calibration
├── Data Engineering and Pipelines/        # PySpark, Delta Lake, dbt transformations, Airflow, DuckDB & Polars
├── Databases and Caching/                 # Redis, MongoDB, Prisma ORM, DynamoDB single-table design
├── Desktop Application Development/       # Tauri v2 (Rust), Electron performance, .NET MAUI / WPF
├── DevSecOps and Supply Chain Security/   # SLSA L3, Syft/CycloneDX SBOM, Cosign, HashiCorp Vault, SAST/DAST
├── Documents and Files/                   # Microsoft Word (docx), PDF, PowerPoint (pptx), Excel (xlsx)
├── Embedded Systems and IoT/              # ESP32 FreeRTOS C++, MQTT v5 / CoAP Edge, Raspberry Pi Rust `rppal`
├── Event Driven Systems/                  # Apache Kafka, RabbitMQ, Saga Orchestration & Choreography
├── Financial and Fintech Engineering/     # PCI-DSS Payment Gateways (Stripe/Adyen), FIX 4.2/5.0, ISO 20022
├── Frontend Design and UI/                # Anti-slop UI, UI/UX Pro Max, frontend slides, web artifacts
├── Game Development and Interactive 3D/   # Unity DOTS/ECS C#, Unreal Engine 5 C++, Godot 4 GDScript
├── Google Cloud and GKE/                  # GKE clusters, Cloud Run, Cloud SQL, BigQuery, Bigtable, WAF
├── Google Workspace Automation/           # Gmail, Drive, Docs, Sheets, Keep, Tasks, Meet recipes & personas
├── Infrastructure as Code and Edge/       # Terraform / OpenTofu, Cloudflare Workers, Ansible playbooks
├── Marketing and Growth/                  # Growth marketing, copywriting, SEO, CRO, social media, ads
├── Mobile Development/                    # iOS SwiftUI, Flutter Riverpod/BLoC, React Native Expo JSI, Android
├── Obsidian and Notes/                    # Obsidian markdown, bases, json-canvas, vault CLI, defuddle
├── Performance and Load Testing/          # k6, Locust, Appium 2.0 Mobile POM testing
├── Productivity and Interrogation/        # Requirements interviewing (interview-me), idea refinement, skill creation
├── Search and Knowledge Graphs/           # Elasticsearch / OpenSearch, Neo4j / Memgraph, Hybrid BM25+Vector RRF
├── Software Engineering and Workflows/    # Superpowers planning, TDD, code review, Caveman compression
└── Web3 and Smart Contracts/              # Solidity & Foundry security, Anchor Solana Rust programs
```

### How to Integrate & Use Skills in Your Projects

All skills in this directory follow the standard `SKILL.md` format with YAML frontmatter:

```yaml
---
name: skill-name
description: Clear description of what the skill does and when the agent should trigger it.
---
```

#### Step 1: Clone the Repository
First, clone this repository locally:

```bash
git clone https://github.com/hamzabellouch/agent-skills.git
```

#### Step 2: Integrate Skills into Your Assistant

##### 1. Google Antigravity, AGY CLI & Gemini CLI

* **Project-Level (Specific Repository):**
  Copy the desired skill folder or category into your project's `.agents/skills/` directory:

  - **Linux (Bash):**
    ```bash
    mkdir -p /path/to/your-project/.agents/skills
    cp -r /path/to/agent-skills/"Mobile Development"/camerax /path/to/your-project/.agents/skills/
    ```

  - **macOS (Zsh / Terminal):**
    ```zsh
    mkdir -p /path/to/your-project/.agents/skills
    cp -R /path/to/agent-skills/"Mobile Development"/camerax /path/to/your-project/.agents/skills/
    ```

  - **Windows (PowerShell):**
    ```powershell
    New-Item -ItemType Directory -Path "C:\path\to\your-project\.agents\skills" -Force
    Copy-Item -Path "C:\path\to\agent-skills\Mobile Development\camerax" -Destination "C:\path\to\your-project\.agents\skills\" -Recurse
    ```

  - **Windows (Command Prompt / CMD):**
    ```cmd
    mkdir "C:\path\to\your-project\.agents\skills"
    xcopy /E /I "C:\path\to\agent-skills\Mobile Development\camerax" "C:\path\to\your-project\.agents\skills\camerax"
    ```

* **Global Level (All Projects):**
  Copy skill folders to your global configuration directory:
  - **Linux:** `~/.gemini/config/skills/`
  - **macOS:** `~/.gemini/config/skills/`
  - **Windows:** `%USERPROFILE%\.gemini\config\skills\`

##### 2. Claude Code (`claude`)

* **Project-Level Integration:**
  Copy desired skills into your project's `.claude/skills/` folder:

  - **Linux (Bash):**
    ```bash
    mkdir -p /path/to/your-project/.claude/skills
    cp -r /path/to/agent-skills/"Software Engineering and Workflows"/* /path/to/your-project/.claude/skills/
    ```

  - **macOS (Zsh / Terminal):**
    ```zsh
    mkdir -p /path/to/your-project/.claude/skills
    cp -R /path/to/agent-skills/"Software Engineering and Workflows"/* /path/to/your-project/.claude/skills/
    ```

  - **Windows (PowerShell):**
    ```powershell
    New-Item -ItemType Directory -Path "C:\path\to\your-project\.claude\skills" -Force
    Copy-Item -Path "C:\path\to\agent-skills\Software Engineering and Workflows\*" -Destination "C:\path\to\your-project\.claude\skills\" -Recurse
    ```

  - **Windows (Command Prompt / CMD):**
    ```cmd
    mkdir "C:\path\to\your-project\.claude\skills"
    xcopy /E /I "C:\path\to\agent-skills\Software Engineering and Workflows" "C:\path\to\your-project\.claude\skills"
    ```

* **Plugin Directory Flag:**
  Pass the skill category path directly when launching Claude Code:

  - **Linux / macOS:**
    ```bash
    claude --plugin-dir /path/to/agent-skills/"Software Engineering and Workflows"
    ```

  - **Windows:**
    ```powershell
    claude --plugin-dir "C:\path\to\agent-skills\Software Engineering and Workflows"
    ```

##### 3. Cursor IDE & Windsurf

1. Create a `.cursor/skills/` directory inside your target project repository.
2. Copy your desired skill folders (e.g., `camerax`, `test-driven-development`) into `.cursor/skills/`.
3. Cursor will automatically parse `SKILL.md` manifests and invoke instructions when relevant.

##### 4. Codex CLI (`codex`) & OpenCode

Copy the desired skill folders into your project's `.codex/skills/` directory:

- **Linux (Bash):**
  ```bash
  mkdir -p /path/to/your-project/.codex/skills
  cp -r /path/to/agent-skills/"Databases and Caching"/* /path/to/your-project/.codex/skills/
  ```

- **macOS (Zsh / Terminal):**
  ```zsh
  mkdir -p /path/to/your-project/.codex/skills
  cp -R /path/to/agent-skills/"Databases and Caching"/* /path/to/your-project/.codex/skills/
  ```

- **Windows (PowerShell):**
  ```powershell
  New-Item -ItemType Directory -Path "C:\path\to\your-project\.codex\skills" -Force
  Copy-Item -Path "C:\path\to\agent-skills\Databases and Caching\*" -Destination "C:\path\to\your-project\.codex\skills\" -Recurse
  ```

- **Windows (Command Prompt / CMD):**
  ```cmd
  mkdir "C:\path\to\your-project\.codex\skills"
  xcopy /E /I "C:\path\to\agent-skills\Databases and Caching" "C:\path\to\your-project\.codex\skills"
  ```

##### 5. Desktop AI Apps (AionUi, Cherry Studio, LibreChat)

* **Cherry Studio / AionUi:** `Settings -> Skills -> Add Local Skill` -> Select any skill folder (containing `SKILL.md`).
* **LibreChat:** List local skill paths in your `librechat.yaml` under `skills.local`.



### Best Practices

1. **Context Window Efficiency:** Copy only the relevant skill categories needed for your active project to keep prompt context focused and fast.
2. **Standard Compatibility:** Any AI coding assistant supporting the `SKILL.md` open specification will automatically detect skill descriptions and execute instructions seamlessly.


> [!WARNING]
> There is always a possibility of error, so we assume no responsibility for any inaccuracies.


### <a name="Copyright©2026"></a> Copyright © 2026

Thank you for engaging with us. For inquiries or collaboration, please contact:  
hamzabellouchcontact@gmail.com

Stay connected and follow us on:  
[Facebook](https://facebook.com/hamzabellouch1) | [Instagram](https://instagram.com/hamzabellouch0) | [Twitter](https://twitter.com/hamzabellouch0) | [Telegram](https://t.me/hammzabellouch) | [LinkedIn](https://www.linkedin.com/in/hamzabellouch)
