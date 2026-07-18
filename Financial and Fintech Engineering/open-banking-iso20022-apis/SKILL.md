---
name: open-banking-iso20022-apis
description: Architect enterprise Open Banking platforms, PSD2/PSD3 compliant APIs, financial message modeling in ISO 20022 (pacs.008, camt.053, pain.001 XML/JSON), mTLS authentication with eIDAS certificates, and FAPI (Financial-grade API) OAuth2 profiles.
---

# Open Banking & ISO 20022 APIs Architecture

This skill package defines architectural guidelines, security controls, and production implementations for building **Open Banking platforms**, **PSD2/PSD3 compliant Payment Initiation (PISP) and Account Information (AISP) services**, and **ISO 20022 financial messaging engines**.

---

## 1. Security Architecture & Standards

### FAPI (Financial-grade API 1.0/2.0) & OAuth 2.0 Security Profile
- **Client Authentication**: Enforce Mutual TLS (`tls_client_auth`) or `private_key_jwt` with asymmetric RSA-SHA256 (PS256) or ECDSA (ES256) key pairs.
- **Pushed Authorization Requests (PAR - RFC 9126)**: PISPs/AISPs must push authorization request parameters directly to the ASPSP authorization server via back-channel POST requests, obtaining an opaque `request_uri` to prevent front-channel tampering.
- **JWS Signature & Non-Repudiation**: Payment initiation payloads must include detached HTTP Message Signatures (RFC 9421) signed with **eIDAS QSealC (Qualified Electronic Seal Certificates)**.

### mTLS & eIDAS Certificate Validation
- **Transport Security**: Enforce mutual TLS 1.3 using **eIDAS QWAC (Qualified Website Authentication Certificates)** to establish identity between Third-Party Providers (TPPs) and Account Servicing Payment Service Providers (ASPSPs).
- **Certificate Revocation Checking**: Validate TPP certificate status in real-time via OCSP stapling and CRL (Certificate Revocation List) checks against Qualified Trust Service Providers (QTSPs).

---

## 2. ISO 20022 Financial Messaging Matrix

| Message Identifier | Name | Domain | Primary Purpose |
| :--- | :--- | :--- | :--- |
| **`pain.001.001.11`** | Customer Credit Transfer Initiation | Payments | TPP/Corporate initiates credit transfer to bank |
| **`pacs.008.001.10`** | FI to FI Customer Credit Transfer | Clearing & Settlement | Interbank real-time settlement (SEPA Instant, FedNow) |
| **`camt.053.001.10`** | Bank to Customer Statement | Account Management | Daily end-of-day account balance & statement |
| **`camt.054.001.10`** | Bank to Customer Debit/Credit Notification | Notifications | Real-time transaction notification advisory |
| **`pacs.002.001.12`** | Payment Status Report | Status Tracking | Real-time ACK/NACK status of payment processing |

---

## 3. Production Code Implementations

### Python Implementation: ISO 20022 `pain.001` XML Builder & Schema Validator

