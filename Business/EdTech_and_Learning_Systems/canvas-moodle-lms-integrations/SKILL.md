---
name: canvas-moodle-lms-integrations
metadata:
  category: EdTech and Learning Management Systems
description: Integrate educational applications with major LMS platforms (Canvas LMS, Moodle, Blackboard) using the IMS Global LTI 1.3 / LTI Advantage standard and REST APIs. Implement LTI launch security, Names and Role Provisioning Services (NRPS roster sync), Assignment and Grade Services (AGS gradebook writeback), and Deep Linking. Trigger when connecting third-party tools into university LMS platforms.
compatibility: 1EdTech LTI 1.3 Advantage, Canvas REST API, Moodle Web Services
---

# Canvas & Moodle LMS Integration Skill Guide

This skill governs standard implementation of LTI 1.3 Advantage protocols and REST API automation for enterprise learning platforms like Canvas and Moodle.

---

## 1. LTI 1.3 Advantage Security Architecture

LTI 1.3 replaces legacy shared-secret authentication with an **OIDC Third-Party Initiated Login & OAuth 2.0 JWT Launch**.

```text
[ Canvas / Moodle LMS ]                              [ Tool Provider Backend ]
         |                                                       |
         |--(1) OIDC Login Initiation (iss, login_hint, lti_id)->|
         |                                                       |
         |<-(2) 302 Redirect to LMS /api/lti/authorize ----------|
         |                                                       |
         |--(3) POST id_token (Signed JWT with Roles & Claims) ->|
         |                                                       |
         |         [ Tool validates signature against LMS JWKS ] |
         |                                                       |
         |<-(4) Render Tool Inside LMS iFrame -------------------|
```

---

## 2. Production Code Implementations

### A. LTI 1.3 Launch Token Verification (Python)

```python
import jwt
from jwt import PyJWKClient


class LTILaunchVerifier:
    def __init__(self, platform_jwks_url: str, client_id: str, platform_issuer: str):
        self.jwks_client = PyJWKClient(platform_jwks_url)
        self.client_id = client_id
        self.platform_issuer = platform_issuer

    def verify_launch_token(self, id_token: str) -> dict:
        signing_key = self.jwks_client.get_signing_key_from_jwt(id_token)

        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.client_id,
            issuer=self.platform_issuer,
            options={"require": ["iss", "aud", "exp", "sub", "https://purl.imsglobal.org/spec/lti/claim/message_type"]},
        )

        message_type = claims.get("https://purl.imsglobal.org/spec/lti/claim/message_type")
        if message_type != "LtiResourceLinkRequest":
            raise ValueError(f"Invalid LTI message type: {message_type}")

        return claims
```

### B. Canvas REST API Gradebook Writeback (TypeScript / Node.js)

```typescript
import axios from "axios";

export interface CanvasGradePayload {
  studentCanvasId: string;
  courseId: string;
  assignmentId: string;
  score: number;
  comment?: string;
}

export async function submitCanvasGrade(
  baseUrl: string,
  apiToken: string,
  payload: CanvasGradePayload
): Promise<void> {
  const url = `${baseUrl.replace(/\\/$/, "")}/api/v1/courses/${payload.courseId}/assignments/${payload.assignmentId}/submissions/${payload.studentCanvasId}`;

  await axios.put(
    url,
    {
      submission: {
        posted_grade: payload.score,
      },
      comment: payload.comment
        ? {
            text_comment: payload.comment,
          }
        : undefined,
    },
    {
      headers: {
        Authorization: `Bearer ${apiToken}`,
        "Content-Type": "application/json",
      },
    }
  );
}
```

---

## 3. Best Practices Checklist

- [ ] **State & Nonce Validation:** In the initial OIDC handshake, verify that the `state` parameter generated on login matches the `state` returned during the final launch POST.
- [ ] **Grade Precision:** In LTI Assignment and Grade Services (AGS), always send both `scoreGiven` and `scoreMaximum` as numeric values to prevent LMS rounding anomalies.
- [ ] **Token Expiration:** Cache LMS OAuth 2.0 access tokens and refresh them prior to expiry rather than generating a new token per roster sync call.
