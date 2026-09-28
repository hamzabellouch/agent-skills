---
name: einvoicing-zatca-peppol-compliance
metadata:
  category: Accounting Tax and Invoicing Tech
description: Implement government electronic invoicing standards including UBL 2.1 XML, Peppol BIS Billing 3.0, and Saudi ZATCA (FATOORA Phase 2) compliance. Generate cryptographic invoice hashes (SHA-256), ECDSA secp256k1 digital signatures, TLV-encoded Base64 QR codes, and clearance/reporting API integrations. Trigger when building electronic billing systems, VAT compliance engines, or cross-border e-invoicing pipelines.
compatibility: UBL 2.1 OASIS standard, Peppol BIS 3.0, ZATCA Phase 2 specifications
---

# E-Invoicing (ZATCA Phase 2 & Peppol BIS) Compliance Skill Guide

This skill specifies technical standards, cryptographic stamping algorithms, and UBL 2.1 XML schema compliance for statutory e-invoicing systems.

---

## 1. Statutory E-Invoicing Cryptographic Flow

```text
[ Business ERP / Billing System ]
                |
                v
[ UBL 2.1 XML Invoice Generation ]
                |
                +---> Compute Canonical Hash: SHA-256(Canonicalized XML)
                +---> Sign Hash using Private Key: ECDSA (secp256k1)
                +---> Generate TLV-Encoded QR Code (Tag-Length-Value Base64)
                +---> Inject Digital Signature & Certificate into XML Extension
                |
                v
[ Government Tax Authority API (ZATCA Clearance / Peppol Access Point) ]
```

---

## 2. Production Code Implementations

### A. TLV (Tag-Length-Value) QR Code Generator (Python)

For tax authorities like ZATCA, QR codes must be encoded using strict sequential Tag-Length-Value (TLV) byte structures converted to Base64.

```python
import base64


def encode_tlv_field(tag: int, value: str) -> bytes:
    val_bytes = value.encode("utf-8")
    length = len(val_bytes)
    return bytes([tag, length]) + val_bytes


def generate_zatca_qr_code(
    seller_name: str,
    vat_registration_number: str,
    invoice_timestamp_iso: str,
    invoice_total_with_vat: str,
    vat_amount: str,
    invoice_hash_sha256: str = "",
    digital_signature: bytes = b"",
    public_key: bytes = b"",
) -> str:
    """Generates standard Base64-encoded TLV string for Phase 2 Tax Invoices."""
    tlv_bytes = bytearray()

    # Tag 1: Seller Name
    tlv_bytes.extend(encode_tlv_field(1, seller_name))
    # Tag 2: VAT Registration Number (15 digits)
    tlv_bytes.extend(encode_tlv_field(2, vat_registration_number))
    # Tag 3: Time Stamp (ISO 8601: YYYY-MM-DDTHH:MM:SSZ)
    tlv_bytes.extend(encode_tlv_field(3, invoice_timestamp_iso))
    # Tag 4: Invoice Total (with VAT)
    tlv_bytes.extend(encode_tlv_field(4, invoice_total_with_vat))
    # Tag 5: VAT Amount
    tlv_bytes.extend(encode_tlv_field(5, vat_amount))

    # Phase 2 Cryptographic Extensions
    if invoice_hash_sha256:
        tlv_bytes.extend(encode_tlv_field(6, invoice_hash_sha256))
    if digital_signature:
        tlv_bytes.extend(bytes([7, len(digital_signature)]) + digital_signature)
    if public_key:
        tlv_bytes.extend(bytes([8, len(public_key)]) + public_key)

    return base64.b64encode(tlv_bytes).decode("ascii")
```

### B. Standard UBL 2.1 XML Skeleton (Excerpt)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:ProfileID>reporting:1.0</cbc:ProfileID>
    <cbc:ID>INV-2026-00084</cbc:ID>
    <cbc:UUID>c3a81234-e89b-12d3-a456-426614174000</cbc:UUID>
    <cbc:IssueDate>2026-09-28</cbc:IssueDate>
    <cbc:IssueTime>14:32:00</cbc:IssueTime>
    <cbc:InvoiceTypeCode name="0100000">388</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>SAR</cbc:DocumentCurrencyCode>
    
    <!-- Previous Invoice Hash for Blockchain-Style Tamper-Proof Chain -->
    <cac:AdditionalDocumentReference>
        <cbc:ID>PIH</cbc:ID>
        <cac:Attachment>
            <cac:EmbeddedDocumentBinaryObject mimeCode="text/plain">
                NWZlYjM4OGY...==
            </cac:EmbeddedDocumentBinaryObject>
        </cac:Attachment>
    </cac:AdditionalDocumentReference>

    <!-- Supplier & Customer Information -->
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>310123456700003</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
</Invoice>
```

---

## 3. Compliance Checklist

- [ ] **Previous Invoice Hash (PIH):** Ensure every sequential invoice cryptographically links to the previous invoice's SHA-256 hash to satisfy tamper-evident audit chaining.
- [ ] **Canonicalization (C14N11):** Prior to hashing and signing, canonicalize XML strictly according to W3C C14N to remove whitespace discrepancies.
- [ ] **Cryptographic Key Storage:** Store private signing keys in a Hardware Security Module (HSM) or secure cloud vault (AWS KMS, Azure Key Vault, HashiCorp Vault).