```python
import datetime
import hashlib
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, Any

class ISO20022Pain001Builder:
    """
    Constructs ISO 20022 pain.001.001.11 Credit Transfer Initiation XML documents
    """
    NS_PAIN = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.11"

    def __init__(self, msg_id: str, initiating_party_name: str):
        self.msg_id = msg_id
        self.initiating_party_name = initiating_party_name

    def build_credit_transfer_xml(self, pmt_inf_id: str, debtor: Dict[str, str], creditor: Dict[str, str], amount: float, currency: str) -> str:
        ET.register_namespace('', self.NS_PAIN)
        doc = ET.Element("Document", xmlns=self.NS_PAIN)
        cstmr_pmt_init = ET.SubElement(doc, "CstmrPmtSttmtReq")

        # Group Header
        grp_hdr = ET.SubElement(cstmr_pmt_init, "GrpHdr")
        ET.SubElement(grp_hdr, "MsgId").text = self.msg_id
        ET.SubElement(grp_hdr, "CreDtTm").text = datetime.datetime.utcnow().isoformat() + "Z"
        ET.SubElement(grp_hdr, "NbOfTxs").text = "1"
        ET.SubElement(grp_hdr, "CtrlSum").text = f"{amount:.2f}"
        
        initg_pty = ET.SubElement(grp_hdr, "InitgPty")
        ET.SubElement(initg_pty, "Nm").text = self.initiating_party_name

        # Payment Information
        pmt_inf = ET.SubElement(cstmr_pmt_init, "PmtInf")
        ET.SubElement(pmt_inf, "PmtInfId").text = pmt_inf_id
        ET.SubElement(pmt_inf, "PmtMtd").text = "TRF"
        ET.SubElement(pmt_inf, "NbOfTxs").text = "1"
        ET.SubElement(pmt_inf, "CtrlSum").text = f"{amount:.2f}"

        # Debtor Info
        dbtr = ET.SubElement(pmt_inf, "Dbtr")
        ET.SubElement(dbtr, "Nm").text = debtor["name"]
        dbtr_acct = ET.SubElement(pmt_inf, "DbtrAcct")
        dbtr_id = ET.SubElement(dbtr_acct, "Id")
        ET.SubElement(dbtr_id, "IBAN").text = debtor["iban"]

        dbtr_agt = ET.SubElement(pmt_inf, "DbtrAgt")
        fin_inst_dbtr = ET.SubElement(dbtr_agt, "FinInstnId")
        ET.SubElement(fin_inst_dbtr, "BICFI").text = debtor["bic"]

        # Credit Transfer Transaction Information
        cdt_trf_tx_inf = ET.SubElement(pmt_inf, "CdtTrfTxInf")
        pmt_id = ET.SubElement(cdt_trf_tx_inf, "PmtId")
        ET.SubElement(pmt_id, "EndToEndId").text = f"E2E-{pmt_inf_id}"

        amt = ET.SubElement(cdt_trf_tx_inf, "Amt")
        instd_amt = ET.SubElement(amt, "InstdAmt", Ccy=currency)
        instd_amt.text = f"{amount:.2f}"

        cdtr_agt = ET.SubElement(cdt_trf_tx_inf, "CdtrAgt")
        fin_inst_cdtr = ET.SubElement(cdtr_agt, "FinInstnId")
        ET.SubElement(fin_inst_cdtr, "BICFI").text = creditor["bic"]

        cdtr = ET.SubElement(cdt_trf_tx_inf, "Cdtr")
        ET.SubElement(cdtr, "Nm").text = creditor["name"]

        cdtr_acct = ET.SubElement(cdt_trf_tx_inf, "CdtrAcct")
        cdtr_id = ET.SubElement(cdtr_acct, "Id")
        ET.SubElement(cdtr_id, "IBAN").text = creditor["iban"]

        raw_xml = ET.tostring(doc, encoding="utf-8")
        parsed = minidom.parseString(raw_xml)
        return parsed.toprettyxml(indent="  ")

    def compute_sha256_digest(self, xml_content: str) -> str:
        """Computes SHA-256 digest for eIDAS JWS HTTP Digest Header"""
        digest = hashlib.sha256(xml_content.encode("utf-8")).digest()
        import base64
        return f"SHA-256={base64.b64encode(digest).decode('utf-8')}"
```

---

### TypeScript Implementation: FAPI 1.0 Advanced Client with Private Key JWT & Signature Interceptor

