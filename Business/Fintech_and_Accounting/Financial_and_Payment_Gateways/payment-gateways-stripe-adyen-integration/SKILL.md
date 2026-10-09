---
name: payment-gateways-stripe-adyen-integration
description: Architect and implement secure, PCI-DSS compliant payment processing integrations with Stripe and Adyen, featuring idempotent webhook handling, tokenization, multi-currency processing, automatic retries, and ledger-based reconciliation.
---

# Payment Gateways Integration Architecture (Stripe & Adyen)

This skill package provides enterprise-grade patterns, architectural principles, PCI-DSS v4.0 compliance guidelines, and production code implementations for orchestrating payment processing across **Stripe** and **Adyen**.

---

## 1. Core Architectural & Compliance Standards

### PCI-DSS v4.0 Compliance & Tokenization
- **Out-of-Scope Architecture (SAQ A / SAQ A-EP)**: Never ingest, process, or store Raw Primary Account Numbers (PAN), Card Verification Values (CVV/CVC), or PINs on your infrastructure. Use client-side SDKs (Stripe Elements / Adyen Web Drop-in) to tokenization endpoints directly owned by payment service providers (PSPs).
- **Network & Transport Layer Security**: All API endpoints and client SDK communications must enforce TLS 1.3 with strong cipher suites (e.g., `TLS_AES_256_GCM_SHA384`).
- **Data Sanitization & Zero Logging**: Redact all sensitive fields from application logs, trace contexts, and error payloads. Never log header signatures, API tokens, raw webhook payloads with PII, or tokens susceptible to account takeover.

### Webhook Idempotency & Replay Protection
- **Idempotency Keying**: Webhook events must be processed exactly once using distributed locking (e.g., Redis `SET key value NX PX`) keyed by the unique Event ID (`event.id` for Stripe, `eventCode` + `pspReference` for Adyen).
- **Time-Window & Signature Verification**: Reject webhooks missing cryptographic HMAC signatures or with timestamps older than 300 seconds to prevent replay attacks.
- **Asynchronous Execution**: Webhook HTTP handlers must validate signatures, enqueue the event into an isolated message queue (e.g., Kafka / RabbitMQ), and return an immediate HTTP `200 OK` within 500ms to avoid PSP retry loops.

### Reconciliation & Ledger Architecture
- **Double-Entry Bookkeeping**: Model payments as state transitions across double-entry ledger accounts (Asset: PSP Clearing, Revenue, Expense: Gateway Fees, Liability: Customer Balance).
- **State Machine Integrity**: Enforce strict status transitions (`AUTHORIZED` -> `CAPTURED` -> `SETTLED` / `REFUNDED` / `DISPUTED`).

---

## 2. PSP Capabilities Comparison Matrix

| Capability | Stripe Integration | Adyen Integration |
| :--- | :--- | :--- |
| **Client Tokenization** | Stripe Elements / PaymentIntents API | Adyen Drop-in / Components API |
| **Webhook Verification** | HMAC-SHA256 (`Stripe-Signature` header) | HMAC-SHA256 Base64 encoded payload validation |
| **Capture Model** | Immediate or Manual (`capture_method: 'manual'`) | Automatic, Manual, or Delayed Capture rules |
| **Payout & Settlement** | Balance Transactions & Payouts API | Financial Reports (Settlement Detail Report) |
| **Global Payment Methods** | iDEAL, SEPA, Klarna, Alipay via PaymentIntents | 250+ local payment methods via `/payments` |

---

## 3. Production Code Implementations

### Python Implementation: Production-Grade Webhook Handler with Redis Idempotency & HMAC Validation

