"""seed database with fixture data from json files."""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import get_db_cursor


def load_fixture_file(fixture_file: str) -> dict:
    """load fixture data from json file."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / fixture_file
    if not fixture_path.exists():
        raise FileNotFoundError(f"fixture file not found: {fixture_path}")
    with open(fixture_path, "r") as f:
        return json.load(f)


def seed_all(fixture_file: str = "seed_data.json", clear_existing: bool = False, table: Optional[str] = None):
    """seed database from fixture file."""
    print(f"loading fixture file: {fixture_file}")
    data = load_fixture_file(fixture_file)
    
    with get_db_cursor() as cur:
        # seed users
        if (table is None or table == "users") and data.get("users"):
            if clear_existing:
                cur.execute("TRUNCATE TABLE users CASCADE")
            
            for user in data["users"]:
                cur.execute("""
                    INSERT INTO users (
                        user_id, fhir_patient_id, primary_channel, phone_e164,
                        email, preferred_language, literacy_mode, country_context_id,
                        demographics, accessibility, is_deleted, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, false, now(), now()
                    )
                    ON CONFLICT (user_id) DO NOTHING
                """, (
                    user.get("user_id"),
                    user.get("fhir_patient_id"),
                    user.get("primary_channel"),
                    user.get("phone_e164"),
                    user.get("email"),
                    user.get("preferred_language"),
                    user.get("literacy_mode"),
                    user.get("country_context_id"),
                    json.dumps(user.get("demographics", {})),
                    json.dumps(user.get("accessibility", {})),
                ))
            print(f"  seeded {len(data['users'])} user(s)")
        
        # seed interactions
        if (table is None or table == "interactions") and data.get("interactions"):
            if clear_existing:
                cur.execute("TRUNCATE TABLE interactions CASCADE")
            
            for interaction in data["interactions"]:
                # handle input - convert string to json if needed
                input_data = interaction.get("input")
                if isinstance(input_data, str):
                    input_data = {"text": input_data}
                
                # handle follow_up_at
                follow_up_at = interaction.get("follow_up_at")
                if follow_up_at:
                    try:
                        follow_up_at = datetime.fromisoformat(str(follow_up_at).replace("Z", "+00:00"))
                    except:
                        follow_up_at = None
                
                cur.execute("""
                    INSERT INTO interactions (
                        interaction_id, user_id, channel, input, protocol_invoked,
                        protocol_version, triage_result, risk_level, recommendations,
                        follow_up_at, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                    )
                    ON CONFLICT (interaction_id) DO NOTHING
                """, (
                    interaction.get("interaction_id"),
                    interaction.get("user_id"),
                    interaction.get("channel"),
                    json.dumps(input_data),
                    interaction.get("protocol_invoked"),
                    interaction.get("protocol_version"),
                    json.dumps(interaction.get("triage_result", {})),
                    interaction.get("risk_level"),
                    json.dumps(interaction.get("recommendations", [])),
                    follow_up_at,
                ))
            print(f"  seeded {len(data['interactions'])} interaction(s)")
        
        # seed consents
        if (table is None or table == "consents") and data.get("consents"):
            if clear_existing:
                cur.execute("TRUNCATE TABLE consents CASCADE")
            
            for consent in data["consents"]:
                # handle recorded_at
                recorded_at = consent.get("recorded_at")
                if recorded_at:
                    try:
                        recorded_at = datetime.fromisoformat(str(recorded_at).replace("Z", "+00:00"))
                    except:
                        recorded_at = datetime.now()
                else:
                    recorded_at = datetime.now()
                
                cur.execute("""
                    INSERT INTO consents (
                        consent_id, user_id, scope, status, version,
                        jurisdiction, evidence, recorded_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (consent_id) DO NOTHING
                """, (
                    consent.get("consent_id"),
                    consent.get("user_id"),
                    consent.get("scope"),
                    consent.get("status"),
                    consent.get("version"),
                    consent.get("jurisdiction"),
                    json.dumps(consent.get("evidence", {})),
                    recorded_at,
                ))
            print(f"  seeded {len(data['consents'])} consent(s)")
    
    print("✓ seeding completed")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="seed database with fixture data")
    parser.add_argument("--file", default="seed_data.json", help="fixture file name")
    parser.add_argument("--clear", action="store_true", help="clear existing data before seeding")
    parser.add_argument("--table", choices=["users", "interactions", "consents"], help="seed only a specific table")
    
    args = parser.parse_args()
    seed_all(args.file, args.clear, args.table)
