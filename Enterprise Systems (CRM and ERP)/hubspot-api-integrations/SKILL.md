---
name: hubspot-api-integrations
metadata:
  category: Enterprise Systems (CRM and ERP)
description: HubSpot CRM API v3 development, OAuth2 authentication, Custom Objects API, Batch CRM sync operations, Webhook subscriptions, and API rate limit management.
compatibility: HubSpot API v3, Node.js @hubspot/api-client, Python hubspot-api-client, OAuth2
---

# HubSpot CRM API v3 Integration Architecture

## Overview
This skill provides production standards for building enterprise integrations with the **HubSpot CRM API v3**. It covers OAuth2 authentication, Private App tokens, Custom Objects definition, high-performance batch updates, webhook event processing, and rate limit handling (150 requests/10 seconds bucket).

---

## 1. HubSpot Integration Principles

1. **Prefer Batch Endpoints over Single Operations**: Use `/crm/v3/objects/{objectType}/batch/create` and `/batch/update` to process up to 100 records per API call, minimizing network roundtrips and preserving API quota.
2. **Private App Access Tokens for Single Tenant**: Use Private App tokens (`Bearer pat-na1-...`) for server-to-server internal integrations; use OAuth2 flow only when building multi-tenant integrations for third-party merchants.
3. **Handle Rate Limits with Exponential Backoff**: Honor `X-HubSpot-RateLimit-Daily-Remaining` and `X-HubSpot-RateLimit-Interval-Milliseconds`. Handle `429 Too Many Requests` responses with jittered retry algorithms.
4. **CRM Associations Management**: Always explicitly define associations between records (e.g., Contact to Company, Deal to Custom Object) using explicit Association Spec IDs during object creation.
5. **Secure Webhook Verification**: Validate the `X-HubSpot-Signature-v3` header using the secret client key to verify event authenticity.

---

## 2. HubSpot CRM Data Flow Architecture

```
[ External System / ERP ]
       │
       │ 1. Batch Payload (100 Records / Chunk)
       ▼
[ Middleware / Integration Engine ] ──(Rate Limit Check: 10s Window)
       │
       │ 2. POST /crm/v3/objects/contacts/batch/create
       ▼
[ HubSpot CRM Core Engine ] ──(CRM Associations)──▶ [ Deals / Companies / Custom Objects ]
       │
       │ 3. Webhook Notifications (v3 Signature Verification)
       ▼
[ External Sync Subscriber ]
```

| Integration Pattern | Endpoint Prefix | Batch Capacity | Rate Limit Quota |
| :--- | :--- | :--- | :--- |
| **Contacts API** | `/crm/v3/objects/contacts` | 100 per call | 150 req / 10 sec (Standard) |
| **Companies API** | `/crm/v3/objects/companies` | 100 per call | 150 req / 10 sec |
| **Custom Objects API**| `/crm/v3/schemas` / `/objects/{type}` | 100 per call | Enterprise Tier Feature |
| **Associations API** | `/crm/v3/associations/{fromType}/{toType}/batch/create` | 100 per call | 150 req / 10 sec |

---

## 3. Anti-Patterns & Common Errors

* **Anti-Pattern: Sequential N+1 Single Object API Calls**
  * *Risk*: Exhaustion of rate limits within seconds, causing API lockout.
  * *Remediation*: Aggregate updates into batch endpoints (`/crm/v3/objects/contacts/batch/update`).
* **Anti-Pattern: Storing Access Tokens in Plain Text**
  * *Risk*: Full compromise of CRM contacts, deals, and PII.
  * *Remediation*: Store access tokens in encrypted key-value stores (AWS Secrets Manager, HashiCorp Vault).
* **Anti-Pattern: Polling the Search API for Changed Records**
  * *Risk*: Excessive API quota consumption and sync lag.
  * *Remediation*: Use HubSpot Webhook Subscriptions (`contact.creation`, `contact.propertyChange`).

---

## 4. Production Node.js Integration Snippets

### A. HubSpot Batch Contacts & Associations Engine (`hubspot_sync.js`)

```javascript
import { Client } from '@hubspot/api-client';

export class HubSpotSyncEngine {
  constructor(accessToken) {
    this.hubspotClient = new Client({ accessToken });
  }

  /**
   * Batch upsert contacts and associate them with a Company
   */
  async batchUpsertContactsWithCompany(contactsData, companyId) {
    try {
      const batchInput = contactsData.map(contact => ({
        properties: {
          email: contact.email,
          firstname: contact.firstName,
          lastname: contact.lastName,
          jobtitle: contact.jobTitle
        },
        associations: [
          {
            to: { id: companyId },
            types: [
              {
                associationCategory: 'HUBSPOT_DEFINED',
                associationTypeId: 1 // Primary Contact to Company Association Type
              }
            ]
          }
        ]
      }));

      // Execute batch create with high-efficiency single API call (up to 100 records)
      const response = await this.hubspotClient.crm.contacts.batchApi.create({
        inputs: batchInput
      });

      console.log(`[HUBSPOT] Successfully batch created ${response.results.length} contacts.`);
      return response.results;
    } catch (error) {
      if (error.statusCode === 429) {
        console.warn('[HUBSPOT RATE LIMIT] Rate limit exceeded. Retrying with backoff...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        return this.batchUpsertContactsWithCompany(contactsData, companyId);
      }
      console.error('[HUBSPOT ERROR]', error.body || error.message);
      throw error;
    }
  }
}
```

---

### B. HubSpot Webhook Signature v3 Validation Express Middleware (`hubspot_webhook.js`)

```javascript
import crypto from 'crypto';
import express from 'express';

const app = express();

/**
 * Validates HubSpot Webhook Signature v3
 */
function verifyHubSpotSignature(req, res, next) {
  const signatureHeader = req.headers['x-hubspot-signature-v3'];
  const timestampHeader = req.headers['x-hubspot-request-timestamp'];
  const clientSecret = process.env.HUBSPOT_CLIENT_SECRET;
  const requestUrl = `${req.protocol}://${req.get('host')}${req.originalUrl}`;

  // Prevent replay attacks (Reject requests older than 5 minutes)
  const FIVE_MINUTES_MS = 5 * 60 * 1000;
  if (Math.abs(Date.now() - Number(timestampHeader)) > FIVE_MINUTES_MS) {
    return res.status(401).send('Timestamp out of valid threshold');
  }

  const sourceString = req.method + requestUrl + req.rawBody + timestampHeader;
  const hash = crypto
    .createHmac('sha256', clientSecret)
    .update(sourceString)
    .digest('base64');

  if (crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(signatureHeader))) {
    return next();
  }

  return res.status(401).send('Invalid HubSpot Webhook Signature');
}

app.use(express.json({
  verify: (req, res, buf) => { req.rawBody = buf.toString(); }
}));

app.post('/webhooks/hubspot', verifyHubSpotSignature, (req, res) => {
  const events = req.body;
  
  for (const event of events) {
    console.log(`[HUB_EVENT] Subscription Type: ${event.subscriptionType}, Object ID: ${event.objectId}`);
    // Process CRM events asynchronously
  }

  res.status(200).send('OK');
});

app.listen(4000, () => console.log('HubSpot Webhook Service running on port 4000'));
```
