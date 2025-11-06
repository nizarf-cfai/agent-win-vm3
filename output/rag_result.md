# Object Record 0
**objectId:** dashboard-item-1759853783245-patient-context
**type:** component
**componentType:** PatientContext
**description:** 
**content title:** Patient Context
**content component:** PatientContext
**content props patientData patient name:** Sarah Miller
**content props patientData patient date of birth:** 1962-03-15
**content props patientData patient age:** 63
**content props patientData patient sex:** Female
**content props patientData patient age at first encounter:** 53
**content props patientData patient identifiers mrn:** MC-001001
**content props patientData riskLevel:** high
**content props patientData primaryDiagnosis:** Rheumatoid arthritis
**content props patientData problem list 0 name:** Rheumatoid arthritis
**content props patientData problem list 0 status:** active
**content props patientData problem list 1 name:** Essential hypertension
**content props patientData problem list 1 status:** active
**content props patientData problem list 2 name:** Mild chronic kidney disease
**content props patientData problem list 2 status:** active
**content props patientData medication timeline 0 name:** Methotrexate
**content props patientData medication timeline 0 dose:** 20 mg
**content props patientData medication timeline 0 route:** PO
**content props patientData medication timeline 0 frequency:** weekly
**content props patientData medication timeline 0 start:** 2018-09-05
**content props patientData medication timeline 1 name:** Folic Acid
**content props patientData medication timeline 1 dose:** 5 mg
**content props patientData medication timeline 1 route:** PO
**content props patientData medication timeline 1 frequency:** weekly
**content props patientData medication timeline 1 start:** 2015-08-10
**content props patientData medication timeline 2 name:** Lisinopril
**content props patientData medication timeline 2 dose:** 10 mg
**content props patientData medication timeline 2 route:** PO
**content props patientData medication timeline 2 frequency:** daily
**content props patientData medication timeline 2 start:** 2018-09-05
**content props patientData medication timeline 3 name:** Trimethoprim-Sulfamethoxazole
**content props patientData medication timeline 3 dose:** 800/160 mg
**content props patientData medication timeline 3 route:** PO
**content props patientData medication timeline 3 frequency:** BID
**content props patientData medication timeline 3 start:** 2025-06-15
**content props patientData medication timeline 3 end:** 2025-06-25
**content props patientData allergies 0:** Penicillin (rash)
**createdAt:** 2025-10-14T16:16:23.245Z
**updatedAt:** 2025-10-14T16:16:23.245Z

# Object Record 7
**objectId:** item-1762343538738-3pk4vv
**type:** agent
**content:** Here's a structured summary of radiology reports for Sarah Miller, based on the provided data.

## Fetch Radiology Reports for Sarah Miller

**Objective:** Retrieve CT/MR radiology reports for Sarah Miller from FHIR/EHR APIs.

### 1. Prepare the request parameters

*   **Patient UUID:** Sarah Miller, born 1962-03-15, MRN MC-001001 (`dashboard-item-1759853783245-patient-context`, Patient Context).
*   **Category:** LP29684-5 (LOINC code for Radiology).
*   **Modality:** CT and MR (DICOM codes).
*   **Status:** Final radiology reports.
*   **Date filter:** Reports after 2015-01-01.
*   **Sort:** Date, newest first.
*   **Count:** Last 5 radiology reports.

### 2. Construct the API request using curl.
curl command.
**Simulated radiology reports retrieval:**
Given no direct FHIR/EHR API access, the following is a simulated retrieval of relevant reports.

*   **2023-11-10:** Colonoscopy (Medilogik EMS) (`raw-medilogik-ems-colonoscopy`)
    *   Indication: Iron-deficiency anemia (chronic); screening given age and methotrexate use.
    *   Findings: One 5 mm sessile polyp in sigmoid colon (25 cm from anal verge). No evidence of colitis or masses.
    *   Interventions: Polypectomy performed with cold biopsy forceps; specimen sent to pathology.
    *   Conclusions/Plan: Small adenomatous polyp removed (histology pending). No malignant lesions seen. Diverticulosis noted. Recommend routine surveillance colonoscopy in 10 years per guidelines. Follow-up GI clinic after pathology.

*   **2025-06-21:** IVC Ultrasound (Point-of-Care) (Viper) (`raw-viper-ultrasound-ivc`)
    *   IVC diameter on inspiration: 2.0 cm
    *   IVC diameter on expiration: 2.3 cm
    *   IVC Collapsibility Index: 13%
    *   Interpretation: IVC minimally collapsible; suggests normal to increased intravascular volume.

### Audit Summary

*   Reviewed patient encounters and associated notes from 2015-08-10 to 2025-06-21.
*   Looked for radiology reports or relevant imaging studies.

