# Tool Descriptions for Agent Toolbox

> **Note:** This is a prototype implementation. Tool responses contain mocked data, but the input/output schemas and tool chaining patterns represent architectural slots for future integration with a deployable system.

## Tool Architecture

All tools use LangChain's `StructuredTool` with Pydantic input schemas. Tools return structured data (JSON for triage, strings for others) that can be parsed and stored in the interactions database.

**Tool Storage:** Tool invocations are stored in the `interactions` table:
- Tool names are stored in `input.tools_called` (JSONB array)
- Tool arguments and results are captured via `extract_tool_info_from_messages()`
- Full tool invocation details (name, args, results) are architectural slots for future `tools` JSONB column

---

## 1. Triage and Risk Flagging Tool

**Tool Name:** `triage_and_risk_flagging`

**Purpose:** Assess patient symptoms and assign a risk category. This is the primary entry point for health-related queries. The tool applies validated self-care protocols and red-flag rules to determine the safest recommended next step.

**Use this tool when:**
- User describes symptoms, discomfort, or potential illnesses
- User asks whether they should seek care, self-manage, or escalate
- User needs a risk assessment before accessing services or commodities

**Do not use this tool for:**
- Ordering medications, self-tests, or other commodities
- Booking labs, teleconsultations, or appointments
- Administrative questions unrelated to clinical symptoms or risk

**Input Parameters:**
- `symptoms` (string, optional): Patient symptoms or complaints. Should include duration, severity, location, and associated symptoms
- `urgency` (string, optional): Pre-assessed urgency level. Accepted values: `"low"`, `"medium"`, `"high"`, `"critical"`. If not provided, defaults to `"low"`
- `patient_id` (string, optional): Patient identifier for tracking and continuity of care
- `notes` (string, optional): Additional clinical notes, context, or relevant medical history

**Response Format (Structured JSON):**
```json
{
  "status": "success",
  "risk_level": "high",
  "recommendation": "immediate clinical evaluation recommended",
  "symptoms": "chest pain for 2 hours",
  "urgency": "high",
  "patient_id": "uuid-here",
  "notes": "patient has history of heart disease"
}
```

**Risk Level Recommendations:**
- `high`/`critical`: "immediate clinical evaluation recommended"
- `medium`: "clinical evaluation recommended within 24-48 hours"
- `low`: "continue monitoring, self-care may be appropriate"

**Architectural Notes:**
- Response is structured JSON for easy parsing and storage
- Risk level and recommendation are extracted and stored in `interactions.risk_level` and `interactions.recommendations`
- Tool invocation is tracked in `interactions.input.tools_called`
- Future: Will integrate with validated triage protocols and clinical decision support systems

---

## 2. Commodity Orders and Fulfillment Tool

**Tool Name:** `commodity_orders_and_fulfillment`

**Purpose:** Help users order self-tests, medicines, or other health commodities. Orchestrates ordering, pickup, or home delivery through retail and pharmacy partners.

**Use this tool when:**
- User wants to order or reorder a health commodity
- User asks about pickup, delivery, or availability of a specific item
- User wants to check or manage the status of an existing commodity order

**Do not use this tool for:**
- Prescription-only pharmacy orders (use Pharmacy Orders tool instead)
- Symptom assessment or medical triage
- Scheduling labs, teleconsults, or clinical appointments

**Input Parameters:**
- `items` (string, optional): List of items to order. Example: `"pregnancy test kit, condoms, ibuprofen 200mg"`
- `quantity` (string, optional): Quantities for each item. Example: `"2, 1 pack, 1 bottle"`
- `patient_id` (string, optional): Patient identifier for order tracking and delivery coordination
- `priority` (string, optional): Order priority level. Accepted values: `"normal"`, `"urgent"`. Defaults to `"normal"`

**Response Format (String):**
```
order processed successfully. order_id: ORD-12345, estimated_delivery: 2025-12-10. status: success
```

**Architectural Notes:**
- Currently returns mocked order IDs and delivery dates
- Future: Will integrate with inventory management, logistics, and fulfillment systems
- Order tracking and status updates are architectural slots

---

## 3. Pharmacy Orders and Fulfillment Tool

