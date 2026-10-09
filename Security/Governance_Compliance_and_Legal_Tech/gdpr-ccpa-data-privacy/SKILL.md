---
name: gdpr-ccpa-data-privacy
metadata:
  category: Compliance Governance and Legal Tech
description: Engineering patterns for GDPR, CCPA/CPRA, and global data privacy compliance. Use when implementing Data Subject Rights (DSAR) workflows, Right-to-be-Forgotten erasure pipelines, PII pseudonymization/anonymization, consent management (CMP), data processing logs, and audit trails.
compatibility: Generic Backend (Node.js/Python/Go), PostgreSQL/MongoDB, Redis, AWS/GCP
---

# GDPR, CCPA & Data Privacy Engineering Guidelines

This skill provides data architecture, encryption standards, PII pseudonymization patterns, consent state tracking, and automated Data Subject Access Request (DSAR) / Right-to-be-Forgotten deletion pipelines for privacy compliance under GDPR and CCPA/CPRA.

---

## 1. Data Privacy Architecture Framework

```
                          +-------------------------------+
                          |    User / Consent Front-End   |
                          |  (Cookie Banner / CMP Widget) |
                          +---------------+---------------+
                                          |
                                   Consent Telemetry
                                          v
+------------------+      +-------------------------------+
|  DSAR Request    | ---> | Privacy API & Orchestration   |
| (Export/Erasure) |      | (Tokenization & Workflow)     |
+------------------+      +---------------+---------------+
                                          |
                   +----------------------+----------------------+
                   |                      |                      |
          +--------v-------+     +--------v-------+     +--------v-------+
          | DB Crypt Key   |     | SQL/NoSQL DB   |     | Log Scrubbing  |
          | Manager (KMS)  |     |  Pseudonymized |     | Analytics Off  |
          +----------------+     +----------------+     +----------------+
```

1. **Lawful Basis & Consent Tracking**: Every data collection event must record explicit user consent timestamp, consent version, and specific purpose scope.
2. **Right to Access (DSAR)**: Users can export all personal data stored across databases in structured machine-readable format (JSON/CSV).
3. **Right to Erasure (Right to be Forgotten)**: Cascading deletion or cryptographic erasure of personal identifiable information (PII) within 30 statutory days.
4. **Data Minimization & Pseudonymization**: PII (emails, phone numbers, IP addresses) stored using salt-hashed tokens or envelope encryption.

---

## 2. PII Pseudonymization & Cryptographic Erasure (Python / SQLAlchemy)

Cryptographic Erasure (Crypto-Shredding) destroys the per-user cryptographic key, rendering encrypted PII irrecoverably unreadable without physically deleting relational transactional metrics.

```python
import base64
import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import Column, String, Integer, DateTime, LargeBinary, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CryptoShredder:
    """Manages per-user AES-GCM encryption key generation & destruction."""
    
    @staticmethod
    def generate_user_key() -> bytes:
        return AESGCM.generate_key(bit_length=256)

    @staticmethod
    def encrypt_pii(plaintext_data: str, user_key: bytes) -> str:
        aesgcm = AESGCM(user_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext_data.encode('utf-8'), None)
        # Combine nonce + ciphertext base64 encoded
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    @staticmethod
    def decrypt_pii(encrypted_payload: str, user_key: bytes) -> str:
        data = base64.b64decode(encrypted_payload.encode('utf-8'))
        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(user_key)
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_bytes.decode('utf-8')

class UserAccount(Base):
    __tablename__ = 'user_accounts'

    id = Column(Integer, primary_key=True)
    user_uuid = Column(String(36), unique=True, nullable=False, index=True)
    
    # Store pseudonymized lookup hash (for querying without revealing raw email)
    email_lookup_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    # Encrypted PII Fields
    encrypted_email = Column(Text, nullable=False)
    encrypted_full_name = Column(Text, nullable=False)
    
    @staticmethod
    def hash_pii_for_lookup(pii_value: str, global_salt: str) -> str:
        return hashlib.sha256((pii_value.lower().strip() + global_salt).encode('utf-8')).hexdigest()
```

---

## 3. DSAR Automated Deletion Workflow (Node.js / Express)

```javascript
const express = require('express');
const router = express.Router();

/**
 * Executes cascading Data Subject Deletion / Anonymization
 */
router.post('/privacy/dsar/erase', async (req, res) => {
  const { userId, requestVerificationToken } = req.body;

  // 1. Verify User Authorization & Identity
  if (!verifyDsarToken(userId, requestVerificationToken)) {
    return res.status(401).json({ error: 'Invalid or expired DSAR verification token' });
  }

  try {
    // 2. Begin Compliance Erasure Transaction
    await db.transaction(async (trx) => {
      // Step A: Destroy User Cryptographic Encryption Key in KMS (Crypto-shredding)
      await kmsKeyStore.deleteUserKey(userId, { transaction: trx });

      // Step B: Anonymize or Soft Delete User Record in Primary DB
      await trx('users')
        .where({ id: userId })
        .update({
          email: `erased_user_${userId}@privacy-deleted.local`,
          full_name: 'ANONYMIZED_DATA_SUBJECT',
          phone_number: null,
          status: 'DELETED_GDPR_DSAR',
          deleted_at: new Date()
        });

      // Step C: Scrub PII from Support Tickets / Comments
      await trx('comments')
        .where({ author_id: userId })
        .update({ author_ip: '0.0.0.0', author_name: 'Anonymous User' });

      // Step D: Write immutable compliance audit log
      await trx('privacy_audit_logs').insert({
        event_type: 'GDPR_RIGHT_TO_ERASURE_EXECUTED',
        user_id_hash: hashUserId(userId),
        executed_at: new Date(),
        status: 'SUCCESS'
      });
    });

    return res.status(200).json({
      status: 'SUCCESS',
      message: 'User personal data has been erased and pseudonymized successfully.'
    });
  } catch (error) {
    console.error('DSAR Erasure Failed:', error);
    return res.status(500).json({ error: 'Internal failure during DSAR erasure processing' });
  }
});

module.exports = router;
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Plaintext PII in application log files | Critical | GDPR fine up to 4% global turnover / $20M | Mask emails (`j***e@domain.com`), IP addresses, and tokens in loggers |
| Soft deleting rows while keeping PII in backup DBs | High | Non-compliance during privacy audit | Crypto-shred user KMS key so historical backups remain unreadable |
| Missing Opt-Out mechanisms for CCPA ("Do Not Sell") | High | CCPA/CPRA enforcement penalties | Provide explicit API endpoint & frontend button for data sharing opt-out |
| Storing user consent in local un-audited state | Medium | Unable to demonstrate legal compliance proof | Persist immutable consent log (`user_id`, `version`, `timestamp`, `ip`) |
| Broad wildcard SELECT queries returning PII to telemetry | Medium | Unintentional PII leakage to third-party analytics | Explicitly exclude PII columns in reporting queries |

---

## 5. Privacy Compliance Verification Checklist

- [ ] **Data Mapping Inventory**: Maintain updated Data Flow Diagram (DFD) and Record of Processing Activities (ROPA).
- [ ] **Consent CMP Integration**: Confirm cookie categories (Necessary, Analytics, Marketing) block tags before user opt-in.
- [ ] **Log Scrubbing Validation**: Grep production logs for email regex patterns to verify zero plaintext PII leaks.
- [ ] **DSAR SLA Monitoring**: Automated alerts ensuring all access/erasure requests complete within **30 days**.
