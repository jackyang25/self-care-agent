"""simple test for triage-verifier executable without dependencies."""

import subprocess
import os
from pathlib import Path

print("=" * 60)
print("testing triage-verifier executable")
print("=" * 60)

# get path to executable (scripts/tools/ -> scripts/ -> root/)
project_root = Path(__file__).resolve().parents[2]
executable = project_root / "bin" / "triage-verifier"


if not os.path.exists(executable):
    print(f"✗ executable not found at: {executable}")
    exit(1)

print(f"✓ found executable at: {executable}\n")


def test_triage(
    name,
    age,
    gender,
    pregnant,
    breathing,
    conscious,
    walking,
    severe,
    moderate,
    expected_code,
):
    """run a single test case."""
    print(f"test: {name}")
    print(
        f"  input: age={age}, gender={gender}, pregnant={pregnant}, breathing={breathing}, conscious={conscious}, walking={walking}, severe={severe}, moderate={moderate}"
    )

    result = subprocess.run(
        [
            executable,
            str(age),
            gender,
            str(pregnant),
            str(breathing),
            str(conscious),
            str(walking),
            str(severe),
            str(moderate),
        ],
        capture_output=True,
        text=True,
    )

    categories = {0: "RED", 1: "YELLOW", 2: "GREEN"}
    category = categories.get(result.returncode, "UNKNOWN")

    print(f"  output: {result.stdout.strip()}")
    print(f"  result: {category} (exit code: {result.returncode})")
    print(f"  expected: exit code {expected_code}")

    if result.returncode == expected_code:
        print(f"  ✓ passed\n")
        return True
    else:
        print(f"  ✗ failed\n")
        return False


# run tests
tests_passed = 0
tests_total = 0

# test 1: stable patient (GREEN)
tests_total += 1
if test_triage("stable patient", 30, "male", 0, 1, 1, 1, 0, 0, 2):
    tests_passed += 1

# test 2: not breathing (RED)
tests_total += 1
if test_triage("not breathing", 30, "male", 0, 0, 1, 1, 0, 0, 0):
    tests_passed += 1

# test 3: unconscious (RED)
tests_total += 1
if test_triage("unconscious", 30, "male", 0, 1, 0, 1, 0, 0, 0):
    tests_passed += 1

# test 4: cannot walk (YELLOW)
tests_total += 1
if test_triage("cannot walk", 30, "male", 0, 1, 1, 0, 0, 0, 1):
    tests_passed += 1

# test 5: moderate symptom only (YELLOW)
tests_total += 1
if test_triage("moderate symptom", 30, "male", 0, 1, 1, 1, 0, 1, 1):
    tests_passed += 1

# test 6: pregnant + moderate (RED - high risk)
tests_total += 1
if test_triage("pregnant + moderate", 30, "female", 1, 1, 1, 1, 0, 1, 0):
    tests_passed += 1

# test 7: elderly + moderate (RED - high risk)
tests_total += 1
if test_triage("elderly + moderate", 70, "male", 0, 1, 1, 1, 0, 1, 0):
    tests_passed += 1

# test 8: infant + moderate (RED - high risk)
tests_total += 1
if test_triage("infant + moderate", 0, "male", 0, 1, 1, 1, 0, 1, 0):
    tests_passed += 1

# test 9: severe symptom (RED)
tests_total += 1
if test_triage("severe symptom", 30, "male", 0, 1, 1, 1, 1, 0, 0):
    tests_passed += 1

print("=" * 60)
print(f"results: {tests_passed}/{tests_total} tests passed")
if tests_passed == tests_total:
    print("✓ all tests passed!")
else:
    print(f"✗ {tests_total - tests_passed} test(s) failed")
print("=" * 60)
