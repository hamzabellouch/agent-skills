# Contributing

Thank you for your interest in contributing to **Agent Skills**! Agent Skills is a curated collection of production-grade agent skills adhering to the open Agent Skills Specification, designed to equip AI assistants—including Claude Code, Gemini CLI, Cursor, and Codex CLI—with domain-specific workflows and capabilities.

Before submitting a bug report or feature request, please search existing issues (including closed ones) to ensure it hasn't already been reported or discussed. If there are no duplicates, feel free to submit a new issue using the appropriate template.

**Please note:** Issues that do not use existing templates or lack sufficient detail may be closed without review.

For questions or any other ideas to improve, you can join our official e-mail : hamzabellouchcontact@gmail.com or [Social Media platforms](https://sites.google.com/view/hamzabellouch/).


## Disclaimer

Agent Skills is an active open-source project focused on providing reliable, standardized, and production-grade capabilities for AI coding agents. While we strive for consistency and quality across all domains, contributions and feedback are always welcome to improve workflows, instructions, and integration.



## Bug Reports

When submitting a bug report, please make sure your issue contains **sufficient information** to reproduce the problem. Useful details include:

- Skill name and category path
- Target AI assistant (Claude Code, Gemini CLI, Cursor, Codex CLI, etc.)
- Operating system and environment
- Steps to reproduce the issue or unexpected prompt behavior
- Error messages, logs, or validator output if applicable



## Feature Requests

Agent Skills aims to remain a comprehensive, modular, and standard-compliant library for AI coding agents. We welcome suggestions that introduce new domain skills, improve prompt precision, or enhance tooling and validation.

When suggesting a new feature, please consider:
- **Relevance:** Does the skill fit into one of the established domain pillars and adhere to the Agent Skills Specification?
- **Privacy & Safety:** Does it follow strict execution safety, sandbox boundaries, and read/write isolation?
- **Simplicity:** We prefer clear, deterministic, and modular instructions over bloated prompts that overwhelm context windows.



## Pull Requests

If you wish to contribute directly by submitting code:

1. **Discuss First:** Leave a comment under an existing issue or open a new issue describing the changes you plan to make before writing code.
2. **Avoid Conflicts:** Comment on the issue to let others know you are working on it to prevent duplicate efforts.
3. **Follow Code Style:** Ensure your skill includes a valid `SKILL.md` with standard YAML frontmatter (`name`, `description`), clear triggers, and cleanly organized scripts or references.



## New Contributors

If you are new to the project:
- Browse our open issues for beginner-friendly tasks marked as `good first issue` or `help wanted`.
- Feel free to ask clarifying questions directly on the issue thread!



## Building From Source

To explore and test Agent Skills locally:

1. **Prerequisites:**
   - [Git](https://git-scm.com/)
   - Python 3.10 or higher
   - Node.js 18 or higher (optional, for running JS validators and test suites)

2. **Steps:**
   ```bash
   # Clone the repository
   git clone https://github.com/hamzabellouch/agent-skills.git

   # Navigate to the project directory
   cd agent-skills
   ```
