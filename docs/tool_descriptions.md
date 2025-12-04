# Tool Descriptions for Agent Toolbox

## 1. Triage and Risk Flagging Tool

**Purpose:** Use this tool to triage user health symptoms or questions and assign a risk category. Call this tool when the user reports symptoms, asks about a possible medical condition, expresses concern about their health, or needs guidance on whether their situation requires self-care, pharmacy support, telemedicine, or clinical evaluation. The tool applies validated self-care protocols and red-flag rules to determine the safest recommended next step.

**Use this tool when:**
- The user describes symptoms, discomfort, or potential illnesses.
- The user asks whether they should seek care, self-manage, or escalate.
- The user needs a risk assessment before accessing services or commodities.

**Do not use this tool for:**
- Ordering medications, self-tests, or other commodities.
- Booking labs, teleconsultations, or appointments.
- Administrative questions unrelated to clinical symptoms or risk.

**Input Parameters:**
- `symptoms` (string, optional): Patient symptoms or complaints. Should include duration, severity, location, and any associated symptoms. Example: "chest pain for 2 hours, radiating to left arm, with shortness of breath"
- `urgency` (string, optional): Pre-assessed urgency level. Accepted values: "low", "medium", "high", "critical". If not provided, the tool will assess based on symptoms.
- `patient_id` (string, optional): Patient identifier for tracking and continuity of care.
- `notes` (string, optional): Additional clinical notes, context, or relevant medical history that may impact triage assessment.

**Functional Suggestions:**
- Consider making `symptoms` required (not optional) since this is the core input for triage assessment.
- The `urgency` parameter seems redundant if the tool is meant to determine urgency - consider removing it or renaming to `initial_urgency_hint` if it's meant as a preliminary assessment.
- Consider adding a `duration` field to capture symptom duration, which is critical for risk assessment.
- Consider adding a `vital_signs` or `severity_indicators` field for structured data capture.

---

## 2. Commodity Orders and Fulfillment Tool

**Purpose:** Use this tool to help users order self-tests, medicines, or other health commodities. Call this tool when a user wants to request, purchase, or refill a commodity such as a self-test kit, over-the-counter medicine, contraception, or related supplies. The tool orchestrates ordering, pickup, or home delivery through retail and pharmacy partners and can provide available fulfillment options.

**Use this tool when:**
- The user wants to order or reorder a health commodity.
- The user asks about pickup, delivery, or availability of a specific item.
- The user wants to check or manage the status of an existing commodity order.

**Do not use this tool for:**
- Prescription-only pharmacy orders (use Pharmacy Orders tool instead).
- Symptom assessment or medical triage.
- Scheduling labs, teleconsults, or clinical appointments.

**Input Parameters:**
- `items` (string, optional): List of items to order. Should specify item names, types, or SKUs. Can include multiple items separated by commas or as a structured list. Example: "pregnancy test kit, condoms, ibuprofen 200mg"
- `quantity` (string, optional): Quantities for each item. Should match the order of items specified. Example: "2, 1 pack, 1 bottle" or "2 pregnancy tests, 1 pack of condoms, 1 bottle of ibuprofen"
- `patient_id` (string, optional): Patient identifier for order tracking and delivery coordination.
- `priority` (string, optional): Order priority level. Accepted values: "normal", "urgent". Defaults to "normal" if not specified.

**Functional Suggestions:**
- Consider making `items` required since an order cannot be processed without knowing what to order.
- The `quantity` field as a string is ambiguous - consider using a structured format (JSON) or separate fields for each item, or at least document the expected format more clearly.
- Consider adding a `delivery_method` field (e.g., "pickup", "home_delivery", "pharmacy_pickup") to specify fulfillment preference.
- Consider adding a `delivery_address` field for home delivery orders.
- Consider adding an `order_id` field for checking status of existing orders (separate from creating new orders).

---

## 3. Pharmacy Orders and Fulfillment Tool

**Purpose:** Use this tool to manage pharmacy-specific orders, including prescription refills and over-the-counter medications that require pharmacy fulfillment. Call this tool when a user wants to refill a prescription, request pharmacy-dispensed commodities, check pharmacy inventory, or arrange pharmacy pickup or delivery. This tool is designed for items that require pharmacy workflows rather than general retail logistics.

**Use this tool when:**
- The user requests a prescription refill or pharmacy-managed medication.
- The user asks about pharmacy availability, stock, or order status.
- The user needs support with pharmacy pickup or home delivery.

