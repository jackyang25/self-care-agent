# Manual Testing Guide

Quick reference for testing agent workflows and demonstrating architecture capabilities.

**Demo User Credentials:**
- Email: `jack.yang@gatesfoundation.org`
- Phone: `+12066608261`

---

## 1. Single Tool Workflows

### 1.1 Information Retrieval (RAG Only)

```
What should I know about managing diabetes?
```

**Expected Tools:** `rag_retrieval`

**Expected Output:**
- Retrieves "Diabetes Self-Care Basics" document
- Provides evidence-based information with natural citations
- No triage needed (no symptoms reported)

**Showcases:** RAG grounding for clinical questions

---

### 1.2 User History Lookup (Database Only)

```
Do I have any appointments scheduled?
```

**Expected Tools:** `database_query` (query_type: "get_user_appointments")

**Expected Output:**
- Lists user's scheduled appointments with provider details
- Includes date, time, specialty, and reason

**Showcases:** Context-aware user data retrieval

---

### 1.3 Simple Triage (Triage Only)

```
I have a mild headache. Is this serious?
```

**Expected Tools:** `triage_and_risk_flagging`

**Expected Output:**
- Risk level: green (low acuity)
- Suggests self-care or pharmacy support
- No referral needed

**Showcases:** Basic symptom assessment

---

## 2. Sequential Tool Chaining

### 2.1 Triage → Emergency Referral

```
I have severe chest pain radiating to my left arm. Should I see a doctor?
```

**Expected Tools:** `triage_and_risk_flagging` → `referrals_and_scheduling` (after consent)

**Expected Output:**
1. Risk level: red/critical (high acuity)
2. Emergency instructions provided immediately
3. Asks for consent to schedule
4. After consent: schedules with cardiology
5. Confirms appointment details

**Showcases:** Critical pathway with consent flow, specialty routing

---

### 2.2 Triage → Pharmacy Fulfillment

```
I have a fever of 101°F and need some ibuprofen. Can you help?
```

**Expected Tools:** `triage_and_risk_flagging` → `pharmacy_orders_and_fulfillment`

**Expected Output:**
1. Assesses fever (likely low-medium risk)
2. Processes pharmacy order for ibuprofen
3. Provides order confirmation with pharmacy details

**Showcases:** Symptom assessment followed by medication fulfillment

---

### 2.3 RAG → Grounded Response

```
I have a fever. What should I do?
```

**Expected Tools:** `triage_and_risk_flagging` → `rag_retrieval`

**Expected Output:**
1. Assesses fever symptoms
2. Retrieves "Fever Management Guidelines"
3. Provides evidence-based fever management advice
4. Cites retrieved guidelines naturally

**Showcases:** Clinical grounding with RAG after triage

---

## 3. Parallel Tool Calling

### 3.1 History Check + Guidelines Retrieval

```
My cough is back again. What should I do this time?
```

**Expected Tools:** `database_query` (user history) + `rag_retrieval` (cough guidelines) **in parallel**

**Expected Output:**
- Retrieves user's previous cough-related interactions
- Retrieves cough management guidelines
- Provides contextualized advice based on history and guidelines
- May suggest triage if symptoms differ from previous

**Showcases:** Parallel information gathering for context-aware response

---

### 3.2 Provider Lookup + Guidelines Retrieval

```
I need to see a cardiologist. What should I expect at my appointment?
```

**Expected Tools:** `database_query` (get providers, specialty="cardiology") + `rag_retrieval` (cardiology visit prep) **in parallel**

**Expected Output:**
- Lists available cardiologists
- Provides information about cardiology appointment preparation
- Offers to schedule if user wants

**Showcases:** Efficient multi-source information gathering

---

## 4. Complex Multi-Request Handling

### 4.1 Symptoms + Medication + Referral Request

```
I have chest pain and shortness of breath. I also need to refill my blood pressure medication and want to see a doctor as soon as possible.
```

**Expected Tools:**
1. `triage_and_risk_flagging` (symptoms)
2. `pharmacy_orders_and_fulfillment` (medication refill)
3. `referrals_and_scheduling` (after consent, specialty: cardiology)

**Expected Output:**
1. Assesses chest pain → red/critical risk
2. Emergency instructions first
3. Processes blood pressure medication refill
4. Asks consent for appointment
5. Schedules urgent cardiology appointment
6. Confirms all three actions completed

**Showcases:** Comprehensive multi-step workflow, priority handling, fulfills all user requests

---

### 4.2 Medication Refill Without Symptoms

```
I need to refill my diabetes medication and also want to know more about managing blood sugar.
```

**Expected Tools:**
1. `pharmacy_orders_and_fulfillment` (medication)
2. `rag_retrieval` (diabetes management)

**Expected Output:**
- Processes medication refill
- Retrieves diabetes management guidelines
- Provides educational information
- No triage needed (no symptoms)

**Showcases:** Non-clinical pathway, education + fulfillment

