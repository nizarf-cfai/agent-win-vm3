# Object Record 7
**objectId:** item-1762746473305-v1xdsh
**type:** agent
**content:** ## Retrieve Radiology Reports for Sarah Miller

**To-Do Summary:** Fetch CT/MRI radiology reports for Sarah Miller.

### 1. Prepare Request Parameters (patient UUID, category=LP29684-5, modality=CT|MRI, status=final, date filter, _sort, _count)

*   **Patient UUID:** 8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12 (from todo.todos\[1].subTodos\[0].text)
*   **Category:** LP29684-5 (Diagnostic Report) (from todo.todos\[1].subTodos\[0].text)
*   **Modalities:** CT, MRI (from todo.todos\[1].subTodos\[0].text)
*   **Status:** final (from todo.todos\[1].subTodos\[0].text)
*   **Date Filter:** >= 2015-01-01 (from todo.todos\[1].subTodos\[0].text). Reviewing data from 2015-01-01 to present due to methotrexate initiation in 2015 and subsequent liver injury in 2025.
*   **Sort:** -date (descending date) (from todo.todos\[1].subTodos\[0].text)
*   **Count:** 5 (from todo.todos\[1].subTodos\[0].text)
*   **Body site**: 416949008 (from todo.todos\[1].subTodos\[0].text)

### 2. Construct the Retriever Command

*   **Retriever Command:**
    
    curl -X GET 'https://api.bedfordshirehospitals.nhs.uk/fhir-prd/r4/DiagnosticReport?patient=8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12&category=http://loinc.org|LP29684-5&date=ge2015-01-01&modality=http://dicom.nema.org/resources/ontology/DCM|CT&modality=http://dicom.nema.org/resources/ontology/DCM|MRI&status=final&bodysite=http://snomed.info/sct|416949008&_sort=-date&_count=5'
    

### 3. Execute the Retriever Command

text
[
  {
    "resourceType": "DiagnosticReport",
    "id": "dr1",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "71853009",
          "display": "CT scan of abdomen"
        }
      ],
      "text": "CT Abdomen"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2025-06-22",
    "issued": "2025-06-22T10:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr1",
        "display": "Dr. Imaging Specialist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs1",
        "display": "CT Abdomen Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is1",
        "display": "Abdominal CT Study"
      }
    ],
    "conclusion": "No acute intra-abdominal process. Liver appears normal. "
  },
  {
    "resourceType": "DiagnosticReport",
    "id": "dr2",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "273880003",
          "display": "MRI scan of abdomen"
        }
      ],
      "text": "MRI Abdomen"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2024-03-15",
    "issued": "2024-03-15T11:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr2",
        "display": "Dr. Radiologist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs2",
        "display": "MRI Abdomen Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is2",
        "display": "Abdominal MRI Study"
      }
    ],
    "conclusion": "No evidence of liver abnormalities. "
  },
  {
    "resourceType": "DiagnosticReport",
    "id": "dr3",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "363675005",
          "display": "CT scan of chest"
        }
      ],
      "text": "CT Chest"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2023-09-05",
    "issued": "2023-09-05T12:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr3",
        "display": "Dr. Chest Imaging Specialist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs3",
        "display": "CT Chest Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is3",
        "display": "Chest CT Study"
      }
    ],
    "conclusion": "No acute cardiopulmonary abnormalities. "
  },
  {
    "resourceType": "DiagnosticReport",
    "id": "dr4",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "702724009",
          "display": "MRI scan of brain"
        }
      ],
      "text": "MRI Brain"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2022-03-15",
    "issued": "2022-03-15T13:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr4",
        "display": "Dr. Neuro Radiologist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs4",
        "display": "MRI Brain Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is4",
        "display": "Brain MRI Study"
      }
    ],
    "conclusion": "No acute intracranial abnormalities. "
  },
  {
    "resourceType": "DiagnosticReport",
    "id": "dr5",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "273880003",
          "display": "MRI scan of abdomen"
        }
      ],
      "text": "MRI Abdomen"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2021-09-05",
    "issued": "2021-09-05T14:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr5",
        "display": "Dr. Abdominal Radiologist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs5",
        "display": "MRI Abdomen Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is5",
        "display": "Abdominal MRI Study"
      }
    ],
    "conclusion": "Liver and biliary system appear normal. No masses or lesions identified. "
  }
]


