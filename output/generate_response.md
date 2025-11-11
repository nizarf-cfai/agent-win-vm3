# Radiology Data Retrieval for Sarah Miller

## Task 1: Identify and access the patient's radiology records for Sarah Miller

### Sub-task: Verify patient identity and access permissions
*   Patient Name: Sarah Miller
*   DOB: 1962-03-15 (`dashboard-item-1759853783245-patient-context`)
*   MRN: MC-001001 (`dashboard-item-1759853783245-patient-context`)
*   Access verified based on provided credentials.

### Sub-task: Locate all relevant radiology reports and images
*   **Colonoscopy (2023-11-10):**
    *   Findings: One 5 mm sessile polyp in the sigmoid colon. No evidence of colitis or masses. (`raw-medilogik-ems-colonoscopy`)
    *   Intervention: Polypectomy performed. Specimen sent to pathology. (`raw-medilogik-ems-colonoscopy`)
    *   Conclusion: Small adenomatous polyp removed. Recommend routine surveillance colonoscopy in 10 years. (`raw-medilogik-ems-colonoscopy`)
*   **IVC Ultrasound (2025-06-21):**
    *   Findings: IVC minimally collapsible; suggests normal to increased intravascular volume. IVC diameter on inspiration: 2.0 cm. IVC diameter on expiration: 2.3 cm. IVC Collapsibility Index: 13% (`raw-viper-ultrasound-ivc`)
    *   Clinical Use: Results used to guide fluid management. (`raw-viper-ultrasound-ivc`)
*   **Abdominal Ultrasound (2025-06-21):**
    *   Plan: STAT abdominal ultrasound (liver appearance, biliary) (`raw-nervecentre-encounter-6`)
    *   *Note:* Actual results of the ultrasound are not provided.

## Task 2: Consolidate and prepare the retrieved radiology data

### Sub-task: Organize reports and image metadata
*   All radiology reports and image metadata are organized chronologically.

### Sub-task: Flag any incomplete or missing data
*   **Missing Abdominal Ultrasound Results (2025-06-21):** The plan in encounter 6 includes a STAT abdominal ultrasound, but the actual results/report from this imaging study are not included in the provided data. (`raw-nervecentre-encounter-6`)
*   **Pending Pathology Report:** Pathology report for the colon polyp removed on 2023-11-10 is pending. (`raw-medilogik-ems-colonoscopy`)

**Audit Summary:** Reviewed patient encounters, radiology reports. Time window: 2023-11-10 to 2025-06-21.

**Next Steps:**

*   **Urgent:** Obtain the abdominal ultrasound report from 2025-06-21 to assess liver and biliary appearance. Rationale: Critical for evaluating the acute liver injury.
*   **Routine:** Obtain pathology report from colonoscopy performed on 2023-11-10. Rationale: Standard follow-up for polyp removal.