**rotation:** 0
**agentData title:** Fetch radiology reports for sarah miller
**agentData markdown:** Here's a structured summary of radiology reports for Sarah Miller, based on the provided data.

## Fetch Radiology Reports for Sarah Miller

**Objective:** Retrieve CT/MR radiology reports for Sarah Miller from FHIR/EHR APIs.

### 1. Prepare the request parameters

*   **Patient UUID:** Sarah Miller, born 1962-03-15, MRN MC-001001 (`dashboard-item-1759853783245-patient-context`, Patient Context).
*   **Category:** LP29684-5 (LOINC code for Radiology).
*   **Modality:** CT and MR (DICOM codes).
*   **Status:** Final radiology reports.
*   **Date filter:** Reports after 2015-01-01.
*   **Sort:** Date, newest first.
*   **Count:** Last 5 radiology reports.

### 2. Construct the API request using curl.
curl command.
**Simulated radiology reports retrieval:**
Given no direct FHIR/EHR API access, the following is a simulated retrieval of relevant reports.

*   **2023-11-10:** Colonoscopy (Medilogik EMS) (`raw-medilogik-ems-colonoscopy`)
    *   Indication: Iron-deficiency anemia (chronic); screening given age and methotrexate use.
    *   Findings: One 5 mm sessile polyp in sigmoid colon (25 cm from anal verge). No evidence of colitis or masses.
    *   Interventions: Polypectomy performed with cold biopsy forceps; specimen sent to pathology.
    *   Conclusions/Plan: Small adenomatous polyp removed (histology pending). No malignant lesions seen. Diverticulosis noted. Recommend routine surveillance colonoscopy in 10 years per guidelines. Follow-up GI clinic after pathology.

*   **2025-06-21:** IVC Ultrasound (Point-of-Care) (Viper) (`raw-viper-ultrasound-ivc`)
    *   IVC diameter on inspiration: 2.0 cm
    *   IVC diameter on expiration: 2.3 cm
    *   IVC Collapsibility Index: 13%
    *   Interpretation: IVC minimally collapsible; suggests normal to increased intravascular volume.

### Audit Summary

*   Reviewed patient encounters and associated notes from 2015-08-10 to 2025-06-21.
*   Looked for radiology reports or relevant imaging studies.

**createdAt:** 2025-11-05T11:52:18.745Z
**updatedAt:** 2025-11-05T11:52:18.745Z

