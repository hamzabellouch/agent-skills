# `nature-shared/` - shared support package for nature-* skills

This is an installable support package, not a standalone user workflow. It
contains references used by multiple `nature-*` skills so those sources remain
consistent and update together. A complete `npx skills` installation discovers
and manages it alongside the user-facing skills.

Sibling skills reference these files through relative paths such as:

```yaml
always_load:
  - ../nature-shared/core/reader-workflow.md
```

## Contents

| File | Consumers |
|---|---|
| `core/reader-workflow.md` | `nature-polishing`, `nature-writing` |
| `core/paper-type-taxonomy.md` | `nature-polishing`, `nature-writing` |
| `core/ethics.md` | `nature-polishing`, `nature-writing` |
| `core/terminology-ledger.md` | `nature-polishing`, `nature-writing`, `nature-reader`, `nature-paper2ppt` |
| `journal-formats/nat-comms.md` | `nature-polishing`, `nature-writing` |

Keep definitions and common references here only when two or more skills use
them. Task-specific workflow, diagnosis, output, and QA instructions belong in
the consuming skill.
