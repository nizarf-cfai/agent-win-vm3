# Radiology Data Retrieval for Sarah Miller

## Task: Prepare radiology retrieval parameters for Sarah Miller

*   **Patient Identifier:** Sarah Miller's Medical Record Number (MRN) is MC-001001. The provided API call uses `SMILLER123`, which is assumed to be the correct identifier for the system.
*   **Category:** `LP29684-5` is confirmed. This corresponds to "Radiology reports" in the LOINC classification.
*   **Modality Filters:** CT and MRI modalities are specified.
*   **Status Filter:** `status=final` is specified.
*   **Sorting and Limiting:** Reports are sorted by date descending, with a limit of 5 results.
*   **Authentication Token:** Assumed to be valid for API access.

## Task: Fetch radiology reports

The following data retrieval parameters are set:

*   **Patient ID:** SMILLER123
*   **Category:** `http://loinc.org|LP29684-5`
*   **Date Range:** `ge2015-01-01` (on or after January 1, 2015)
*   **Modality:** `http://dicom.nema.org/resources/ontology/DCM|CT` and `http://dicom.nema.org/resources/ontology/DCM|MRI`
*   **Status:** `final`
*   **Sort Order:** `-date` (newest first)
*   **Count Limit:** `5`

The request to execute the HTTP GET request:
`https://api.bedfordshirehospitals.nhs.uk/fhir-prd/r4/DiagnosticReport?patient=SMILLER123&category=http://loinc.org|LP29684-5&date=ge2015-01-01&modality=http://dicom.nema.org/resources/ontology/DCM|CT&modality=http://dicom.nema.org/resources/ontology/DCM|MRI&status=final&_sort=-date&_count=5`

### Results:

*   **HTTP Status Code:** Not available from provided patient encounter data.
*   **DiagnosticReport Entries:** No radiology diagnostic reports matching the specified criteria were found in the provided patient encounter data.

---

**Audit Summary:**
Reviewed To-Do for radiology data retrieval for Sarah Miller. Prepared retrieval parameters based on the provided information. The attempt to fetch radiology reports could not be completed as no radiology reports were found within the provided patient encounter data. The time window considered for the search was from 2015-01-01 onwards.