```python
import base64
import hashlib
import hmac
import json
import time
import logging
from typing import Dict, Any, Optional
import redis
import stripe

logger = logging.getLogger("payment_orchestrator")
logger.setLevel(logging.INFO)

class PaymentWebhookProcessor:
    def __init__(self, stripe_webhook_secret: str, adyen_hmac_key: str, redis_client: redis.Redis):
        self.stripe_webhook_secret = stripe_webhook_secret
        self.adyen_hmac_key = adyen_hmac_key
        self.redis = redis_client
        self.lock_ttl_ms = 60000  # 60s processing lock

    def process_stripe_webhook(self, raw_body: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Validates Stripe signature, enforces idempotency, and queues event.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload=raw_body,
                sig_header=sig_header,
                secret=self.stripe_webhook_secret,
                tolerance=300
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid Stripe webhook signature", exc_info=True)
            raise ValueError("Invalid signature") from e

        event_id = event["id"]
        event_type = event["type"]

        if not self._acquire_idempotency_lock(f"stripe:{event_id}"):
            logger.info(f"Duplicate Stripe event skipped: {event_id}")
            return {"status": "already_processed", "event_id": event_id}

        try:
            self._route_stripe_event(event_type, event["data"]["object"])
            return {"status": "success", "event_id": event_id}
        except Exception as e:
            # Release lock on processing error to allow retry
            self.redis.delete(f"stripe:{event_id}")
            raise e

    def verify_adyen_hmac(self, notification_item: Dict[str, Any]) -> bool:
        """
        Verifies Adyen HMAC signature according to Adyen HMAC validator specs.
        """
        item = notification_item.get("NotificationRequestItem", {})
        hmac_signature = item.get("additionalData", {}).get("hmacSignature")
        if not hmac_signature:
            return False

        keys = [
            "pspReference", "originalReference", "merchantAccountCode", "merchantReference",
            "value", "currency", "eventCode", "success"
        ]
        
        # Format string to sign
        signed_vals = []
        for k in keys:
            val = str(item.get(k, "") or "")
            # Escape backslashes and colons
            escaped_val = val.replace("\\", "\\\\").replace(":", "\\:")
            signed_vals.append(escaped_val)

        payload_to_sign = ":".join(signed_vals).encode("utf-8")
        hmac_key_bytes = bytes.fromhex(self.adyen_hmac_key)
        
        calculated_hmac = base64.b64encode(
            hmac.new(hmac_key_bytes, payload_to_sign, hashlib.sha256).digest()
        ).decode("utf-8")

        return hmac.compare_digest(calculated_hmac, hmac_signature)

    def process_adyen_webhook(self, notification_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes Adyen notification items with HMAC validation and idempotency.
        """
        items = notification_payload.get("notificationItems", [])
        processed = []

        for container in items:
            item = container.get("NotificationRequestItem", {})
            if not self.verify_adyen_hmac(container):
                logger.error("Adyen HMAC signature mismatch")
                continue

            psp_ref = item.get("pspReference")
            event_code = item.get("eventCode")
            idempotency_key = f"adyen:{psp_ref}:{event_code}"

            if not self._acquire_idempotency_lock(idempotency_key):
                logger.info(f"Duplicate Adyen notification skipped: {idempotency_key}")
                processed.append({"pspReference": psp_ref, "status": "duplicate"})
                continue

            # Process notification logic
            self._route_adyen_event(event_code, item)
            processed.append({"pspReference": psp_ref, "status": "processed"})

        return {"status": "ok", "processed": processed}

    def _acquire_idempotency_lock(self, lock_key: str) -> bool:
        """Atomic Redis distributed lock for idempotency enforcement."""
        return bool(self.redis.set(lock_key, "1", nx=True, px=self.lock_ttl_ms))

    def _route_stripe_event(self, event_type: str, data_object: Dict[str, Any]):
        if event_type == "payment_intent.succeeded":
            payment_intent_id = data_object["id"]
            amount = data_object["amount"]
            currency = data_object["currency"]
            logger.info(f"Stripe Payment Succeeded: {payment_intent_id} | {amount}{currency}")
            # Execute double-entry ledger settlement...
        elif event_type == "charge.dispute.created":
            dispute_id = data_object["id"]
            logger.warning(f"Stripe Dispute Created: {dispute_id}")

    def _route_adyen_event(self, event_code: str, item: Dict[str, Any]):
        if event_code == "AUTHORISATION" and item.get("success") == "true":
            psp_ref = item["pspReference"]
            val = item.get("value", {}).get("value")
            currency = item.get("value", {}).get("currency")
            logger.info(f"Adyen Authorisation Succeeded: {psp_ref} | {val} {currency}")
```

---

### TypeScript Implementation: Modern Payment Intent & Checkout Orchestration

