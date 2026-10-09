---
name: oauth2-oidc-security-flows
metadata:
  category: Identity Auth and Access Management
description: Implement enterprise OAuth 2.1 and OpenID Connect (OIDC) authorization code flow with Proof Key for Code Exchange (PKCE), state and nonce verification, refresh token rotation, token revocation, and centralized IdP federation (Keycloak, Auth0, Okta). Trigger when building secure authentication, single sign-on (SSO), or third-party delegated authorization.
compatibility: OAuth 2.1 RFC standards, OIDC Core 1.0, RFC 7636 (PKCE), RFC 7009
---

# OAuth 2.1 & OpenID Connect Security Flows Skill Guide

This skill governs standard, hardened implementation of OAuth 2.1 and OIDC authentication and authorization patterns for modern SPAs, mobile apps, and backend APIs.

---

## 1. Authorization Code Flow with PKCE (RFC 7636)

OAuth 2.1 mandates **PKCE (Proof Key for Code Exchange)** for all clients, deprecating the legacy Implicit Grant and Resource Owner Password Credentials (ROPC) grant.

```text
+--------+                               +---------------+
|        |--(A)- Generate code_verifier -|               |
|        |       and code_challenge      |               |
|        |                               |               |
|        |--(B)- GET /authorize -------->| Authorization |
|        |       &code_challenge=SHA256  | Server (IdP)  |
| Client |       &state=RANDOM_NONCE     | (Keycloak/    |
| (App)  |<-(C)- 302 Redirect with code -|  Auth0/Okta)  |
|        |                               |               |
|        |--(D)- POST /token ----------->|               |
|        |       code + code_verifier    |               |
|        |       &client_id              |               |
|        |<-(E)- Return Tokens ----------|               |
|        |       (access, id, refresh)   |               |
+--------+                               +---------------+
```

---

## 2. Production Implementation Patterns

### A. PKCE Generator & Validator (TypeScript / Node.js)

```typescript
import crypto from "node:crypto";

export interface PKCEPair {
  codeVerifier: string;
  codeChallenge: string;
}

/**
 * Generates a cryptographically secure PKCE code verifier and SHA256 challenge.
 */
export function generatePKCE(): PKCEPair {
  // RFC 7636 Section 4.1: High-entropy cryptographic random string (43 to 128 characters)
  const codeVerifier = crypto
    .randomBytes(32)
    .toString("base64url");

  const codeChallenge = crypto
    .createHash("sha256")
    .update(codeVerifier)
    .digest("base64url");

  return { codeVerifier, codeChallenge };
}

/**
 * Validates code_verifier against code_challenge on the authorization server.
 */
export function verifyPKCE(verifier: string, challenge: string): boolean {
  const computed = crypto
    .createHash("sha256")
    .update(verifier)
    .digest("base64url");

  return crypto.timingSafeEqual(
    Buffer.from(computed),
    Buffer.from(challenge)
  );
}
```

### B. OIDC Token Exchange & Validation Handler (Python)

```python
import time
import httpx
from jose import jwt, jwk
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class OIDCClient:
    def __init__(self, idp_base_url: str, client_id: str, client_secret: str | None = None):
        self.idp_base_url = idp_base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self._jwks_cache = None

    async def get_jwks(self) -> dict:
        if not self._jwks_cache:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.idp_base_url}/protocol/openid-connect/certs")
                resp.raise_for_status()
                self._jwks_cache = resp.json()
        return self._jwks_cache

    async def exchange_code(
        self,
        code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> TokenResponse:
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.idp_base_url}/protocol/openid-connect/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            return TokenResponse(**resp.json())

    async def verify_id_token(self, id_token: str, expected_nonce: str) -> dict:
        jwks = await self.get_jwks()
        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header["kid"]

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise ValueError(f"Public key {kid} not found in IdP JWKS")

        claims = jwt.decode(
            id_token,
            key,
            algorithms=["RS256"],
            audience=self.client_id,
            issuer=f"{self.idp_base_url}",
        )

        if claims.get("nonce") != expected_nonce:
            raise ValueError("Nonce mismatch: potential replay attack")

        return claims
```

---

## 3. Security Guidelines & Attack Mitigations

1. **Always Enforce PKCE:** Never allow plain `code_challenge_method=plain`; strictly reject anything except `S256`.
2. **State Parameter for CSRF:** Generate an unpredictable, encrypted or hashed `state` parameter stored in an HttpOnly session cookie, verified upon redirect.
3. **Nonce for Replay Prevention:** Include a unique `nonce` in `/authorize` requests and verify that the returned `id_token` contains an identical `nonce` claim.
4. **Refresh Token Rotation (RTR):** Invalidate the old refresh token whenever a new one is issued. If a revoked refresh token is presented, revoke all descended tokens immediately (compromise detection).
