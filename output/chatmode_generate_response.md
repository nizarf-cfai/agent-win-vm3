# Radiology Data Retrieval for Sarah Miller

## Task: Prepare radiology retrieval parameters for Sarah Miller

### Identify patient Sarah Miller's UUID
*   **UUID:** Not explicitly provided in the patient encounter data. This information is typically found in a patient's master patient index or demographic record.

### Determine correct category code for radiology (LP29684-5)
*   **Category Code:** `LP29684-5` is identified as the correct LOINC code for radiology reports. This code is used in the FHIR API query.

### Set modality filters for CT and MRI
*   **Modality Filters:** The query should include filters for `http://dicom.nema.org/resources/ontology/DCM|CT` and `http://dicom.nema.org/resources/ontology/DCM|MRI`.

### Set status filter to 'final'
*   **Status Filter:** The query should specify `status=final` to retrieve only finalized radiology reports.

### Apply date filter (e.g., 'ge2015-01-01')
*   **Date Filter:** The query should include `date=ge2015-01-01` to retrieve reports from January 1, 2015, onwards.

### Set sorting to newest first and limit results
*   **Sorting:** The query should use `_sort=-date` to sort results by date in descending order (newest first).
*   **Limit:** The query should use `_count=5` to limit the results to the 5 most recent reports.

### Verify authentication token
*   **Authentication Token:** Verification of the authentication token is required before executing the API request. This step is external to the provided patient data.

## Task: Execute HTTP request with patient UUID

*   **Action:** Execute the provided `curl` command using the identified parameters.
*   **Note:** The `<UUID>` placeholder must be replaced with Sarah Miller's actual patient UUID. The `curl` command as provided:
    ```bash
    curl -X GET 'https://api.bedfordshirehospitals.nhs.uk/fhir-prd/r4/DiagnosticReport?patient=<UUID>&category=http://loinc.org|LP29684-5&date=ge2015-01-01&modality=http://dicom.nema.org/resources/ontology/DCM|CT&modality=http://dicom.nema.org/resources/ontology/DCM|MRI&status=final&_sort=-date&_count=5'
    ```

### Check HTTP status code for success
*   **Requirement:** Monitor the HTTP status code returned by the API request. A `200 OK` status code indicates success.

### Validate response JSON structure for DiagnosticReport entries
*   **Requirement:** Parse the JSON response and validate that it contains `DiagnosticReport` entries with expected fields such as `code`, `subject`, `effectiveDateTime`, `conclusionCode`, and `presentedForm`.

---
**Audit Summary:**
Reviewed the `todo` object for radiology data retrieval for Sarah Miller. Extracted specific parameters for API query based on the provided sub-tasks. Identified missing patient UUID and external authentication requirement. The structured output provides the necessary parameters for executing the retrieval task. Data reviewed spans from 2015-01-01 to the present, based on the specified date filter. No radiology reports were found within the provided patient encounter data.