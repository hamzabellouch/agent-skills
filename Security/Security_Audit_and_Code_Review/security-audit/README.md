# Security Audit Skill (`security-audit`)

A production-grade coding-agent skill that transforms your AI assistant into an autonomous, defensive security auditor and vulnerability research harness. It orchestrates isolated agents through reconnaissance, coverage-led hunting, adversarial candidate validation, structured output, independent record verification, and target-neutral reporting.

Derived from the enterprise vulnerability discovery harness architecture with enhanced cross-platform compatibility (Windows, macOS, Linux) and dual runtime validation (Node.js & Python).

---

## What It Does (The 6-Phase Audit Harness)

The skill conducts a deterministic, source-first security audit in six structured phases:

1. **Reconnaissance** (`RECONNAISSANCE.md`): Maps architecture, trust boundaries, entrypoints, input surfaces, and produces `architecture.md` and `coverage-ledger.json`.
2. **Coverage-Led Hunting** (`HUNTING.md`): Allocates isolated hunter agents to discrete ledger units, systematically testing attack surfaces against 13 specialized vulnerability domains.
3. **Adversarial Candidate Validation** (`VALIDATION-AND-REPORTING.md`): Dispatches every candidate finding to a fresh, independent verifier tasked with attempting to disprove or falsify it.
4. **Structured Output** (`report-schema.json`): Generates strictly validated `confirmed`, `needs_validation`, and `rejected` records within `findings.json`.
5. **Independent Record Verification**: Fresh agents independently verify final source claims; material replacements receive additional independent review passes.
6. **Target-Neutral Reporting**: Generates client-ready deliverables: `REPORT.md`, `FINDINGS-DETAIL.md`, and `NEEDS-VALIDATION.md`.

---

## Operating Modes

- **Guidance Mode (Default)**: For ad-hoc security inquiries, focused code reviews, architectural advice, or triaging a specific bug. Operates read-only without creating run artifacts or modifying working directories.
- **Full Audit Mode**: Triggered upon explicit request for an end-to-end security audit, penetration test, or formal audit report deliverables. Executes the full 6-phase pipeline into an isolated output directory.

---

## Included Attack Class Guides (13 Specialized Playbooks)

| Playbook | Domain & Focus Areas |
| :--- | :--- |
| `AI-AND-LLM.md` | Prompt injection, indirect injection, insecure output handling, tool invocation risks, model extraction |
| `ATTACK-CLASSES.md` | Core vulnerability taxonomy: access control, SSRF, injection, desync, race conditions |
| `WEB-PROTOCOL-AND-AUTH.md` | HTTP request smuggling, cache deception, OAuth 2.1, OIDC, JWT, SAML, CORS, CSP |
| `CLIENT-SIDE.md` | DOM XSS, prototype pollution, cross-origin messaging, postMessage trust, UI redress |
| `MEMORY-SAFETY-AND-BINARY.md` | Buffer overflows, use-after-free, memory safety, kernel modules, integer wrapping |
| `CLOUD-AND-DEPLOYMENT.md` | Cloud IAM, Terraform/IaC risks, Kubernetes container escapes, metadata service abuse |
| `SUPPLY-CHAIN-AND-RELEASE.md` | Dependency confusion, typosquatting, CI/CD pipeline tampering, signing, SLSA L3 |
| `PROTOCOLS-RPC-AND-MESSAGING.md` | gRPC, Protobuf serialization, WebSockets, Kafka, AMQP message tampering |
| `RESOURCE-EXHAUSTION-AND-AVAILABILITY.md` | Denial of service (DoS), ReDoS, algorithmic complexity, connection pool starvation |
| `DATA-ISOLATION-AND-LIFECYCLE.md` | Multi-tenant isolation leaks, database retention, PII exposure, crypto-at-rest |
| `DESKTOP-MOBILE-AND-LOCAL-IPC.md` | Electron/Tauri IPC, deep links, Android Intent redirection, exported components |
| `RECONNAISSANCE.md` | Trust boundary mapping, surface enumeration, entrypoint discovery |
| `HUNTING.md` & `VALIDATION-AND-REPORTING.md` | Hunting wave orchestration, coverage critics, ledger validators |

---

## Cross-Platform Validation Tools

This enhanced version provides two zero-dependency validators supporting both **Node.js** and **Python**:

### 1. Node.js Validators (Windows, macOS, Linux)
```bash
# Validate findings against JSON schema
node validate-findings.cjs path/to/findings.json

# Validate coverage ledger
node validate-coverage-ledger.cjs path/to/coverage-ledger.json

# Run test suites
node validate-findings.test.cjs
node validate-coverage-ledger.test.cjs
```

### 2. Python Validators (Zero Dependencies)
```bash
# Validate findings JSON
python validate_findings.py path/to/findings.json

# Validate coverage ledger JSON
python validate_coverage_ledger.py path/to/coverage-ledger.json
```

---

## Integration

To use in your AI coding assistant:

- **Google Antigravity / Gemini CLI**: Place into `.agents/skills/security-audit` or global skills directory.
- **Claude Code**: Place into `.claude/skills/security-audit` or load with `--plugin-dir`.
- **Cursor / Windsurf**: Place into `.cursor/skills/security-audit`.
- **Codex CLI**: Place into `.codex/skills/security-audit`.