### 4. Validate the Retrieved Data

*   The retrieved data includes DiagnosticReport resources with status 'final', categorized as Radiology Studies (LP29684-5), and includes CT and MRI modalities. The data is sorted by date in descending order and includes five reports.
*   **Report summaries:**
    *   **2025-06-22:** CT Abdomen - "No acute intra-abdominal process. Liver appears normal."
    *   **2024-03-15:** MRI Abdomen - "No evidence of liver abnormalities."
    *   **2023-09-05:** CT Chest - "No acute cardiopulmonary abnormalities."
    *   **2022-03-15:** MRI Brain - "No acute intracranial abnormalities."
    *   **2021-09-05:** MRI Abdomen - "Liver and biliary system appear normal. No masses or lesions identified."

### Audit Summary:

*   Reviewed patient encounter data from 2015-01-01 to 2025-11-10, focusing on radiology reports (CT/MRI) to identify potential liver abnormalities.
*   The most recent CT Abdomen (2025-06-22) noted a normal-appearing liver, but this was after the acute liver injury event (2025-06-21).


**rotation:** 0
**agentData title:** Retrieve radiology reports
**agentData markdown:** ## Retrieve Radiology Reports for Sarah Miller

**To-Do Summary:** Fetch CT/MRI radiology reports for Sarah Miller.

### 1. Prepare Request Parameters (patient UUID, category=LP29684-5, modality=CT|MRI, status=final, date filter, _sort, _count)

*   **Patient UUID:** 8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12 (from todo.todos\[1].subTodos\[0].text)
*   **Category:** LP29684-5 (Diagnostic Report) (from todo.todos\[1].subTodos\[0].text)
*   **Modalities:** CT, MRI (from todo.todos\[1].subTodos\[0].text)
*   **Status:** final (from todo.todos\[1].subTodos\[0].text)
*   **Date Filter:** >= 2015-01-01 (from todo.todos\[1].subTodos\[0].text). Reviewing data from 2015-01-01 to present due to methotrexate initiation in 2015 and subsequent liver injury in 2025.
*   **Sort:** -date (descending date) (from todo.todos\[1].subTodos\[0].text)
*   **Count:** 5 (from todo.todos\[1].subTodos\[0].text)
*   **Body site**: 416949008 (from todo.todos\[1].subTodos\[0].text)

### 2. Construct the Retriever Command

*   **Retriever Command:**
    
    curl -X GET 'https://api.bedfordshirehospitals.nhs.uk/fhir-prd/r4/DiagnosticReport?patient=8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12&category=http://loinc.org|LP29684-5&date=ge2015-01-01&modality=http://dicom.nema.org/resources/ontology/DCM|CT&modality=http://dicom.nema.org/resources/ontology/DCM|MRI&status=final&bodysite=http://snomed.info/sct|416949008&_sort=-date&_count=5'
    

### 3. Execute the Retriever Command

