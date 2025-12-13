# Triage Verification System

Formally verified triage classification using the `triage-lean` executable.

## Overview

The `triage-verifier` executable is a formally verified binary that classifies patients into emergency categories based on vital signs and symptoms. The verification ensures the triage logic is mathematically correct and consistent.

## Executable Location

```
bin/triage-verifier
```

Located in the `bin/` directory.

## Usage

```bash
./bin/triage-verifier <age> <gender> <pregnant> <breathing> <conscious> <walking> <severeSymptom> <moderateSymptom>
```

## Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `age` | number | Patient age in years (use 0 for infant) |
| `gender` | string | `"male"` or `"female"` |
| `pregnant` | 0/1 | 1 if pregnant, 0 if not |
| `breathing` | 0/1 | 1 if breathing normally, 0 if not |
| `conscious` | 0/1 | 1 if conscious, 0 if not |
| `walking` | 0/1 | 1 if can walk, 0 if not |
| `severeSymptom` | 0/1 | 1 if severe symptoms present, 0 if not |
| `moderateSymptom` | 0/1 | 1 if moderate symptoms present, 0 if not |

## Exit Codes

| Exit Code | Category | Meaning |
|-----------|----------|---------|
| 0 | RED | Immediate emergency |
| 1 | YELLOW | Urgent |
| 2 | GREEN | Non-urgent |

## Triage Rules (Formally Verified)

### RED (Exit Code 0) - Immediate Emergency
Patient is classified RED if ANY of the following:
- Not breathing (`breathing=0`)
- Unconscious (`conscious=0`)
- Severe symptom present (`severeSymptom=1`)
- Moderate symptom + high-risk factors:
  - Infant (`age=0`)
  - Elderly (`age>65`)
  - Pregnant female (`gender="female"` AND `pregnant=1`)

### YELLOW (Exit Code 1) - Urgent
Patient is classified YELLOW if:
- Cannot walk (`walking=0`)
- Moderate symptom present (`moderateSymptom=1`) without high-risk factors

### GREEN (Exit Code 2) - Non-urgent
Patient is classified GREEN if:
- None of the above conditions apply (stable patient)

## Python Integration

```python
import subprocess

def triage_patient(age, gender, pregnant, breathing, conscious, walking, severe, moderate):
    """
    classify patient using formally verified triage executable.
    
    returns: "RED", "YELLOW", "GREEN", or "UNKNOWN"
    """
    result = subprocess.run(
        ["./bin/triage-verifier", str(age), gender, str(pregnant), str(breathing), 
         str(conscious), str(walking), str(severe), str(moderate)],
        capture_output=True, text=True
    )
    categories = {0: "RED", 1: "YELLOW", 2: "GREEN"}
    return categories.get(result.returncode, "UNKNOWN")
```

## Examples

### GREEN - Stable Patient
```bash
# 30yo male, breathing, conscious, walking, no symptoms
./bin/triage-verifier 30 male 0 1 1 1 0 0
# Output: Category.green
# Exit code: 2
```

### YELLOW - Urgent
```bash
# 30yo male, cannot walk
./bin/triage-verifier 30 male 0 1 1 0 0 0
# Output: Category.yellow
# Exit code: 1

# 30yo male, moderate symptom only
./bin/triage-verifier 30 male 0 1 1 1 0 1
# Output: Category.yellow
# Exit code: 1
```

### RED - Immediate Emergency
```bash
# not breathing
./bin/triage-verifier 30 male 0 0 1 1 0 0
# Output: Category.red
# Exit code: 0

# unconscious
./bin/triage-verifier 30 male 0 1 0 1 0 0
# Output: Category.red
# Exit code: 0

# pregnant female with moderate symptom (high-risk)
./bin/triage-verifier 30 female 1 1 1 1 0 1
# Output: Category.red
# Exit code: 0

# infant with moderate symptom (high-risk)
./bin/triage-verifier 0 male 0 1 1 1 0 1
# Output: Category.red
# Exit code: 0

# elderly with moderate symptom (high-risk)
./bin/triage-verifier 70 male 0 1 1 1 0 1
# Output: Category.red
# Exit code: 0
```

## Integration with Triage Tool

The verified executable can be integrated with the existing `triage_and_risk_flagging` tool in `src/tools/triage.py` to provide:

1. **Verification layer**: validate LLM-determined urgency against formally verified logic
2. **Structured assessment**: when vital signs are available, use verified classification
3. **Audit trail**: log both LLM assessment and verified result for comparison

### Database Integration

User demographics (`age`, `gender`) can be pulled from the `users.demographics` JSONB field:

```python
from src.db import get_db_cursor
from src.utils.context import current_user_id

def get_user_demographics():
    user_id = current_user_id.get()
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT demographics FROM users WHERE user_id = %s",
            (user_id,)
        )
        result = cur.fetchone()
        if result and result[0]:
            return result[0].get("age"), result[0].get("gender")
    return None, None
```

## File Info

- **Binary**: Mach-O 64-bit executable arm64
- **Size**: ~7.1 MB
- **SHA-256**: `7f71ad1328ad1e9cf5ab73b0e201f33ac63ecac94f9f19396ddd6aad103e4590`

## Limitations & Scope

### Current Coverage

The formal verification currently has **limited theorem coverage** due to minimal assumptions in the verification context. This means:

- The verified logic is **safely constrained** within a well-defined input/output space
- All behaviors within this space are **provably correct** given the current logic
- The verification guarantees **logical correctness**, not clinical completeness

### What This Provides

1. **Logical correctness**: the triage rules execute exactly as specified, with no edge cases or undefined behavior within the input domain
2. **Deterministic classification**: same inputs always produce same outputs
3. **Safety constraint**: the logic cannot produce results outside the defined category set (RED/YELLOW/GREEN)

### What This Does Not (Yet) Provide

- **Clinical validity**: the rules may not reflect comprehensive clinical triage protocols
- **Full domain coverage**: additional theorems and assumptions would expand the verified behavior space
- **Edge case handling**: inputs outside expected ranges have undefined verification status

### Integration with LLM

The system combines:
- **LLM requirements gathering**: dynamic extraction of vital signs and symptoms from natural conversation
- **Verified classification**: deterministic, provably correct categorization of structured inputs

This hybrid approach leverages:
- LLM flexibility for understanding patient descriptions
- Formal verification for safety-critical classification logic

As the theorem coverage expands, the verified behavior space will grow while maintaining the same correctness guarantees.

## Notes

- the executable must have execute permissions: `chmod +x triage-verifier`
- formally verified means the triage logic has been mathematically proven correct
- this provides a safety layer independent of LLM reasoning

