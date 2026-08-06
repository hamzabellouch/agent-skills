---
name: fhir-hl7-health-data
metadata:
  category: Digital Health and BioTech (FHIR and HL7)
description: Production-grade FHIR R4/R5 data modeling, HL7 v2 message parsing, SMART on FHIR authorization, HIPAA-compliant patient record exchange, and HAPI FHIR integration.
compatibility: FHIR R4 / R5, HL7 v2.x, SMART on FHIR (OAuth2 + OpenID Connect), HAPI FHIR / Node.js @medplum/core
---

# FHIR R4/R5 & HL7 v2 Health Data Integration

## Overview
This skill provides standards for digital health interoperability using **HL7 FHIR (Fast Healthcare Interoperability Resources) R4/R5** and legacy **HL7 v2.x** messaging. It covers FHIR JSON resources (`Patient`, `Observation`, `Encounter`, `Condition`), SMART on FHIR OAuth2 scoping, HL7 v2 MLLP framing/parsing, and HIPAA-compliant data security.

---

## 1. Healthcare Data Interoperability Principles

1. **FHIR Spec Compliance**: Stick strictly to standard FHIR R4/R5 resource schemas. Use extensions (`Extension`) only when necessary and register custom profiles via `StructureDefinition`.
2. **SMART on FHIR Security**: Enforce fine-grained OAuth2 scopes (`patient/Patient.read`, `user/Observation.write`, `launch/patient`). Enforce OpenID Connect for practitioner identity verification.
3. **HL7 v2 to FHIR Mapping**: Convert incoming legacy HL7 v2 pipeline messages (ADT, ORU, MDM) into standard FHIR bundles (`Bundle` of type `transaction` or `batch`) for modern storage.
4. **Idempotent Resource Mutations**: Use conditional updates (`PUT /Patient?identifier=system|value`) to prevent duplicating patient records across EHR sync pipelines.
5. **HIPAA & PHI Security**: Encrypt all Protected Health Information (PHI) in transit (TLS 1.3) and at rest (AES-256). Audit access via FHIR `AuditEvent` resources.

---

## 2. Health Data Pipeline Architecture

```
[ Legacy EHR System ] ──(HL7 v2 ADT/ORU over MLLP)
                                 │
                                 ▼
[ Interoperability Engine ] ──(HL7 v2 Parser & FHIR Converter)
                                 │
                                 │ FHIR Transaction Bundle (HTTPS / SMART on FHIR)
                                 ▼
[ HAPI FHIR / Medplum Server ] ◀──(OAuth2 Bearer Token)── [ Patient Portal / Mobile App ]
```

| FHIR Resource | Primary Medical Data | Key Search Parameters |
| :--- | :--- | :--- |
| `Patient` | Demographics, Identifiers, Contact Info | `_id`, `identifier`, `name`, `birthdate` |
| `Observation` | Lab Results, Vital Signs, Social History | `patient`, `category`, `code` (LOINC), `date` |
| `Condition` | Diagnoses, Problems, Medical History | `patient`, `clinical-status`, `code` (SNOMED CT) |
| `Encounter` | Inpatient/Outpatient visits, Stays | `patient`, `status`, `class`, `date` |
| `Bundle` | Container for multiple resources | `type=transaction`, `type=searchset` |

---

## 3. Anti-Patterns & Common Errors

* **Anti-Pattern: Storing Medical Concepts as Free-Text**
  * *Risk*: Inability to execute automated clinical decision support or analytics across health networks.
  * *Remediation*: Bind code fields to standard medical terminologies (LOINC for labs, SNOMED CT for diagnoses, RxNorm for medications, RxNorm/ICD-10-CM).
* **Anti-Pattern: Over-Privileged SMART Scopes (`user/*.*`)**
  * *Risk*: Massive PHI data breach on token theft.
  * *Remediation*: Restrict scopes to least privilege (`patient/Observation.read`).
