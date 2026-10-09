---
name: zapier-make-integrations
metadata:
  category: No-Code Low-Code and Workflow Automation
description: Best practices for building robust integrations, CLI apps, and complex scenarios on Zapier and Make (Integromat). Use when building custom Zapier CLI triggers/actions, Make custom apps/modules (JSON I/O, IMLS), webhooks, data transformation, rate limiting, and failure handling.
compatibility: Zapier CLI (zapier-platform-cli), Make Custom Apps API, Node.js 18+, REST/JSON APIs
---

# Zapier & Make Integration Engineering Guidelines

This skill details design principles, implementation standards, authentication lifecycle management, and error resilience patterns for building custom Zapier CLI applications and Make (formerly Integromat) Custom Apps.

---

## 1. Integration Platform Architecture Comparison

| Feature Dimension | Zapier Platform CLI | Make Custom Apps (Integromat) |
|---|---|---|
| **Core Architecture** | Node.js JavaScript functions executing in V8 environment | Declarative JSON configuration directives (IMLS expressions) |
| **Trigger Mechanism** | REST Hooks (Static/Subscribe) or Polling (`z.request`) | Instant Webhooks or Polling scenarios |
| **Authentication** | OAuth2, Session, API Key, Basic, Custom (`z.dehydrate`) | OAuth2, API Key, Generic HTTP connection handlers |
| **Data Flow Logic** | Code-driven JavaScript objects (`bundle.inputData`) | JSON Mapper directives, RPC functions, custom IMLS language |
| **Execution Error Controls** | `z.errors.HaltAndCatchFire`, `ExpiredAuthError` | Directive handlers: `break`, `rollback`, `ignore`, `commit` |

---

## 2. Zapier Platform CLI Development

### 2.1 Trigger Implementation Patterns (REST Hooks vs Polling)

#### REST Hook Subscription (`triggers/lead_created.js`)
```javascript
const subscribeHook = async (z, bundle) => {
  const response = await z.request({
    url: `${bundle.authData.apiUrl}/v1/webhooks/subscribe`,
    method: 'POST',
    body: {
      target_url: bundle.targetUrl,
      event: 'lead.created'
    }
  });
  return response.data; // Stores subscription metadata (e.g., webhook ID)
};

const unsubscribeHook = async (z, bundle) => {
  const hookId = bundle.subscribeData.id;
  await z.request({
    url: `${bundle.authData.apiUrl}/v1/webhooks/subscriptions/${hookId}`,
    method: 'DELETE'
  });
  return { id: hookId };
};

const parseHookPayload = (z, bundle) => {
  // Extract record array from incoming POST payload
  const rawLead = bundle.cleanedRequest;
  return [{
    id: rawLead.id,
    first_name: rawLead.first_name,
    last_name: rawLead.last_name,
    email: rawLead.email,
    created_at: rawLead.created_at
  }];
};

const performListFallback = async (z, bundle) => {
  // Sample data fallback required for Zapier editor preview
  const response = await z.request({
    url: `${bundle.authData.apiUrl}/v1/leads`,
    params: { limit: 5, sort: 'desc' }
  });
  return response.data.leads;
};

module.exports = {
  key: 'lead_created',
  noun: 'Lead',
  display: {
    label: 'New Lead Created',
    description: 'Triggers instantly when a new lead is registered in the platform.'
  },
  operation: {
    type: 'hook',
    performSubscribe: subscribeHook,
    performUnsubscribe: unsubscribeHook,
    perform: parseHookPayload,
    performList: performListFallback,
    sample: {
      id: 'lead_102938',
      first_name: 'Jane',
      last_name: 'Doe',
      email: 'jane.doe@example.com',
      created_at: '2026-08-01T10:00:00Z'
    }
  }
};
```

### 2.2 Error Management & Auth Refreshes

```javascript
const performAction = async (z, bundle) => {
  const response = await z.request({
    url: `${bundle.authData.apiUrl}/v1/contacts`,
    method: 'POST',
    body: bundle.inputData
  });

  if (response.status === 401) {
    // Tells Zapier to trigger refresh token flow
    throw new z.errors.RefreshAuthError('Access token expired.');
  }

  if (response.status === 429) {
    // Rate limit hit - asks Zapier to auto-retry after delay
    const retryAfter = parseInt(response.headers.get('retry-after') || '60', 10);
    throw new z.errors.ThrottledError('Rate limit exceeded', retryAfter);
  }

  if (response.status >= 500) {
    // Transient error - trigger retry
    throw new z.errors.Error('Upstream service error', 'TransientServerError', 502);
  }

  return response.data;
};
```

---

## 3. Make Custom Apps Architecture (Integromat)

### 3.1 Module API Communication JSON Schema

Make custom app modules map API requests declaratively:

#### Communication Specification (`api.json`)
```json
{
  "url": "/v2/customers",
  "method": "POST",
  "qs": {},
  "headers": {
    "Authorization": "Bearer {{connection.accessToken}}",
    "Content-Type": "application/json"
  },
  "body": {
    "name": "{{parameters.name}}",
    "email": "{{parameters.email}}",
    "company": "{{parameters.company}}",
    "tags": "{{split(parameters.tags, \",\")}}"
  },
  "response": {
    "output": "{{body}}",
    "error": {
      "message": "[{{statusCode}}] {{body.error.message}}",
      "type": "DataError"
    }
  }
}
```

### 3.2 Expects Interface Definition (`expect.json`)
```json
[
  {
    "name": "name",
    "type": "text",
    "label": "Full Name",
    "required": true
  },
  {
    "name": "email",
    "type": "email",
    "label": "Email Address",
    "required": true
  },
  {
    "name": "company",
    "type": "text",
    "label": "Company Name",
    "required": false
  },
  {
    "name": "tags",
    "type": "text",
    "label": "Comma Separated Tags",
    "required": false
  }
]
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Polling without sorting by `created_at desc` | High | Missing data or duplicate trigger activations | Always sort trigger poll queries by descending timestamp/ID |
| Hardcoding access tokens without refresh handling | Critical | Workflows silently break when token expires | Implement `RefreshAuthError` in Zapier or OAuth refresh flow in Make |
| Returning single object instead of Array in Triggers | High | Zapier platform error during step execution | Triggers MUST return an array of objects `[ { id: 1, ... } ]` |
| Swallowing HTTP 429 status codes | Medium | Lost payloads under heavy API traffic | Throw `ThrottledError` to allow platform native retries |
| Missing `sample` payload in Zapier CLI trigger | Medium | User cannot set up downstream steps in Zapier UI | Provide accurate, comprehensive `sample` objects |

---

## 5. Verification Checklist

- [ ] **Zapier CLI Validation**: Run `zapier test` with 100% test coverage for authentication, triggers, and actions.
- [ ] **Deduplication Key**: Verify all triggers include a unique `id` string field for platform deduplication engines.
- [ ] **Make IMLS Syntax Check**: Ensure all functions in Make JSON (e.g., `{{lower(...)}}`, `{{split(...)}}`) pass validation.
- [ ] **OAuth Lifecycle**: Test token expiration and refresh token retrieval workflows explicitly.