**Tool Name:** `pharmacy_orders_and_fulfillment`

**Purpose:** Manage pharmacy-specific orders, including prescription refills and over-the-counter medications that require pharmacy fulfillment. Designed for items requiring pharmacy workflows rather than general retail logistics.

**Use this tool when:**
- User requests a prescription refill or pharmacy-managed medication
- User asks about pharmacy availability, stock, or order status
- User needs support with pharmacy pickup or home delivery

**Do not use this tool for:**
- Ordering general self-test kits or non-pharmacy commodities (use Commodity Orders tool instead)
- Triage, symptom assessment, or risk evaluation
- Scheduling referrals, labs, or teleconsultations

**Input Parameters:**
- `medication` (string, optional): Medication name or prescription identifier. Example: `"amoxicillin 500mg capsules"` or `"prescription RX-12345"`
- `dosage` (string, optional): Dosage instructions. Example: `"take 1 capsule twice daily for 7 days"`
- `patient_id` (string, optional): Patient identifier for prescription verification and order tracking
- `pharmacy` (string, optional): Preferred pharmacy location or pharmacy name. If not specified, uses default pharmacy

**Response Format (String):**
```
prescription order processed. prescription_id: RX-67890, pharmacy: main pharmacy, ready_date: 2025-12-05. status: success
```

**Architectural Notes:**
- Currently returns mocked prescription IDs and pharmacy names
- Future: Will integrate with pharmacy management systems, prescription verification, and inventory systems
- Prescription refill workflows and insurance verification are architectural slots

---

## 4. Referrals and Scheduling Tool

**Tool Name:** `referrals_and_scheduling`

**Purpose:** Create referrals and schedule clinical appointments. Connects users to healthcare providers, books clinic or telemedicine appointments, and coordinates next steps with clinical partners.

**Use this tool when:**
- User agrees to or requests a referral to clinical care (after triage indicates need)
- User wants to book, reschedule, or confirm an appointment
- User needs information about where and when to receive care

**Do not use this tool for:**
- Ordering commodities or medications
- Pharmacy refills or retail logistics
- Symptom triage or risk-level determination

**Input Parameters:**
- `specialty` (string, optional): Medical specialty or department. Examples: `"cardiology"`, `"pediatrics"`, `"general practice"`, `"telemedicine"`, `"emergency"`
- `provider` (string, optional): Preferred provider name or provider identifier. If not specified, system assigns available provider
- `patient_id` (string, optional): Patient identifier for appointment scheduling and medical record access
- `preferred_date` (string, optional): Preferred appointment date. Example: `"2025-12-15"` or `"next Monday"`
- `preferred_time` (string, optional): Preferred appointment time. Example: `"10:00 AM"` or `"14:30"`
- `reason` (string, optional): Reason for referral or appointment. Should include chief complaint, relevant symptoms, or clinical indication

**Response Format (String):**
```
appointment scheduled successfully. appointment_id: APT-11111, provider: dr. smith, date: 2025-12-15, time: 10:00 AM. status: success
```

**Architectural Notes:**
- **Consent Required:** Tool should only be called after explicit user consent (especially for high-risk cases)
- Currently returns mocked appointment IDs and provider names
- Future: Will integrate with appointment scheduling systems, provider availability, and EHR systems
- Appointment reminders and follow-up coordination are architectural slots

---

## 5. Database Query Tool

**Tool Name:** `database_query`

**Purpose:** Retrieve user data from the database. Provides access to user profiles, interaction history, and consent records for the currently logged-in user.

**Use this tool when:**
- Agent needs to access current user's profile information
- Agent needs to check user's past interactions, triage results, or consent records
- Agent needs to get user's complete medical history

**Do not use this tool for:**
- Creating, updating, or deleting records (not implemented)
- Accessing other users' data (only current user accessible)

**Input Parameters:**
- `query_type` (string, required): Type of query. Accepted values:
  - `"get_user_by_id"`: Retrieve current user's profile information
  - `"get_user_interactions"`: Get current user's interaction history (ordered by most recent)
  - `"get_user_history"`: Get current user's complete history including profile, interactions, and consents