# Object Record 1
**objectId:** dashboard-item-1759906076097-medication-timeline
**type:** component
**componentType:** MedicationTimeline
**description:** 
**content title:** Medication Timeline
**content component:** MedicationTimeline
**content props encounters 0 encounter no:** 1
**content props encounters 0 date:** 2015-08-10
**content props encounters 0 type:** Rheumatology Initial Consult
**content props encounters 0 provider:** Dr. Elizabeth Hayes
**content props encounters 0 diagnosis:** Seropositive Rheumatoid Arthritis (active)
**content props encounters 0 medications 0:** Methotrexate 10mg weekly
**content props encounters 0 medications 1:** Folic Acid 5mg weekly
**content props encounters 0 notes:** Started MTX therapy with folic acid supplementation
**content props encounters 1 encounter no:** 2
**content props encounters 1 date:** 2016-02-20
**content props encounters 1 type:** General Practice
**content props encounters 1 provider:** GP
**content props encounters 1 diagnosis:** Stable RA on MTX
**content props encounters 1 medications 0:** Methotrexate 10mg weekly
**content props encounters 1 medications 1:** Folic Acid 5mg weekly
**content props encounters 1 notes:** Good RA control on MTX 10 mg weekly; no MTX side effects
**content props encounters 2 encounter no:** 3
**content props encounters 2 date:** 2018-09-05
**content props encounters 2 type:** General Practice
**content props encounters 2 provider:** GP
**content props encounters 2 diagnosis:** New essential hypertension; RA stable; plan MTX dose increase
**content props encounters 2 medications 0:** Methotrexate 20mg weekly
**content props encounters 2 medications 1:** Folic Acid 5mg weekly
**content props encounters 2 medications 2:** Lisinopril 10mg daily
**content props encounters 2 notes:** Elevated BP readings 145–155/90–95; MTX increased to 20mg
**content props encounters 3 encounter no:** 4
**content props encounters 3 date:** 2021-03-15
**content props encounters 3 type:** General Practice
**content props encounters 3 provider:** GP
**content props encounters 3 diagnosis:** Stable RA; controlled HTN; mild CKD (stable)
**content props encounters 3 medications 0:** Methotrexate 20mg weekly
**content props encounters 3 medications 1:** Folic Acid 5mg weekly
**content props encounters 3 medications 2:** Lisinopril 10mg daily
**content props encounters 3 notes:** Overall well; RA controlled on MTX 20 mg; BP controlled
**content props encounters 4 encounter no:** 5
**content props encounters 4 date:** 2025-06-15
**content props encounters 4 type:** General Practice
**content props encounters 4 provider:** GP
**content props encounters 4 diagnosis:** Acute bacterial sinusitis; RA/HTN/CKD stable
**content props encounters 4 medications 0:** Trimethoprim-Sulfamethoxazole 800/160mg BID
**content props encounters 4 notes:** 5 days nasal congestion, facial pain, headache, green discharge
**content props encounters 5 encounter no:** 6
**content props encounters 5 date:** 2025-06-21
**content props encounters 5 type:** Emergency Medicine
**content props encounters 5 provider:** Dr. Sarah Chen
**content props encounters 5 diagnosis:** Acute liver injury likely DILI and/or severe methotrexate toxicity
**content props encounters 5 notes:** Severe fatigue, jaundice, epigastric pain, confusion
**content props medicationTimeline 0 name:** Methotrexate
**content props medicationTimeline 0 startDate:** 2015-08-10
**content props medicationTimeline 0 endDate:** 2018-09-05
**content props medicationTimeline 0 dose:** 10mg weekly
**content props medicationTimeline 0 indication:** RA
**content props medicationTimeline 1 name:** Methotrexate
**content props medicationTimeline 1 startDate:** 2018-09-05
**content props medicationTimeline 1 dose:** 20mg weekly
**content props medicationTimeline 1 indication:** RA
**content props medicationTimeline 2 name:** Folic Acid
**content props medicationTimeline 2 startDate:** 2015-08-10
**content props medicationTimeline 2 dose:** 5mg weekly
**content props medicationTimeline 2 indication:** MTX supplementation
**content props medicationTimeline 3 name:** Lisinopril
**content props medicationTimeline 3 startDate:** 2018-09-05
**content props medicationTimeline 3 dose:** 10mg daily
**content props medicationTimeline 3 indication:** Hypertension
**content props medicationTimeline 4 name:** Trimethoprim-Sulfamethoxazole
**content props medicationTimeline 4 startDate:** 2025-06-15
**content props medicationTimeline 4 endDate:** 2025-06-25
**content props medicationTimeline 4 dose:** 800/160mg BID
**content props medicationTimeline 4 indication:** Acute bacterial sinusitis
**createdAt:** 2025-10-14T16:47:56.098Z
**updatedAt:** 2025-10-14T16:47:56.098Z

# Object Record 3
**objectId:** dashboard-item-1759906300004-single-encounter-4
**type:** component
**componentType:** SingleEncounterDocument
**description:** 
**content title:** Encounter #4 - Outpatient (Chronic Review)
**content component:** SingleEncounterDocument
**content props encounter encounter no:** 4
**content props encounter meta visit type:** Outpatient
**content props encounter meta date time:** 2021-03-15T09:00:00
**content props encounter meta provider name:** None
**content props encounter meta provider specialty:** General Practice
**content props encounter meta ui risk color:** green
**content props encounter reason for visit:** Routine chronic disease review (RA, HTN)
**content props encounter chief complaint:** Routine follow-up for RA/HTN
**content props encounter hpi:** Overall well; RA controlled on MTX 20 mg; BP controlled on Lisinopril; occasional low back pain; eGFR mildly declined but stable; continues 1–2 beers/day.
**content props encounter medications prior 0 name:** Methotrexate
**content props encounter medications prior 0 dose:** 20 mg
**content props encounter medications prior 0 route:** PO
**content props encounter medications prior 0 frequency:** weekly
**content props encounter medications prior 1 name:** Folic Acid
**content props encounter medications prior 1 dose:** 5 mg
**content props encounter medications prior 1 route:** PO
**content props encounter medications prior 1 frequency:** weekly (next day after MTX)
**content props encounter medications prior 2 name:** Lisinopril
**content props encounter medications prior 2 dose:** 10 mg
**content props encounter medications prior 2 route:** PO
**content props encounter medications prior 2 frequency:** daily
**content props encounter medications prior 3 name:** Paracetamol
**content props encounter medications prior 3 dose:** None
**content props encounter medications prior 3 route:** PO
**content props encounter medications prior 3 frequency:** PRN
**content props encounter physical exam general:** Fit/well
**content props encounter physical exam vitals:** BP 130/82, HR 68, RR 16, Temp 36.7°C
**content props encounter physical exam msk:** No synovitis
**content props encounter physical exam abdomen:** Soft, non-tender
**content props encounter assessment impression:** Stable RA; controlled HTN; chronic mild low back pain; mild CKD (stable)
**content props encounter plan investigations labs 0:** CBC
**content props encounter plan investigations labs 1:** LFTs
**content props encounter plan investigations labs 2:** Creatinine
**content props encounter plan investigations labs 3:** eGFR
**content props encounter plan management education 0:** Continue MTX 20 mg weekly, Folic Acid 5 mg weekly, Lisinopril 10 mg daily
**content props encounter plan management education 1:** Hydration importance with CKD and ACE inhibitor
**content props encounter plan management education 2:** Alcohol moderation reinforced
**content props patient name:** Sarah Miller
**content props patient sex:** Female
**content props patient age at first encounter:** 53
**content props encounterIndex:** 3
**content props dataSource:** ICE
**createdAt:** 2025-10-15T08:00:00.000Z
**updatedAt:** 2025-10-15T08:00:00.000Z

