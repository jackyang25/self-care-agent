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