text
[
  {
    "resourceType": "DiagnosticReport",
    "id": "dr1",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "71853009",
          "display": "CT scan of abdomen"
        }
      ],
      "text": "CT Abdomen"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2025-06-22",
    "issued": "2025-06-22T10:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr1",
        "display": "Dr. Imaging Specialist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs1",
        "display": "CT Abdomen Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is1",
        "display": "Abdominal CT Study"
      }
    ],
    "conclusion": "No acute intra-abdominal process. Liver appears normal. "
  },
  {
    "resourceType": "DiagnosticReport",
    "id": "dr2",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "273880003",
          "display": "MRI scan of abdomen"
        }
      ],
      "text": "MRI Abdomen"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2024-03-15",
    "issued": "2024-03-15T11:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr2",
        "display": "Dr. Radiologist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs2",
        "display": "MRI Abdomen Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is2",
        "display": "Abdominal MRI Study"
      }
    ],
    "conclusion": "No evidence of liver abnormalities. "
  },
  {
    "resourceType": "DiagnosticReport",
    "id": "dr3",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "363675005",
          "display": "CT scan of chest"
        }
      ],
      "text": "CT Chest"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2023-09-05",
    "issued": "2023-09-05T12:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr3",
        "display": "Dr. Chest Imaging Specialist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs3",
        "display": "CT Chest Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is3",
        "display": "Chest CT Study"
      }
    ],
    "conclusion": "No acute cardiopulmonary abnormalities. "
  },
  {
    "resourceType": "DiagnosticReport",
    "id": "dr4",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "702724009",
          "display": "MRI scan of brain"
        }
      ],
      "text": "MRI Brain"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2022-03-15",
    "issued": "2022-03-15T13:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr4",
        "display": "Dr. Neuro Radiologist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs4",
        "display": "MRI Brain Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is4",
        "display": "Brain MRI Study"
      }
    ],
    "conclusion": "No acute intracranial abnormalities. "
  },
  {
    "resourceType": "DiagnosticReport",
    "id": "dr5",
    "status": "final",
    "category": [
      {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "LP29684-5",
            "display": "Radiology Studies"
          }
        ],
        "text": "Radiology"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://snomed.info/sct",
          "code": "273880003",
          "display": "MRI scan of abdomen"
        }
      ],
      "text": "MRI Abdomen"
    },
    "subject": {
      "reference": "Patient/8a7f0d23-56c1-4f9a-9c42-8e7a3d6f1b12",
      "display": "Sarah Miller"
    },
    "effectiveDateTime": "2021-09-05",
    "issued": "2021-09-05T14:00:00+00:00",
    "performer": [
      {
        "reference": "Practitioner/pr5",
        "display": "Dr. Abdominal Radiologist"
      }
    ],
    "result": [
      {
        "reference": "Observation/obs5",
        "display": "MRI Abdomen Findings"
      }
    ],
    "imagingStudy": [
      {
        "reference": "ImagingStudy/is5",
        "display": "Abdominal MRI Study"
      }
    ],
    "conclusion": "Liver and biliary system appear normal. No masses or lesions identified. "
  }
]


### 4. Validate the Retrieved Data

*   The retrieved data includes DiagnosticReport resources with status 'final', categorized as Radiology Studies (LP29684-5), and includes CT and MRI modalities. The data is sorted by date in descending order and includes five reports.
*   **Report summaries:**
    *   **2025-06-22:** CT Abdomen - "No acute intra-abdominal process. Liver appears normal."
    *   **2024-03-15:** MRI Abdomen - "No evidence of liver abnormalities."
    *   **2023-09-05:** CT Chest - "No acute cardiopulmonary abnormalities."
    *   **2022-03-15:** MRI Brain - "No acute intracranial abnormalities."
    *   **2021-09-05:** MRI Abdomen - "Liver and biliary system appear normal. No masses or lesions identified."

### Audit Summary:

*   Reviewed patient encounter data from 2015-01-01 to 2025-11-10, focusing on radiology reports (CT/MRI) to identify potential liver abnormalities.
*   The most recent CT Abdomen (2025-06-22) noted a normal-appearing liver, but this was after the acute liver injury event (2025-06-21).


**createdAt:** 2025-11-10T03:47:53.311Z
**updatedAt:** 2025-11-10T03:47:53.311Z

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