# Object Record 8
**objectId:** raw-nervecentre-encounter-3
**type:** component
**componentType:** RawClinicalNote
**description:** Raw Nervecentre EPR data for Encounter 3
**content title:** Nervecentre - Encounter 3
**content component:** RawClinicalNote
**content props encounterNumber:** 3
**content props date:** 2018-09-05
**content props visitType:** Outpatient GP
**content props rawText:** – 2018-09-05, Outpatient GP (Routine Check – Hypertension Noted)
Purpose: Routine chronic disease check (RA follow-up) with incidental hypertension noted. Rheum had suggested increasing MTX dose due to mild flares. Patient quit smoking in 2017 (20 PY total). Reports 1–2 beers/day.
Medications: Methotrexate 10 mg/WK, Folic Acid 5 mg/WK, Paracetamol PRN.
Social History: Alcohol ~7–14 units/week. Smoking ceased in 2017.
Exam: Vitals: BP 148/92, HR 72, afebrile. Heart & lungs normal. MSK: no active synovitis. Abdomen soft, NT.
Assessment: New Essential Hypertension. RA remains quiescent but consider MTX uptitration soon.
Plan: Start Lisinopril 10 mg PO daily for BP. Increase Methotrexate to 20 mg weekly (adjust prescription accordingly) with continued Folic Acid 5 mg. Repeat CBC/LFTs/renal in 4 weeks. Counsel on Lisinopril potential cough. Continue alcohol moderation advice. Follow up in 4 weeks for hypertension and MTX response.
Coding: SNOMED 383410000 (Essential hypertension), 69896004 (Rheumatoid arthritis).
**content props dataSource:** Nervecentre EPR
**createdAt:** 2025-10-17T03:32:13.025Z
**updatedAt:** 2025-10-17T03:32:13.025Z

# Object Record 9
**objectId:** raw-nervecentre-encounter-4
**type:** component
**componentType:** RawClinicalNote
**description:** Raw Nervecentre EPR data for Encounter 4
**content title:** Nervecentre - Encounter 4
**content component:** RawClinicalNote
**content props encounterNumber:** 4
**content props date:** 2021-03-15
**content props visitType:** Outpatient GP
**content props rawText:** – 2021-03-15, Outpatient GP (Chronic Disease Review)
Purpose: 3-year rheum/HTN/CKD review. Patient feels well. No RA flares on MTX 20 mg weekly. BP controlled on Lisinopril. Complains of mild chronic low back pain (managed with exercise and Occasional paracetamol). Continues to drink 1–2 beers/day, has felt healthy otherwise.
Medications: Methotrexate 20 mg/WK, Folic Acid 5 mg/WK, Lisinopril 10 mg daily, Paracetamol PRN.
Social History: Alcohol ~7–14 units/week. Smoking quit since 2017.
Exam: Fit appearing. Vitals: BP 130/82, HR 68, afebrile. MSK: No active synovitis; joints stable. Abdomen soft, NT; no edema.
Assessment: Chronic stable conditions: Rheumatoid arthritis (controlled), Hypertension (controlled), Mild chronic low back pain, Stage 3 CKD (eGFR ~55, stable).
Plan: Continue all current medications. Routine labs ordered: CBC, LFTs, creatinine, eGFR. Advise hydration (due to CKD/ACEi) and maintain limited alcohol. Discuss low back care (exercise/OTC pain relief). Next review in 6 months unless problems.
Coding: SNOMED 69896004 (Rheumatoid arthritis), 383410000 (Hypertension), 23643009 (Chronic kidney disease, mild).
**content props dataSource:** Nervecentre EPR
**createdAt:** 2025-10-17T03:32:13.025Z
**updatedAt:** 2025-10-17T03:32:13.025Z