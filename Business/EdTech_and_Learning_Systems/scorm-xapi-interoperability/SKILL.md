---
name: scorm-xapi-interoperability
metadata:
  category: EdTech and Learning Management Systems
description: Implement e-learning interoperability standards including SCORM 1.2, SCORM 2004, Experience API (xAPI / Tin Can), and CMI5. Author compliant imsmanifest.xml packages, handle browser-to-LMS SCORM JavaScript API communication (LMSInitialize, LMSSetValue, cmi.core.lesson_status), emit xAPI Actor-Verb-Object statements, and synchronize with Learning Record Stores (LRS). Trigger when building e-learning courses, LMS integrations, or training tracking modules.
compatibility: SCORM 1.2 / 2004 4th Ed, xAPI 1.0.3, CMI5 specification
---

# SCORM & xAPI Interoperability Skill Guide

This skill governs standard implementation of interactive e-learning communication protocols, SCORM packaging manifests, and xAPI statement streaming to Learning Record Stores (LRS).

---

## 1. E-Learning Standard Architectural Comparison

```text
+-----------------------+---------------------------------------+---------------------------------------+
| Feature               | SCORM (1.2 / 2004)                   | xAPI (Tin Can) / CMI5                 |
+-----------------------+---------------------------------------+---------------------------------------+
| Environment           | Browser iframe inside LMS only        | Anywhere (Web, Mobile, VR, Offline)   |
| Communication         | Window JavaScript object (`API_1484`) | REST API (HTTP JSON Statements)       |
| Data Model            | CMI data elements (pass/fail, score)  | Actor-Verb-Object + Context Extensions|
| Storage Target        | LMS Database                          | Learning Record Store (LRS)           |
+-----------------------+---------------------------------------+---------------------------------------+
```

---

## 2. Production Code Implementations

### A. SCORM 1.2 JavaScript Bridge Interface (Client-Side)

```javascript
class SCORM12Bridge {
  constructor() {
    this.api = this.findLMSAPI(window);
    this.isInitialized = false;
  }

  findLMSAPI(win) {
    let attempts = 0;
    while (!win.API && win.parent && win.parent !== win && attempts < 10) {
      attempts++;
      win = win.parent;
    }
    return win.API || null;
  }

  initialize() {
    if (!this.api) {
      console.warn("[SCORM] No LMS API found. Running in standalone preview mode.");
      return false;
    }
    const result = this.api.LMSInitialize("");
    this.isInitialized = result === "true";
    return this.isInitialized;
  }

  setScore(scoreRaw, min = 0, max = 100) {
    if (!this.isInitialized) return;
    this.api.LMSSetValue("cmi.core.score.raw", String(scoreRaw));
    this.api.LMSSetValue("cmi.core.score.min", String(min));
    this.api.LMSSetValue("cmi.core.score.max", String(max));
  }

  completeCourse(passed = true) {
    if (!this.isInitialized) return;
    const status = passed ? "passed" : "failed";
    this.api.LMSSetValue("cmi.core.lesson_status", status);
    this.api.LMSCommit("");
  }

  terminate() {
    if (!this.isInitialized) return;
    this.api.LMSFinish("");
    this.isInitialized = false;
  }
}
```

### B. xAPI Statement Dispatcher to LRS (TypeScript / Node.js)

```typescript
import axios from "axios";

export interface XAPIStatement {
  actor: {
    name: string;
    mbox: string; // e.g. "mailto:learner@example.com"
  };
  verb: {
    id: string; // e.g. "http://adlnet.gov/expapi/verbs/completed"
    display: { "en-US": string };
  };
  object: {
    id: string; // Activity IRI
    definition: {
      name: { "en-US": string };
      description: { "en-US": string };
    };
  };
  result?: {
    score?: { scaled: number; raw: number; min: number; max: number };
    success?: boolean;
    completion?: boolean;
    duration?: string; // ISO 8601 duration: e.g. "PT15M30S"
  };
}

export class LRSClient {
  constructor(
    private readonly endpointUrl: string,
    private readonly authKey: string,
    private readonly authSecret: string
  ) {}

  public async sendStatement(statement: XAPIStatement): Promise<string> {
    const credentials = Buffer.from(`${this.authKey}:${this.authSecret}`).toString("base64");

    const response = await axios.post(
      `${this.endpointUrl.replace(/\\/$/, "")}/statements`,
      statement,
      {
        headers: {
          "Content-Type": "application/json",
          "X-Experience-API-Version": "1.0.3",
          Authorization: `Basic ${credentials}`,
        },
      }
    );

    return response.data[0]; // Returns recorded statement UUID
  }
}
```

---

## 3. Best Practices Checklist

- [ ] **LMS API Discovery:** Always recurse through `window.parent` and `window.opener` up to 10 levels to locate the SCORM API instance in multi-frame LMS setups.
- [ ] **Commit Frequency:** Call `LMSCommit("")` only on major milestone events (chapter finish, quiz submit) to avoid overwhelming LMS backend databases.
- [ ] **xAPI IRIs:** Use official ADL vocabulary IRIs (e.g. `http://adlnet.gov/expapi/verbs/passed`) rather than ad-hoc custom verbs.