---

### 4.3 Moderate Risk with Multiple Actions

```
I've had stomach pain for 3 days. Can you help me figure out what to do and maybe get some antacids?
```

**Expected Tools:**
1. `triage_and_risk_flagging`
2. `commodity_orders_and_fulfillment` (antacids)
3. `rag_retrieval` (stomach pain guidelines) - optional
4. `referrals_and_scheduling` (if user consents)

**Expected Output:**
1. Assesses stomach pain → yellow (moderate risk)
2. Recommends clinical evaluation within 24-48 hours
3. Processes antacid order for symptom relief
4. Asks if user wants to schedule
5. May retrieve stomach pain guidelines for interim self-care

**Showcases:** Moderate risk handling, dual fulfillment (commodity + potential referral)

---

## 5. Context-Aware Interactions

### 5.1 Returning User with Ongoing Condition

```
My symptoms are back, just like last time.
```

**Expected Tools:** `database_query` (query_type: "get_user_history") → `triage_and_risk_flagging`

**Expected Output:**
1. Retrieves user's previous interactions and triage results
2. Performs new triage with historical context
3. Compares current symptoms to previous episodes
4. Provides contextualized recommendations

**Showcases:** Historical context awareness, continuity of care

---

### 5.2 Follow-up After Previous Triage

```
I saw the doctor like we discussed. They prescribed medication. How do I take it?
```

**Expected Tools:** `database_query` (appointments/interactions) + `rag_retrieval` (medication guidance)

**Expected Output:**
- Checks user's recent appointments and interactions
- Retrieves medication adherence/usage guidelines
- Provides personalized guidance based on context

**Showcases:** Care continuity, multi-source context

---

## 6. Edge Cases & Safety

### 6.1 Breathing Emergency

```
I can't breathe properly and my chest feels very tight. Help!
```

**Expected Tools:** `triage_and_risk_flagging` → `referrals_and_scheduling`

**Expected Output:**
1. Immediate emergency escalation
2. "Call emergency services immediately" or "Go to emergency room now"
3. Does NOT suggest "continue monitoring"
4. After emergency instruction, offers to schedule follow-up if appropriate

**Showcases:** Emergency handling, safety prioritization

---

### 6.2 Empty RAG Results

```
Tell me about a very rare tropical disease that's not in the knowledge base.
```

**Expected Tools:** `rag_retrieval`

**Expected Output:**
- Calls RAG but finds no relevant documents
- Acknowledges limitation gracefully
- Does not fabricate information
- May suggest user consult healthcare provider for rare conditions

**Showcases:** Graceful error handling, honesty about limitations

---

### 6.3 Ambiguous Request

```
I'm not feeling well.
```

**Expected Tools:** None initially

**Expected Output:**
- Asks clarifying questions: "Can you describe your symptoms?" "Where does it hurt?" "How long have you felt this way?"
- Gathers more information before calling triage
- Shows intelligent information gathering

**Showcases:** Contextual awareness, appropriate tool deferral

---

## Expected Tool Call Logs

When testing, check logs for tool invocations. Example patterns:

**Single tool:**
```
[tools used: rag_retrieval]
```

**Sequential chaining:**
```
[tools used: triage_and_risk_flagging, referrals_and_scheduling]
```

**Parallel + chaining:**
```
[tools used: database_query, rag_retrieval, triage_and_risk_flagging]
```

---

## Testing Checklist

**Before Demo (Fresh Start):**
- [ ] Reset database and restart services: `make reset-db`
- [ ] Access Streamlit UI: `http://localhost:8501`
- [ ] Login as demo user (credentials at top)
- [ ] Prepare log viewing: `make logs-app` OR use Docker Desktop logs tab

**During Demo:**
1. Start with simple single-tool examples
2. Progress to tool chaining
3. Show parallel calling efficiency
4. Demonstrate complex multi-request handling
5. Highlight context awareness
6. Show safety/edge case handling

**After Demo:**
- [ ] Review tool execution logs (terminal or Docker Desktop)
- [ ] Check interactions saved to database
- [ ] Verify RAG citations displayed correctly

## Quick Reference

### Demo Commands

**Fresh start (recommended before each demo):**
```bash
make reset-db  # stops containers, clears volumes, reseeds database, and restarts services
```

**View logs:**
```bash
make logs-app  # follow application logs in terminal
```

**Alternative:** Use Docker Desktop → Containers → `gh-ai-self-care-app` → Logs tab for GUI log viewing

**Other commands:**
```bash
make up        # start services (if stopped)
make down      # stop services
make restart   # restart containers without clearing data
```

---

### Database Access

**Direct PostgreSQL:**
- Host: `localhost:5432`
- User: `postgres`
- Password: `postgres`
- Database: `selfcare`

**pgAdmin UI:**
- URL: `http://localhost:5050`
- Email: `admin@admin.com`
- Password: `admin`

**Shell access:**
```bash
make shell-db
```