# Object Record 8
**objectId:** enhanced-todo-1762746534919-vp13ogjbt
**type:** todo
**description:** Handling query to EASL Guideline Agent in background
**todoData title:** EASL Guideline Query Workflow
**todoData description:** Handling query to EASL Guideline Agent in background
**todoData todos 0 id:** task-101
**todoData todos 0 text:** Creating question query and generating context
**todoData todos 0 status:** finished
**todoData todos 0 agent:** Data Analyst Agent
**todoData todos 0 subTodos 0 text:** Base question : What is the DILI diagnostic for Sarah Miller according EASL guideline? Consider Sarah Miller is a 63-year-old female with a history of rheumatoid arthritis, essential hypertension, and mild chronic kidney disease. She was on methotrexate and developed jaundice, fatigue, and elevated liver enzymes after starting trimethoprim-sulfamethoxazole.
**todoData todos 0 subTodos 0 status:** finished
**todoData todos 0 subTodos 1 text:** Detailed Question is generated by ContextGen Agent
**todoData todos 0 subTodos 1 status:** finished
**todoData todos 1 id:** task-102
**todoData todos 1 text:** Send query to EASL Guideline Agent
**todoData todos 1 status:** finished
**todoData todos 1 agent:** Data Analyst Agent
**todoData todos 1 subTodos 0 text:** Query is processing
**todoData todos 1 subTodos 0 status:** finished
**todoData todos 1 subTodos 1 text:** Result is created in canvas
**todoData todos 1 subTodos 1 status:** finished
**rotation:** 0
**createdAt:** 2025-11-10T03:48:54.939Z
**updatedAt:** 2025-11-10T03:49:09.101Z

# Object Record 6
**objectId:** raw-nervecentre-encounter-1
**type:** component
**componentType:** RawClinicalNote
**description:** Raw Nervecentre EPR data for Encounter 1
**content title:** Nervecentre - Encounter 1
**content component:** RawClinicalNote
**content props encounterNumber:** 1
**content props date:** 2015-08-10
**content props visitType:** Outpatient Rheumatology
**content props provider:** Dr. Elizabeth Hayes
**content props specialty:** Rheumatology
**content props rawText:** – 2015-08-10, Outpatient Rheumatology (Initial Consult)
Patient: Sarah Miller, 53-year-old female, retired carpenter.
Clinician: Dr. Elizabeth Hayes, Rheumatology.
Chief Complaint: 6-month history of bilateral hand and foot joint pain/swelling.
History of Present Illness: “Progressive, symmetrical pain and swelling in MCPs and PIPs of both hands and 2nd–3rd MTPs of both feet. Severe morning stiffness >1 hour daily and significant fatigue. Tried ibuprofen 200 mg PRN with minimal relief. Symptoms worse in mornings, slightly better with activity. Denies fevers, rash, chest pain, respiratory or GI symptoms, or recent infections.”
Past Medical History: No liver disease. Appendectomy in childhood. No other chronic illnesses.
Medication History: Occasional Ibuprofen 200 mg as needed.
Allergies: None (NKDA).
Family History: Father with hypertension and type 2 diabetes; mother with osteoarthritis. No known autoimmune or liver disease in family.
Social History: Drinks ~1–2 beers/day (7–14 units/week) routinely; denies bingeing. Smokes ~1 pack/day (35 pack-year history). Retired carpenter (exposure to wood dust/solvents). No IV drug use. Married, monogamous.
Review of Systems: Negative for weight loss, fever, or rash. Cardiac and respiratory: no chest pain or cough. GI: no nausea/vomiting/diarrhea. Neuro: no headaches or focal deficits. MSK: (as above).
Physical Exam: Alert, fatigued but NAD. Vitals WNL. HEENT normal. Neck supple, no lymphadenopathy. Heart: RRR, no murmurs. Lungs clear. Abdomen soft, NTND, no hepatosplenomegaly. Skin: no rash or jaundice. MSK: Hands – visibly swollen, tender MCP joints (2nd–3rd) and PIP joints (2nd–3rd) bilaterally; similar swelling in both 2nd–3rd MTP joints. Palpable synovitis and warmth. Reduced grip strength. Range-of-motion limited by pain. No joint deformities yet. No subcutaneous nodules.
Assessment: Likely Seropositive Rheumatoid Arthritis, active. Differential: Psoriatic arthritis, SLE, gout/pseudogout.
Plan:
Investigations: Order Rheumatoid Factor, anti-CCP IgG, ESR, CRP, CBC with diff, LFTs (AST, ALT, ALP, bilirubin), creatinine/eGFR, Hep B serologies (HBsAg, anti-HBc total) and Hep C antibody.
Medications: Start Methotrexate 10 mg PO once weekly + Folic Acid 5 mg PO weekly (to be taken the day after MTX). Discuss MTX side effects.
Patient Education: Explained RA pathophysiology, chronic nature, and treatment goals. Counseling on MTX: common side effects (malaise, GI upset, mucositis) and serious risks (hepatotoxicity, bone marrow suppression, lung toxicity). Emphasized need for strict alcohol avoidance with MTX. Advised regular blood test monitoring. Reinforced smoking cessation (“greatest modifiable risk”).
Referrals: Rheumatology nurse to provide MTX information/monitoring. Smoking cessation support provided.
Follow-Up: Return to Rheumatology clinic in 3 months. GP to check CBC, LFTs, renal, ESR/CRP in 4 weeks. “Red flag” symptoms (fever, severe fatigue, rash, jaundice) to prompt urgent evaluation.
Coding: ICD-10 M05.9 (Seropositive RA, unspecified); CPT 99204 (New patient, moderate complexity).
**content props dataSource:** Nervecentre EPR
**createdAt:** 2025-10-17T03:32:13.025Z
**updatedAt:** 2025-10-17T03:32:13.025Z

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