**Do not use this tool for:**
- Ordering general self-test kits or non-pharmacy commodities (use Commodity Orders tool instead).
- Triage, symptom assessment, or risk evaluation.
- Scheduling referrals, labs, or teleconsultations.

**Input Parameters:**
- `medication` (string, optional): Medication name or prescription identifier. Should include medication name, strength, and form if applicable. Example: "amoxicillin 500mg capsules" or "prescription RX-12345"
- `dosage` (string, optional): Dosage instructions for the medication. Should include frequency, timing, and duration if known. Example: "take 1 capsule twice daily for 7 days"
- `patient_id` (string, optional): Patient identifier for prescription verification and order tracking.
- `pharmacy` (string, optional): Preferred pharmacy location or pharmacy name. If not specified, the system will use the patient's default pharmacy or nearest available location.

**Functional Suggestions:**
- Consider making `medication` required since a pharmacy order needs to specify what medication is being ordered.
- Consider adding a `prescription_id` field separate from `medication` to handle prescription refills more explicitly.
- Consider adding a `refill_number` or `refill_request` boolean field to distinguish between new prescriptions and refills.
- Consider adding a `quantity` field to specify how many units/packs are needed.
- Consider adding a `delivery_method` field similar to the commodity tool.
- The distinction between this tool and the Commodity tool could be clearer - consider adding guidance that pharmacy tool is for items requiring pharmacist oversight, prescription verification, or controlled substances.

---

## 4. Referrals and Scheduling Tool

**Purpose:** Use this tool to create referrals and schedule clinical appointments. Call this tool when a user needs to be connected to a healthcare provider, book a clinic or telemedicine appointment, or follow up on a referral. The tool can generate structured referral information, confirm appointment times, and coordinate next steps with clinical partners.

**Use this tool when:**
- The user agrees to or requests a referral to clinical care.
- The user wants to book, reschedule, or confirm an appointment.
- The user needs information about where and when to receive care.

**Do not use this tool for:**
- Ordering commodities or medications.
- Pharmacy refills or retail logistics.
- Symptom triage or risk-level determination.

**Input Parameters:**
- `specialty` (string, optional): Medical specialty or department for the referral. Examples: "cardiology", "pediatrics", "general practice", "telemedicine", "emergency"
- `provider` (string, optional): Preferred provider name or provider identifier. If not specified, the system will assign an available provider.
- `patient_id` (string, optional): Patient identifier for appointment scheduling and medical record access.
- `preferred_date` (string, optional): Preferred appointment date in ISO format (YYYY-MM-DD) or natural language. Example: "2025-12-15" or "next Monday"
- `preferred_time` (string, optional): Preferred appointment time. Can be in 24-hour format or 12-hour format with AM/PM. Example: "10:00 AM" or "14:30"
- `reason` (string, optional): Reason for referral or appointment. Should include chief complaint, relevant symptoms, or clinical indication. This helps match the patient with the appropriate provider and prepare for the visit.

**Functional Suggestions:**
- Consider making `specialty` required (or at least `reason`) since a referral needs to specify what type of care is needed.
- Consider adding an `appointment_type` field to distinguish between "in-person", "telemedicine", "lab", "follow-up", etc.
- Consider adding an `urgency` field that can be populated from triage results to help prioritize scheduling.
- Consider adding a `referral_id` field for tracking existing referrals or follow-up appointments.
- Consider adding a `location` or `clinic_address` field for in-person appointments.
- The `preferred_date` and `preferred_time` could be combined into a single `preferred_datetime` field for clarity, or kept separate if the system needs flexibility in matching availability.
- Consider adding guidance that this tool should typically be called AFTER triage when clinical evaluation is recommended, and that user consent should be obtained before scheduling.

---

## General Suggestions Across All Tools

1. **Patient ID Consistency:** All tools have `patient_id` as optional. Consider making it required for production use, or at least document when it's necessary vs. optional (e.g., for anonymous consultations vs. registered users).

2. **Error Handling:** Consider documenting what happens when required information is missing or invalid, and how the agent should handle partial information.

3. **Tool Chaining:** Document the typical workflow patterns (e.g., triage → commodity order, triage → referral, pharmacy → referral for prescription issues).

4. **Return Values:** Consider documenting the expected return format/structure from each tool so the agent knows how to interpret results and chain tools appropriately.

5. **Validation Rules:** Add guidance on input validation (e.g., date formats, urgency values, priority levels) to help the agent format inputs correctly.

