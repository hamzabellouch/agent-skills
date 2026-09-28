---
name: jwt-session-management-hardening
metadata:
  category: Identity Auth and Access Management
description: Harden JWT-based authentication and session lifecycles using asymmetric signing (RS256/EdDSA), JWKS rotation, strict claims validation, Redis-backed sliding window sessions, revocation lists, and secure HttpOnly cookie storage. Trigger when implementing token validation, session revocation, or hardening API authentication.
compatibility: RFC 7519 (JWT), RFC 7517 (JWKS), Redis 7+
---

# JWT Session Management & Hardening Skill Guide

This skill specifies security rules and architectural implementations for issuing, verifying, storing, and revoking JSON Web Tokens (JWT) in high-security backend environments.

---

## 1. Storage Architecture: HttpOnly Cookies vs Bearer Tokens

```text
[ Browser Context ]
   |
   |-- NEVER store JWT in localStorage or sessionStorage (XSS Vulnerable!)
   |
   +---> Uses HttpOnly, Secure, SameSite=Strict / Lax Cookie
             |
             v (Automated Cookie Transport)
[ Reverse Proxy / API Gateway ]
   |
   +---> Extracts JWT from Cookie or Authorization: Bearer <token>
   +---> Validates signature using Public JWKS (Asymmetric RS256/EdDSA)
   +---> Checks Revocation / Blacklist in Redis
             |
             v
[ Internal Microservices (Context Propagated via Verified Claims) ]
```

---

## 2. Production Hardening Implementation

### A. JWT Verification & Claim Assertion (Python / PyJWT)

```python
import time
from typing import Any
import jwt
from jwt import PyJWKClient


class JWTVerifier:
    def __init__(self, jwks_url: str, expected_issuer: str, expected_audience: str):
        self.jwks_client = PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)
        self.issuer = expected_issuer
        self.audience = expected_audience

    def decode_and_validate(self, token: str) -> dict[str, Any]:
        # 1. Fetch matching public key by kid header
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)

        # 2. Strict cryptographic validation
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "EdDSA"],  # Explicit algorithm whitelist
            issuer=self.issuer,
            audience=self.audience,
            options={
                "require": ["exp", "iat", "nbf", "iss", "aud", "sub", "jti"],
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
                "verify_iss": True,
                "verify_aud": True,
            },
            leeway=10,  # 10 seconds clock skew tolerance
        )
        return payload
```

### B. Redis Revocation List & Sliding Session (Go)

```go
package session

import (
	"context"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

type SessionManager struct {
	rdb *redis.Client
}

func NewSessionManager(rdb *redis.Client) *SessionManager {
	return &SessionManager{rdb: rdb}
}

// RevokeToken marks a JWT ID (jti) as revoked until its natural expiration.
func (sm *SessionManager) RevokeToken(ctx context.Context, jti string, expiresAt time.Time) error {
	ttl := time.Until(expiresAt)
	if ttl <= 0 {
		return nil // Already naturally expired
	}
	key := fmt.Sprintf("jwt:blacklist:%s", jti)
	return sm.rdb.Set(ctx, key, "revoked", ttl).Err()
}

// IsRevoked checks if the token jti is present in the blacklist.
func (sm *SessionManager) IsRevoked(ctx context.Context, jti string) (bool, error) {
	key := fmt.Sprintf("jwt:blacklist:%s", jti)
	val, err := sm.rdb.Exists(ctx, key).Result()
	if err != nil {
		return false, err
	}
	return val > 0, nil
}

// RefreshSlidingSession extends user activity timestamp.
func (sm *SessionManager) RefreshSlidingSession(ctx context.Context, userID string, maxInactivity time.Duration) error {
	key := fmt.Sprintf("user:session:%s", userID)
	return sm.rdb.Expire(ctx, key, maxInactivity).Err()
}
```

---

## 3. Mandatory Security Checklist

- [ ] **Algorithm Whitelisting:** Explicitly allow only `["RS256"]` or `["EdDSA"]`. Strictly disallow `none` or symmetric keys `HS256` if verified against an external IdP.
- [ ] **Short Access Lifetimes:** Set Access Token expiration between 5 to 15 minutes max.
- [ ] **Mandatory `jti` Claim:** Ensure every token includes a unique `jti` (UUID v4) to enable individual token blacklisting.
- [ ] **Cookie Flags:** When using browser cookies, enforce:
  `Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Lax; Path=/`