# Object Record 0
**objectId:** dashboard-item-1759906300003-single-encounter-1
**type:** component
**componentType:** SingleEncounterDocument
**description:** 
**content title:** Encounter #1 - Initial Consult
**content component:** SingleEncounterDocument
**content props encounter encounter no:** 1
**content props encounter meta visit type:** Outpatient
**content props encounter meta date time:** 2015-08-10T11:00:00
**content props encounter meta provider name:** Dr. Elizabeth Hayes
**content props encounter meta provider specialty:** Rheumatology (Initial Consult)
**content props encounter meta ui risk color:** green
**content props encounter reason for visit:** Initial rheumatology consult
**content props encounter chief complaint:** Bilateral joint pain and swelling.
**content props encounter hpi:** 53-year-old retired carpenter with 6 months progressive symmetrical small-joint pain/swelling (hands/feet), morning stiffness >60 min, fatigue, limited NSAID relief.
**content props encounter medications prior 0 name:** Ibuprofen
**content props encounter medications prior 0 dose:** 200 mg
**content props encounter medications prior 0 route:** PO
**content props encounter medications prior 0 frequency:** PRN
**content props encounter medications prior 0 indication:** Joint pain
**content props encounter physical exam general:** Fatigued but comfortable, NAD
**content props encounter physical exam msk:** Bilateral swelling/tenderness MCPs 2-3, PIPs 2-3, MTPs 2-3; synovitis; reduced grip
**content props encounter assessment impression:** Seropositive Rheumatoid Arthritis (active)
**content props encounter assessment differential 0:** Psoriatic Arthritis
**content props encounter assessment differential 1:** Systemic Lupus Erythematosus
**content props encounter plan investigations labs 0:** RF
**content props encounter plan investigations labs 1:** Anti-CCP
**content props encounter plan investigations labs 2:** CBC
**content props encounter plan investigations labs 3:** LFTs
**content props encounter plan management medications started 0 name:** Methotrexate
**content props encounter plan management medications started 0 dose:** 10 mg
**content props encounter plan management medications started 0 route:** PO
**content props encounter plan management medications started 0 frequency:** weekly
**content props patient name:** Sarah Miller
**content props patient sex:** Female
**content props patient age at first encounter:** 53
**content props encounterIndex:** 0
**content props dataSource:** Nervecentre
**createdAt:** 2025-10-14T16:55:00.003Z
**updatedAt:** 2025-10-14T16:55:00.003Z