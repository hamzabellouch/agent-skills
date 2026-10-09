# Agent Skills

<h3 align="center">One Standard. Multiple AI Assistants. Instant Domain Expertise.</h3>

<p align="center">
Equip Claude Code, Gemini CLI, Cursor, and Codex CLI with 660+ production-grade, standard-compliant agent skills.
</p>


<img width="1374" height="767" alt="Agent-Skills" src="https://github.com/user-attachments/assets/78972f3e-b1dd-4476-a386-14153c24367e" />

## Overview

A curated, categorized collection of 660+ production-grade **Agent Skills** adhering to the open [Agent Skills Specification](https://agentskills.io/). This library empowers AI coding agents and LLM assistants with domain-specific capabilities, workflows, quality gates, and tool integrations.


### Repository Structure & Categories

The skills in this repository are organized into 9 core pillars categorized by granular specialization:

```text
agent-skills/
├── Science/                                       # Natural sciences, health informatics, environment & earth sciences
│   ├── Academic_Research_and_Methodology/         # Nature writing, academic peer review, research pipelines
│   ├── BioTech_and_Health_Sciences/               # FHIR R4/R5, HL7 integration, DICOM imaging, healthcare APIs
│   ├── Environmental_and_Energy_Science/          # GHG protocol carbon accounting, smart grid telemetry
│   └── Geospatial_and_Earth_Sciences/             # PostGIS, GeoJSON, Mapbox spatial analysis & remote sensing
│
├── Physics/                                       # Classical, quantum, relativistic, thermal, optical & electromagnetic physics
│   ├── Classical_Mechanics_and_Kinematics/        # Kinematics, dynamics, energy, gravitation, oscillations & fluid mechanics
│   ├── Thermodynamics_and_Statistical_Physics/    # Laws of thermodynamics, Carnot engines, entropy, ensembles & phase transitions
│   ├── Electromagnetism_and_Electrodynamics/      # Electrostatics, circuits, magnetostatics, Maxwell's equations & radiation
│   ├── Optics_and_Photonics/                      # Geometrical optics, lenses, wave interference, diffraction, lasers & Fourier optics
│   ├── Quantum_Physics_and_Simulation/            # Qiskit, Cirq, Bohr model, Schrödinger equation, perturbation theory & scattering
│   └── Relativity_and_Astrophysics/               # Special & General relativity, Lorentz transforms, Schwarzschild metric & GWs
│
├── Math/                                          # Pure & applied mathematics, statistics & optimization
│   ├── Statistics_and_Exploratory_Data_Analysis/  # Pandas/Polars EDA, statistical distributions, reproducible research
│   └── Differential_Privacy_and_Synthetic_Data/   # Differential privacy mathematical mechanisms, synthetic tabular data
│
├── Programming/                                   # Software engineering, backend, frontend, cloud, AI & low-level
│   ├── Software_Engineering_Practices/            # Superpowers planning, TDD, code review, distributed architectures
│   ├── Backend/                                   # Frameworks (FastAPI, Spring Boot), APIs (gRPC, REST), Databases, Events
│   ├── Frontend/                                  # Modern frameworks (Vue, Nuxt, Svelte), Desktop (Tauri, Electron), i18n
│   ├── Mobile/                                    # iOS SwiftUI, Android Jetpack Compose, Flutter, React Native Expo
│   ├── Cloud_DevOps_and_Infrastructure/           # GCP, AWS/Azure, Kubernetes, Terraform IaC, Networking, Observability
│   ├── Systems_and_Hardware/                      # Linux kernel & drivers, Embedded IoT (ESP32), FPGA EDA, Robotics (ROS 2)
│   ├── AI_Engineering_and_Platforms/              # Agents (Gemini, Claude, MCP), Gemma 4 ecosystem & training, Vector DBs, MLOps
│   ├── Data_Engineering/                          # PySpark, Delta Lake, dbt transformations, Airflow pipelines
│   ├── Web3_and_Blockchain/                       # Solidity & Foundry security, Anchor Solana Rust programs
│   ├── Automation_and_Integration/                # n8n workflow automation, Zapier & Make integration patterns
│   └── Testing_and_QA/                            # Playwright E2E automation, Cypress, k6 load testing
│
├── Design/                                        # UI/UX design systems, component styling, branding & visual assets
│   └── UI_UX_and_Design_Systems/                  # Anti-slop UI, UI/UX Pro Max, brand kits, design taste, web artifacts
│
├── Art/                                           # Digital art, generative algorithms, 3D, audio & video media
│   ├── Generative_and_Algorithmic_Art/            # Algorithmic p5.js art, canvas design, Slack GIF animations
│   ├── Game_Art_and_3D_Interactive/               # Unity DOTS/ECS C#, Unreal Engine 5 C++, Godot 4 GDScript
│   ├── Spatial_Design_and_XR/                     # WebXR 3D spatial design, visionOS Swift spatial computing
│   ├── Audio_Engineering_and_Sound_Design/        # Web Audio API synthesis, DSP audio filter effects
│   └── Digital_Media_and_Video_Production/        # FFmpeg ABR transcoding pipeline, WebRTC real-time media
│
├── Reference/                                     # References, documentation, office automation & knowledge management
│   ├── Personal_Knowledge_and_Notes/              # Obsidian markdown, bases, json-canvas, vault CLI
│   ├── Document_Standards_and_Formats/            # Microsoft Word (docx), PDF, PowerPoint (pptx), Excel (xlsx)
│   ├── Workspace_and_Productivity_Suites/         # Google Workspace (Gmail, Drive, Docs, Sheets, Keep, Tasks)
│   ├── Technical_Writing_and_Documentation/       # AI humanizer, natural writing style calibration
│   └── Methodologies_and_Interrogation/           # Requirements interviewing (interview-me), idea refinement
│
├── Business/                                      # Enterprise, commerce, financial engineering & product operations
│   ├── Fintech_and_Accounting/                    # Invoicing (ZATCA, Peppol), Payment Gateways (Stripe, PCI-DSS, FIX)
│   ├── E_Commerce_and_Retail/                     # Shopify Liquid & App SDK, WooCommerce payment & inventory sync
│   ├── Supply_Chain_and_Logistics/                # Vehicle routing problem (VRP), WMS inventory control
│   ├── Enterprise_Systems_CRM_ERP/                # Salesforce Apex & LWC, HubSpot CRM API integration
│   ├── Product_Management_and_Ops/                # PRD feature specification, user story mapping & backlog
│   ├── Marketing_and_Growth/                      # Growth marketing, SEO, copywriting, ads, CRO
│   ├── Customer_Operations_and_Support/           # Omnichannel helpdesk ticket routing, CSAT sentiment triage
│   └── EdTech_and_Learning_Systems/               # SCORM & xAPI interoperability, Canvas & Moodle LMS integrations
│
└── Security/                                      # Cybersecurity, code auditing, supply chain, IAM & compliance
    ├── Security_Audit_and_Code_Review/            # Automated vulnerability discovery harness, source code auditing
    ├── Offensive_Security_and_Pentesting/         # Application pentesting, offensive security, malware analysis
    ├── DevSecOps_and_Supply_Chain_Security/       # SLSA L3, Syft/CycloneDX SBOM, Cosign, HashiCorp Vault
    ├── Identity_and_Access_Management_IAM/        # OAuth 2.1 / OIDC security flows, JWT session hardening
    └── Governance_Compliance_and_Legal_Tech/      # GDPR & CCPA privacy engineering, SOC 2 compliance automation
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
    cp -r /path/to/agent-skills/Programming/Mobile/camerax /path/to/your-project/.agents/skills/
    ```

  - **macOS (Zsh / Terminal):**
    ```zsh
    mkdir -p /path/to/your-project/.agents/skills
    cp -R /path/to/agent-skills/Programming/Mobile/camerax /path/to/your-project/.agents/skills/
    ```

  - **Windows (PowerShell):**
    ```powershell
    New-Item -ItemType Directory -Path "C:\path\to\your-project\.agents\skills" -Force
    Copy-Item -Path "C:\path\to\agent-skills\Programming\Mobile\camerax" -Destination "C:\path\to\your-project\.agents\skills\" -Recurse
    ```

  - **Windows (Command Prompt / CMD):**
    ```cmd
    mkdir "C:\path\to\your-project\.agents\skills"
    xcopy /E /I "C:\path\to\agent-skills\Programming\Mobile\camerax" "C:\path\to\your-project\.agents\skills\camerax"
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
    cp -r /path/to/agent-skills/Programming/Software_Engineering_Practices/* /path/to/your-project/.claude/skills/
    ```

  - **macOS (Zsh / Terminal):**
    ```zsh
    mkdir -p /path/to/your-project/.claude/skills
    cp -R /path/to/agent-skills/Programming/Software_Engineering_Practices/* /path/to/your-project/.claude/skills/
    ```

  - **Windows (PowerShell):**
    ```powershell
    New-Item -ItemType Directory -Path "C:\path\to\your-project\.claude\skills" -Force
    Copy-Item -Path "C:\path\to\agent-skills\Programming\Software_Engineering_Practices\*" -Destination "C:\path\to\your-project\.claude\skills\" -Recurse
    ```

  - **Windows (Command Prompt / CMD):**
    ```cmd
    mkdir "C:\path\to\your-project\.claude\skills"
    xcopy /E /I "C:\path\to\agent-skills\Programming\Software_Engineering_Practices" "C:\path\to\your-project\.claude\skills"
    ```

* **Plugin Directory Flag:**
  Pass the skill category path directly when launching Claude Code:

  - **Linux / macOS:**
    ```bash
    claude --plugin-dir /path/to/agent-skills/Programming/Software_Engineering_Practices
    ```

  - **Windows:**
    ```powershell
    claude --plugin-dir "C:\path\to\agent-skills\Programming\Software_Engineering_Practices"
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
  cp -r /path/to/agent-skills/Programming/Backend/Databases_and_Caching/* /path/to/your-project/.codex/skills/
  ```

- **macOS (Zsh / Terminal):**
  ```zsh
  mkdir -p /path/to/your-project/.codex/skills
  cp -R /path/to/agent-skills/Programming/Backend/Databases_and_Caching/* /path/to/your-project/.codex/skills/
  ```

- **Windows (PowerShell):**
  ```powershell
  New-Item -ItemType Directory -Path "C:\path\to\your-project\.codex\skills" -Force
  Copy-Item -Path "C:\path\to\agent-skills\Programming\Backend\Databases_and_Caching\*" -Destination "C:\path\to\your-project\.codex\skills\" -Recurse
  ```

- **Windows (Command Prompt / CMD):**
  ```cmd
  mkdir "C:\path\to\your-project\.codex\skills"
  xcopy /E /I "C:\path\to\agent-skills\Programming\Backend\Databases_and_Caching" "C:\path\to\your-project\.codex\skills"
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
[WhatsApp](https://whatsapp.com/channel/0029Vb7MArw0LKZMpjjqOk2P) | [Facebook](https://facebook.com/hamzabellouch0) | [Instagram](https://instagram.com/hamzabellouch0) | [Twitter](https://twitter.com/hamzabellouch0) | [Telegram](https://t.me/hammzabellouch) | [LinkedIn](https://www.linkedin.com/in/hamzabellouch)