```typescript
import crypto from 'crypto';
import fs from 'fs';

export interface FapiClientConfig {
  clientId: string;
  tokenEndpoint: string;
  privateKeyPath: string;
  keyId: string;
}

export class FapiAdvancedAuthClient {
  private config: FapiClientConfig;
  private privateKeyPem: string;

  constructor(config: FapiClientConfig) {
    this.config = config;
    this.privateKeyPem = fs.readFileSync(config.privateKeyPath, 'utf8');
  }

  /**
   * Generates a signed Client Assertion JWT for private_key_jwt authentication (RFC 7523)
   */
  public generateClientAssertion(): string {
    const now = Math.floor(Date.now() / 1000);
    const header = {
      alg: 'PS256',
      typ: 'JWT',
      kid: this.config.keyId,
    };

    const payload = {
      iss: this.config.clientId,
      sub: this.config.clientId,
      aud: this.config.tokenEndpoint,
      jti: crypto.randomUUID(),
      exp: now + 300,
      iat: now,
    };

    const encodedHeader = this.base64UrlEncode(JSON.stringify(header));
    const encodedPayload = this.base64UrlEncode(JSON.stringify(payload));
    const dataToSign = `${encodedHeader}.${encodedPayload}`;

    const signer = crypto.createSign('RSA-SHA256');
    signer.update(dataToSign);
    signer.end();

    const signature = signer.sign({
      key: this.privateKeyPem,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST,
    });

    return `${dataToSign}.${this.base64UrlEncode(signature)}`;
  }

  /**
   * Sign Open Banking HTTP Request with RFC 9421 HTTP Message Signatures (eIDAS QSealC)
   */
  public createSignedHttpHeaders(httpMethod: string, requestPath: string, bodyPayload: string): Record<string, string> {
    const digest = 'SHA-256=' + crypto.createHash('sha256').update(bodyPayload).digest('base64');
    const xFapiInteractionId = crypto.randomUUID();
    const dateHeader = new Date().toUTCString();

    const signatureInputStr = `"(request-target)": ${httpMethod.toLowerCase()} ${requestPath}\n"host": api.bank.com\n"date": ${dateHeader}\n"digest": ${digest}\n"x-fapi-interaction-id": ${xFapiInteractionId}`;

    const signer = crypto.createSign('RSA-SHA256');
    signer.update(signatureInputStr);
    const signature = signer.sign(this.privateKeyPem, 'base64');

    return {
      'Digest': digest,
      'Date': dateHeader,
      'x-fapi-interaction-id': xFapiInteractionId,
      'Signature': `keyId="${this.config.keyId}",algorithm="rsa-sha256",headers="(request-target) host date digest x-fapi-interaction-id",signature="${signature}"`,
    };
  }

  private base64UrlEncode(input: string | Buffer): string {
    const buf = typeof input === 'string' ? Buffer.from(input) : input;
    return buf.toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
  }
}
```

---

## 4. Anti-Patterns & Critical Mistakes

1. **Failure to Perform XML Schema (XSD) Validation Prior to Parsing**
   - *Impact*: Vulnerability to XML External Entity (XXE) injection attacks and unexpected XML expansion attacks (Billion Laughs).
   - *Remediation*: Disable external DTD resolution (`resolve_entities=False`) and validate all incoming ISO 20022 XML against official ISO XSD schemas before business processing.

2. **Passing Dynamic Auth Parameters via Front-Channel Authorize Endpoint**
   - *Impact*: Vulnerable to Authorization Code injection and parameter tampering.
   - *Remediation*: Require FAPI Pushed Authorization Requests (PAR) to exchange parameters back-channel for an opaque `request_uri`.

3. **Treating IBAN Validation as a Simple Regex Match**
   - *Impact*: False positives and failed SEPA payments due to missing MOD-97 check digit calculations.
   - *Remediation*: Always execute MOD-97 checksum algorithm verification on IBAN strings prior to generating `pain.001` or `pacs.008` messages.

4. **Omitting `x-fapi-interaction-id` Tracing Headers**
   - *Impact*: Non-compliance with Open Banking auditing mandates, leading to untraceable dispute handling between TPP and ASPSP.
   - *Remediation*: Inject and log unique UUID v4 `x-fapi-interaction-id` headers across all HTTP client requests and server logs.

---

## 5. Verification & Testing Playbook

- **ISO 20022 XSD Validation CLI**:
  ```bash
  xmllint --schema pain.001.001.11.xsd payment_initiation.xml --noout
  ```
- **Open Banking Conformance Suite**: Run official OIDF (OpenID Foundation) FAPI 1.0 Advanced test suite against the OAuth 2.0 authorization server.
- **eIDAS QSealC Signature Verification**: Verify detached HTTP signatures using OpenSSL and public QSealC certificate chains.
