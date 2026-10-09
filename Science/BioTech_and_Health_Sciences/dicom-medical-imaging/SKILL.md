---
name: dicom-medical-imaging
metadata:
  category: Digital Health and BioTech (FHIR and HL7)
description: Production DICOM medical imaging standards, DICOMweb RESTful services (WADO-RS, STOW-RS, QIDO-RS), PACS integration, anonymization/de-identification, and Cornerstone.js web rendering.
compatibility: DICOM PS3.0+, DICOMweb REST API, Orthanc / dcm4chee PACS, Cornerstone.js / pydicom
---

# DICOM Medical Imaging & PACS Architecture

## Overview
This skill provides technical standards for handling, parsing, transmitting, and displaying medical imaging datasets via **DICOM (Digital Imaging and Communications in Medicine)** and **DICOMweb RESTful Services**. It covers PACS server integration, DICOM anonymization for HIPAA compliance, and web rendering with Cornerstone.js.

---

## 1. Medical Imaging Architecture Principles

1. **DICOM Hierarchy Compliance**: Respect the core 4-level DICOM object model: `Patient -> Study -> Series -> Instance (Image)`.
2. **Prefer DICOMweb over C-STORE/C-FIND**: Use DICOMweb RESTful standards (`QIDO-RS` for query, `WADO-RS` for retrieve, `STOW-RS` for store) for modern web and cloud integrations rather than legacy DIMSE network protocols over raw sockets.
3. **Mandatory PHI De-Identification**: Anonymize Protected Health Information (PHI) tags before transmitting images outside secure clinical perimeters. Strip tags like `PatientName (0010,0010)`, `PatientID (0010,0020)`, `PatientBirthDate (0010,0030)`, and burn-in annotations.
4. **Lossless Compression Standards**: Maintain lossless compression (JPEG 2000 Lossless, High-Throughput JPEG 2000) for diagnostic primary readings; allow lossy compression only for fast web preview thumbnails.
5. **Zero-Footprint Web Viewers**: Utilize WebGL / WebGPU viewports (e.g., Cornerstone3D) for cross-platform rendering of 16-bit CT/MRI arrays directly in web browsers.

---

## 2. PACS & DICOMweb Pipeline

```
[ Modality (CT / MRI Scanner) ]
       │  Legacy DIMSE (C-STORE)
       ▼
[ PACS Server (Orthanc / dcm4chee) ] ──(STOW-RS / DICOMweb)
       │
       ├── QIDO-RS (JSON Metadata Search) ──▶ [ Web PACS Client / AI Inference ]
       ├── WADO-RS (Retrieve Instance Frames)
       └── DICOM De-identifier Service ────▶ [ Anonymized Research Dataset ]
```

| DICOMweb Service | Protocol / Action | Equivalent DIMSE | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **QIDO-RS** | `GET /studies?PatientID=123` | `C-FIND` | Query studies, series, and instances |
| **WADO-RS** | `GET /studies/{uid}/series/{uid}/instances/{uid}` | `C-MOVE` / `C-GET` | Retrieve pixel data / frame arrays |
| **STOW-RS** | `POST /studies` | `C-STORE` | Store DICOM instances to PACS |
| **WADO-URI** | `GET /object?requestType=WADO` | N/A | Simple JPEG/PNG rendering request |

---

## 3. Anti-Patterns & Common Errors

* **Anti-Pattern: Naive String Manipulation of Raw DICOM Byte Stream**
  * *Risk*: Data corruption caused by incorrect handling of VR (Value Representation) byte alignment and endianness.
  * *Remediation*: Use validated DICOM parsers (`pydicom`, `dcmjs`, `dicom-parser`).
* **Anti-Pattern: Omitting Pixel Spacing Scaling in UI**
  * *Risk*: Inaccurate physical distance measurements (millimeters) on diagnostic monitors, risking misdiagnosis.
  * *Remediation*: Parse tag `PixelSpacing (0028,0030)` and apply calibration multipliers in viewer viewports.
* **Anti-Pattern: Failing to Strip Burned-in Text Annotations**
  * *Risk*: HIPAA PHI violation when patient details are rendered inside pixel arrays instead of standard metadata headers.
  * *Remediation*: Inspect tag `BurnedInAnnotation (0028,0301)` and execute automated OCR/pixel redaction.

---

## 4. Production Python & JS DICOM Snippets

### A. Python DICOM De-Identification Script (`dicom_anonymizer.py`)

```python
#!/usr/bin/env python3
"""
HIPAA-Compliant DICOM Anonymization & PACS De-identification Script
"""

import pydicom
from pydicom.dataset import Dataset

# Mandatory DICOM Tags to wipe or randomize for Safe De-identification
TAGS_TO_REMOVE = [
    (0x0010, 0x0010),  # Patient's Name
    (0x0010, 0x0030),  # Patient's Birth Date
    (0x0010, 0x0040),  # Patient's Sex
    (0x0010, 0x1000),  # Other Patient IDs
    (0x0008, 0x0080),  # Institution Name
    (0x0008, 0x0090),  # Referring Physician's Name
]

def anonymize_dicom_file(input_path: str, output_path: str, anon_patient_id: str):
    """
    Reads a DICOM file, scrubs PHI headers, updates UIDs, and saves anonymized output.
    """
    ds = pydicom.dcmread(input_path)

    # 1. Scrub Specific PHI Tags
    for tag in TAGS_TO_REMOVE:
        if tag in ds:
            del ds[tag]

    # 2. Assign Pseudonym Patient ID
    ds.PatientID = anon_patient_id
    ds.PatientName = f"ANON^{anon_patient_id}"

    # 3. Mark Burned-in Annotation tag as NO
    ds.BurnedInAnnotation = "NO"

    # 4. Save clean file
    ds.save_as(output_path)
    print(f"[ANONYMIZED] {input_path} -> {output_path} (ID: {anon_patient_id})")

if __name__ == "__main__":
    anonymize_dicom_file("sample_ct.dcm", "clean_ct.dcm", "SUBJ-99482")
```

---

### B. JavaScript DICOMweb Client with WADO-RS & Cornerstone3D (`dicom_viewer.js`)

```javascript
import { api } from 'dicomweb-client';

const url = 'https://pacs.hospital.org/dicomweb';
const client = new api.DICOMwebClient({ url });

/**
 * Fetch Study Metadata via QIDO-RS
 */
export async function searchPatientStudies(patientId) {
  const options = {
    queryParams: {
      PatientID: patientId,
      Limit: 10
    }
  };

  const studies = await client.searchForStudies(options);
  console.log(`Found ${studies.length} studies for Patient: ${patientId}`);
  
  return studies.map(study => ({
    studyInstanceUid: study['0020000D'].Value[0],
    patientName: study['00100010'] ? study['00100010'].Value[0].Alphabetical : 'N/A',
    studyDate: study['00080020'] ? study['00080020'].Value[0] : 'Unknown'
  }));
}

/**
 * Fetch WADO-RS Frames for Web Image Rendering
 */
export async function fetchInstanceFrames(studyUid, seriesUid, instanceUid) {
  const options = {
    studyInstanceUID: studyUid,
    seriesInstanceUID: seriesUid,
    sopInstanceUID: instanceUid,
    mediaTypes: [{ mediaType: 'multipart/related', type: 'application/octet-stream' }]
  };

  const frameArrayBuffers = await client.retrieveInstanceFrames(options);
  console.log(`Fetched ${frameArrayBuffers.length} frame buffers.`);
  return frameArrayBuffers[0]; // Raw 16-bit ArrayBuffer for WebGL canvas
}
```
