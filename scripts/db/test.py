"""simple script to test database connection."""

import sys
from pathlib import Path

# add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import test_connection
import json

if __name__ == "__main__":
    print("testing database connection...")
    result = test_connection()

    if result["connected"]:
        print("✓ database connection successful!")
        print(f"  database: {result['database']}")
        print(f"  user: {result['user']}")
        print(f"  postgres version: {result['postgres_version']}")
        print(f"  server time: {result['server_time']}")
    else:
        print("✗ database connection failed!")
        print(f"  error: {result['error']}")

    print("\nfull result:")
    print(json.dumps(result, indent=2))