* **Anti-Pattern: Direct Custom SQL Queries on EHR Databases**
  * *Risk*: Database corruption and breaking EHR software updates.
  * *Remediation*: Interact exclusively through authenticated FHIR APIs or HL7 v2 message brokers.

---

## 4. Production TypeScript / Node.js FHIR Snippets

### A. TypeScript FHIR R4 Bundle Builder & Client (`fhir_client.ts`)

```typescript
import { MedplumClient } from '@medplum/core';
import { Patient, Observation, Bundle } from '@medplum/fhirtypes';

export class HealthDataSyncService {
  private client: MedplumClient;

  constructor(baseUrl: string, accessToken: string) {
    this.client = new MedplumClient({
      baseUrl,
      accessToken,
    });
  }

  /**
   * Idempotent patient registration and Vital Signs observation bundle ingest
   */
  async recordPatientVitalSign(
    mrn: string,
    familyName: string,
    givenName: string,
    birthDate: string,
    heartRateBpm: number
  ): Promise<Observation> {
    // 1. Construct Patient Resource
    const patientResource: Patient = {
      resourceType: 'Patient',
      identifier: [
        {
          system: 'http://hospital.enterprise.org/mrn',
          value: mrn,
        },
      ],
      name: [
        {
          use: 'official',
          family: familyName,
          given: [givenName],
        },
      ],
      gender: 'unknown',
      birthDate: birthDate,
    };

    // 2. Upsert Patient via Conditional PUT
    const patient = await this.client.upsertResource(patientResource, {
      identifier: `http://hospital.enterprise.org/mrn|${mrn}`,
    });

    // 3. Construct Observation Resource bound to LOINC & SNOMED CT
    const observationResource: Observation = {
      resourceType: 'Observation',
      status: 'final',
      category: [
        {
          coding: [
            {
              system: 'http://terminology.hl7.org/CodeSystem/observation-category',
              code: 'vital-signs',
              display: 'Vital Signs',
            },
          ],
        },
      ],
      code: {
        coding: [
          {
            system: 'http://loinc.org',
            code: '8867-4',
            display: 'Heart rate',
          },
        ],
        text: 'Heart Rate',
      },
      subject: {
        reference: `Patient/${patient.id}`,
      },
      effectiveDateTime: new Date().toISOString(),
      valueQuantity: {
        value: heartRateBpm,
        unit: 'beats/min',
        system: 'http://unitsofmeasure.org',
        code: '/min',
      },
    };

    return await this.client.createResource<Observation>(observationResource);
  }
}
```

---

### B. Legacy HL7 v2 Message Parsing & Conversion (`hl7_parser.js`)

```javascript
/**
 * HL7 v2 ORU^R01 (Observation Result) Segment Parser
 */
export function parseHl7v2OruMessage(hl7RawText) {
  const segments = hl7RawText.split('\r').map(line => line.split('|'));
  
  let mshSegment = null;
  let pidSegment = null;
  const observations = [];

  for (const seg of segments) {
    const type = seg[0];
    if (type === 'MSH') mshSegment = seg;
    if (type === 'PID') pidSegment = seg;
    if (type === 'OBX') {
      observations.push({
        valueType: seg[2],
        loincCode: seg[3] ? seg[3].split('^')[0] : '',
        loincDisplay: seg[3] ? seg[3].split('^')[1] : '',
        value: seg[5],
        units: seg[6] ? seg[6].split('^')[0] : '',
        resultStatus: seg[11],
      });
    }
  }

  const patientMrn = pidSegment && pidSegment[3] ? pidSegment[3].split('^')[0] : '';
  const patientLastName = pidSegment && pidSegment[5] ? pidSegment[5].split('^')[0] : '';
  const patientFirstName = pidSegment && pidSegment[5] ? pidSegment[5].split('^')[1] : '';

  return {
    mrn: patientMrn,
    patientName: `${patientFirstName} ${patientLastName}`,
    observations,
  };
}
```