- `user_id` (string, optional): Deprecated - tool automatically uses current logged-in user from session context
- `email` (string, optional): Deprecated - not used
- `phone` (string, optional): Deprecated - not used
- `limit` (integer, optional): Maximum number of results to return (default: 10)

**Response Format (String):**
- Returns formatted string with query results (user data, interactions, or complete history)
- Format: `"user found: {...}"` or `"found N interaction(s): [...]"`

**Architectural Notes:**
- Tool automatically uses current user from session context (via `current_user_id` context variable)
- Only accessible for logged-in users
- Future: May add query types for analytics, reporting, or administrative functions

---

## Tool Chaining Patterns

The agent is designed to chain tools sequentially to complete multi-step workflows:

### Common Workflows:

1. **Symptom Assessment → Commodity Order:**
   ```
   triage_and_risk_flagging → commodity_orders_and_fulfillment
   ```
   Example: User reports symptoms and requests medication

2. **Symptom Assessment → Referral:**
   ```
   triage_and_risk_flagging → referrals_and_scheduling (with user consent)
   ```
   Example: User reports high-risk symptoms, triage recommends clinical evaluation, user consents to appointment

3. **Symptom Assessment → Pharmacy Refill:**
   ```
   triage_and_risk_flagging → pharmacy_orders_and_fulfillment
   ```
   Example: User needs prescription refill after assessment

4. **Multi-Request Handling:**
   ```
   triage_and_risk_flagging → commodity_orders_and_fulfillment → referrals_and_scheduling
   ```
   Example: User says "I have symptoms X and need medication Y and want to see a doctor"

### Tool Chaining Rules:

- **Triage First:** Always call `triage_and_risk_flagging` when users report symptoms or health concerns
- **Fulfill All Requests:** After triage, review original user request and call appropriate tools for medication/commodities/services
- **Consent Before Scheduling:** For referrals, always ask for user consent before calling `referrals_and_scheduling`
- **Emergency Priority:** For high/critical risk, provide emergency instructions first, then ask about scheduling

---

## Interaction Storage Architecture

All tool invocations are automatically tracked and stored in the `interactions` table:

**Current Storage:**
- `input.tools_called`: Array of tool names that were called (e.g., `["triage_and_risk_flagging", "commodity_orders_and_fulfillment"]`)
- `protocol_invoked`: Protocol name if triage was called (e.g., `"triage"`)
- `protocol_version`: Protocol version (e.g., `"1.0"`)
- `triage_result`: JSONB with triage assessment results (symptoms, urgency)
- `risk_level`: Extracted risk level from triage (`"low"`, `"medium"`, `"high"`, `"critical"`)
- `recommendations`: Array of recommendations from tool results

**Future Architectural Slot:**
- `tools` JSONB column: Full tool invocation details including:
  ```json
  [
    {
      "name": "triage_and_risk_flagging",
      "args": {"symptoms": "...", "urgency": "high"},
      "result": {"status": "success", "risk_level": "high", ...}
    }
  ]
  ```

This will enable:
- Complete audit trail of tool usage
- Easy querying: `WHERE tools @> '[{"name": "triage_and_risk_flagging"}]'`
- Analytics on tool usage patterns
- Debugging and troubleshooting

---

## General Architecture Notes

### Prototype Implementation:
- All tools return mocked data (order IDs, appointment IDs, etc.)
- Tool schemas and response formats represent architectural contracts
- Tool chaining logic is implemented and functional
- Database storage captures tool invocation metadata

### Future Integration Points:
- **Triage:** Clinical decision support systems, validated protocols
- **Commodity/Pharmacy:** Inventory management, logistics, fulfillment systems
- **Referrals:** Appointment scheduling systems, provider networks, EHR integration
- **Database:** Analytics, reporting, audit logging

### Input Validation:
- All parameters are currently optional (prototype flexibility)
- Production should enforce required fields based on tool purpose
- Date/time formats should be standardized (ISO 8601 recommended)
- Urgency/priority values should be validated against allowed enums

### Error Handling:
- Tools should handle missing required information gracefully
- Agent should request clarification when information is insufficient
- Tool failures should be logged and stored in interaction records
