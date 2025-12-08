"""simple script to test database connection."""

from src.db import test_connection
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