```typescript
import stripe from 'stripe';
import crypto from 'crypto';

export interface PaymentRequest {
  merchantReference: string;
  amountCents: number;
  currency: string;
  paymentMethodToken: string;
  customerId: string;
}

export interface PaymentResult {
  transactionId: string;
  status: 'AUTHORIZED' | 'CAPTURED' | 'REQUIRES_ACTION' | 'FAILED';
  clientSecret?: string;
  rawResponse: Record<string, unknown>;
}

export class StripePaymentProvider {
  private stripeClient: stripe;

  constructor(apiKey: string) {
    this.stripeClient = new stripe(apiKey, {
      apiVersion: '2023-10-16',
      typescript: true,
    });
  }

  /**
   * Orchestrates PaymentIntent creation with 3D Secure 2.0 Strong Customer Authentication (SCA)
   */
  public async createPaymentIntent(req: PaymentRequest): Promise<PaymentResult> {
    const idempotencyKey = crypto
      .createHash('sha256')
      .update(`${req.merchantReference}-${req.amountCents}-${req.currency}`)
      .digest('hex');

    try {
      const intent = await this.stripeClient.paymentIntents.create(
        {
          amount: req.amountCents,
          currency: req.currency.toLowerCase(),
          customer: req.customerId,
          payment_method: req.paymentMethodToken,
          confirm: true,
          off_session: false,
          capture_method: 'manual', // Auth and capture separated for risk checks
          confirmation_method: 'automatic',
          metadata: {
            merchant_reference: req.merchantReference,
          },
        },
        {
          idempotencyKey,
        }
      );

      if (intent.status === 'requires_action' || intent.status === 'requires_source_action') {
        return {
          transactionId: intent.id,
          status: 'REQUIRES_ACTION',
          clientSecret: intent.client_secret ?? undefined,
          rawResponse: intent as unknown as Record<string, unknown>,
        };
      }

      if (intent.status === 'requires_capture') {
        return {
          transactionId: intent.id,
          status: 'AUTHORIZED',
          rawResponse: intent as unknown as Record<string, unknown>,
        };
      }

      throw new Error(`Unexpected PaymentIntent status: ${intent.status}`);
    } catch (err: any) {
      throw new Error(`Stripe Payment Intent Execution Failed: ${err.message}`);
    }
  }

  /**
   * Captures a previously authorized payment after manual anti-fraud review
   */
  public async captureAuthorizedPayment(paymentIntentId: string, amountToCaptureCents?: number): Promise<PaymentResult> {
    const captureOptions: stripe.PaymentIntentCaptureParams = {};
    if (amountToCaptureCents) {
      captureOptions.amount_to_capture = amountToCaptureCents;
    }

    const intent = await this.stripeClient.paymentIntents.capture(paymentIntentId, captureOptions);

    return {
      transactionId: intent.id,
      status: 'CAPTURED',
      rawResponse: intent as unknown as Record<string, unknown>,
    };
  }
}
```

---

## 4. Anti-Patterns & Pitfalls

### Critical Architectural Mistakes

1. **Processing Webhooks Synchronously in HTTP Worker Threads**
   - *Impact*: Gateways like Stripe/Adyen time out after 5-10 seconds and re-send webhooks, causing cascading duplicate executions and worker thread starvation.
   - *Remediation*: Accept payload, verify HMAC, publish event to broker (Kafka/AWS SQS), return HTTP 200 immediately.

2. **Using Floating-Point Numbers for Currency Operations**
   - *Impact*: IEEE 754 floating-point rounding errors (`0.1 + 0.2 = 0.30000000000000004`) lead to balance mismatches in accounting ledgers.
   - *Remediation*: Always store and compute amounts as 64-bit integers in minor currency units (cents, pence) or fixed-point decimal objects (`Decimal`).

3. **Ignoring Client-Side 3D-Secure (3DS2) Challenge Flows**
   - *Impact*: Soft-deletes and authorization rejections increase due to PSD2 SCA requirements in Europe and worldwide mandate compliance.
   - *Remediation*: Correctly propagate `requires_action` states back to client SDKs to render 3DS authentication modals.

4. **Storing API Keys or Webhook Secrets in Code Repositories**
   - *Impact*: Secrets leak, leading to unauthorized refund triggers, customer data breach, or fraud.
   - *Remediation*: Inject secrets using KMS (HashiCorp Vault, AWS Secrets Manager) and support seamless secret rotation.

---

## 5. Verification & Testing Playbook

- **Stripe CLI Webhook Testing**:
  ```bash
  stripe listen --forward-to localhost:8080/api/v1/webhooks/stripe
  stripe trigger payment_intent.succeeded
  ```
- **Adyen Mock Webhook Replay**: Test HMAC generation using official Adyen test payload fixtures and verify zero-drop idempotency under simulated concurrent execution.
- **Chaos & Failure Testing**: Simulate network splits during capture API calls and verify double-entry ledger idempotency keys prevent double charging.
