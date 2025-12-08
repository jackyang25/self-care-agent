"""check if database is empty and seed if needed."""

import sys
from pathlib import Path

# add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.db import get_db_cursor
from db_seed import seed_all


def is_database_empty() -> bool:
    """check if database has any data in main tables."""
    try:
        with get_db_cursor() as cur:
            # check if users table exists and has data
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                )
            """)
            table_exists = cur.fetchone()["exists"]
            
            if not table_exists:
                return True
            
            # check if any users exist
            cur.execute("SELECT COUNT(*) as count FROM users WHERE is_deleted = false")
            user_count = cur.fetchone()["count"]
            
            return user_count == 0
    except Exception as e:
        # if tables don't exist or error, consider it empty
        print(f"warning: could not check database state: {e}")
        return True


def auto_seed_if_empty(fixture_file: str = "seed_data.json", force: bool = False) -> bool:
    """seed database if empty, return True if seeded."""
    if force or is_database_empty():
        print("database is empty, seeding with fixture data...")
        try:
            seed_all(fixture_file, clear_existing=False)
            print("✓ auto-seeding completed")
            return True
        except Exception as e:
            print(f"warning: auto-seeding failed: {e}")
            return False
    else:
        print("database already contains data, skipping auto-seed")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="check database and seed if empty")
    parser.add_argument(
        "--file",
        default="seed_data.json",
        help="fixture file name (default: seed_data.json)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="force seeding even if database has data",
    )
    
    args = parser.parse_args()
    
    auto_seed_if_empty(args.file, args.force)

