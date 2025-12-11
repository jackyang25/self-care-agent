# Manual Testing Guide

## Test Cases

### Test Case 1: High-Risk Symptoms with Referral

**Query:**
```
I have severe chest pain and feel dizzy. Should I see a doctor?
```

**Expected Behavior:**
- Triage → Referrals (based on triage result indicating high risk)

**Tests:**
- Tool result triggers next tool
- Multi-step reasoning
- Conditional escalation

---

### Test Case 2: Multiple Needs

**Query:**
```
I need to refill my diabetes medication and also check if I should see a doctor about my symptoms
```

**Expected Behavior:**
- Triage → Pharmacy + possibly Referrals

**Tests:**
- Multiple needs, multiple tools
- Tool chaining for complex requests

---

### Test Case 3: Critical Risk with Consent Flow

**Query:**
```
I'm having trouble breathing and my chest feels tight. What should I do?
```

**Expected Behavior:**
- Triage → Emergency instructions → Ask for consent → Referrals (if consented)

**Tests:**
- Critical risk handling
- Safety prioritization
- Consent flow
- Tool chaining based on severity

---

### Test Case 4: Medium Risk with Consent

**Query:**
```
I've been having stomach pain for 3 days and I'm worried
```

**Expected Behavior:**
- Triage → Ask if user wants to schedule → Referrals (if yes)

**Tests:**
- Medium risk handling
- Consent before scheduling
- Result-based decision making

---

### Test Case 5: Risk Assessment with Care Pathway

**Query:**
```
I'm feeling dizzy and nauseous, should I get medication or see a doctor?
```

**Expected Behavior:**
- Triage → Referrals (likely) or Pharmacy

**Tests:**
- Risk assessment → appropriate care pathway

---

### Test Case 6: Basic RAG Retrieval

**Query:**
```
What should I know about managing diabetes?
```

**Expected Behavior:**
- Agent calls `rag_retrieval` with query about diabetes
- Retrieves "Diabetes Self-Care Basics" document
- Agent responds with information from retrieved document

**Tests:**
- RAG tool is called (check logs or tool execution)
- Relevant document is retrieved (similarity > 0.7)
- Agent incorporates retrieved information in response

---

### Test Case 7: Symptom-Specific Knowledge

**Query:**
```
I have a fever. What should I do?
```

**Expected Behavior:**
- Agent may call `rag_retrieval` for fever management guidelines
- Retrieves "Fever Management Guidelines" document
- Agent provides evidence-based fever management advice

**Tests:**
- RAG retrieves fever-related content
- Agent combines RAG knowledge with triage assessment
- Response includes actionable guidance from knowledge base

---

### Test Case 8: Emergency Red Flags with RAG

**Query:**
```
I'm having chest pain. Should I be worried?
```

**Expected Behavior:**
- Agent calls triage first (mandatory for symptoms)
- Agent may call `rag_retrieval` for chest pain red flags
- Retrieves "Chest Pain Red Flags" document
- Agent provides appropriate emergency guidance

**Tests:**
- RAG supplements triage with protocol knowledge
- Emergency information is clearly communicated
- Tool chaining: triage → RAG → response

---

### Test Case 9: No Relevant Documents

**Query:**
```
Tell me about a rare condition that's not in the knowledge base
```

**Expected Behavior:**
- Agent calls `rag_retrieval`
- No documents meet similarity threshold
- Agent handles gracefully (doesn't crash)
- Agent responds appropriately without retrieved context

**Tests:**
- System handles empty results gracefully
- Agent doesn't fabricate information
- Error handling works correctly

---

## Demo Credentials

### Agent Login Page

**Demo Email:**
```
jack.yang@gatesfoundation.org
```

**Demo Phone:**
```
+12066608261
```

---

## Database Connection

### PostgreSQL Server

**Container Name:**
```
gh-ai-self-care-db
```

**Connection Details:**
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=selfcare
```

**Access:**
- Host: `localhost` (from host) or `db` (from container)
- Port: `5432`
- pgAdmin: `http://localhost:5050`

