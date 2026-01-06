"""seed database with seed data from json files."""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.postgres.connection import get_db_cursor
from src.application.services.rag import store_document, store_source


def load_fixture_file(fixture_file: str) -> dict:
    """load seed data from json file."""
    fixture_path = Path(__file__).parent.parent / "seeds" / fixture_file
    if not fixture_path.exists():
        raise FileNotFoundError(f"seed file not found: {fixture_path}")
    with open(fixture_path, "r") as f:
        return json.load(f)


def seed_all(
    fixture_file: str = "demo.json",
    clear_existing: bool = False,
    table: Optional[str] = None,
):
    """seed database from seed file (app data + RAG documents)."""
    print(f"Loading seed file: {fixture_file}")
    data = load_fixture_file(fixture_file)

    with get_db_cursor() as cur:
        # seed users
        if (table is None or table == "users") and data.get("users"):
            if clear_existing:
                cur.execute("TRUNCATE TABLE users CASCADE")

            for user in data["users"]:
                cur.execute(
                    """
                    INSERT INTO users (
                        user_id, fhir_patient_id, primary_channel, phone_e164,
                        email, preferred_language, literacy_mode, country_context_id,
                        timezone, demographics, accessibility, is_deleted, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, false, now(), now()
                    )
                    ON CONFLICT (user_id) DO NOTHING
                """,
                    (
                        user.get("user_id"),
                        user.get("fhir_patient_id"),
                        user.get("primary_channel"),
                        user.get("phone_e164"),
                        user.get("email"),
                        user.get("preferred_language"),
                        user.get("literacy_mode"),
                        user.get("country_context_id"),
                        user.get("timezone", "UTC"),
                        json.dumps(user.get("demographics", {})),
                        json.dumps(user.get("accessibility", {})),
                    ),
                )
            print(f"  ✓ Seeded {len(data['users'])} user(s)")

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
                        follow_up_at = datetime.fromisoformat(
                            str(follow_up_at).replace("Z", "+00:00")
                        )
                    except:
                        follow_up_at = None

                cur.execute(
                    """
                    INSERT INTO interactions (
                        interaction_id, user_id, channel, input, protocol_invoked,
                        protocol_version, triage_result, risk_level, recommendations,
                        follow_up_at, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                    )
                    ON CONFLICT (interaction_id) DO NOTHING
                """,
                    (
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
                    ),
                )
            print(f"  ✓ Seeded {len(data['interactions'])} interaction(s)")

        # seed consents
        if (table is None or table == "consents") and data.get("consents"):
            if clear_existing:
                cur.execute("TRUNCATE TABLE consents CASCADE")

            for consent in data["consents"]:
                # handle recorded_at
                recorded_at = consent.get("recorded_at")
                if recorded_at:
                    try:
                        recorded_at = datetime.fromisoformat(
                            str(recorded_at).replace("Z", "+00:00")
                        )
                    except:
                        recorded_at = datetime.now()
                else:
                    recorded_at = datetime.now()

                cur.execute(
                    """
                    INSERT INTO consents (
                        consent_id, user_id, scope, status, version,
                        jurisdiction, evidence, recorded_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (consent_id) DO NOTHING
                """,
                    (
                        consent.get("consent_id"),
                        consent.get("user_id"),
                        consent.get("scope"),
                        consent.get("status"),
                        consent.get("version"),
                        consent.get("jurisdiction"),
                        json.dumps(consent.get("evidence", {})),
                        recorded_at,
                    ),
                )
            print(f"  ✓ Seeded {len(data['consents'])} consent(s)")

        # seed providers
        if (table is None or table == "providers") and data.get("providers"):
            if clear_existing:
                cur.execute("TRUNCATE TABLE providers CASCADE")

            for provider in data["providers"]:
                cur.execute(
                    """
                    INSERT INTO providers (
                        provider_id, external_provider_id, external_system, name,
                        specialty, facility, available_days, country_context_id,
                        contact_info, is_active, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                    )
                    ON CONFLICT (provider_id) DO NOTHING
                """,
                    (
                        provider.get("provider_id"),
                        provider.get("external_provider_id"),
                        provider.get("external_system"),
                        provider.get("name"),
                        provider.get("specialty"),
                        provider.get("facility"),
                        provider.get("available_days", []),
                        provider.get("country_context_id"),
                        json.dumps(provider.get("contact_info", {})),
                        provider.get("is_active", True),
                    ),
                )
            print(f"  ✓ Seeded {len(data['providers'])} provider(s)")

        # seed appointments
        if (table is None or table == "appointments") and data.get("appointments"):
            if clear_existing:
                cur.execute("TRUNCATE TABLE appointments CASCADE")

            for appointment in data["appointments"]:
                # handle appointment_date
                appointment_date = appointment.get("appointment_date")

                # handle appointment_time
                appointment_time = appointment.get("appointment_time")

                # handle last_synced_at
                last_synced_at = appointment.get("last_synced_at")
                if last_synced_at:
                    try:
                        last_synced_at = datetime.fromisoformat(
                            str(last_synced_at).replace("Z", "+00:00")
                        )
                    except:
                        last_synced_at = None

                cur.execute(
                    """
                    INSERT INTO appointments (
                        appointment_id, external_appointment_id, external_system,
                        user_id, provider_id, specialty, appointment_date,
                        appointment_time, status, reason, triage_interaction_id,
                        consent_id, sync_status, last_synced_at, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                    )
                    ON CONFLICT (appointment_id) DO NOTHING
                """,
                    (
                        appointment.get("appointment_id"),
                        appointment.get("external_appointment_id"),
                        appointment.get("external_system"),
                        appointment.get("user_id"),
                        appointment.get("provider_id"),
                        appointment.get("specialty"),
                        appointment_date,
                        appointment_time,
                        appointment.get("status", "scheduled"),
                        appointment.get("reason"),
                        appointment.get("triage_interaction_id"),
                        appointment.get("consent_id"),
                        appointment.get("sync_status", "pending"),
                        last_synced_at,
                    ),
                )
            print(f"  ✓ Seeded {len(data['appointments'])} appointment(s)")

    # seed RAG sources and documents (only if not seeding specific table)
    if table is None:
        if data.get("sources"):
            seed_rag_sources(data["sources"])
        if data.get("documents"):
            seed_rag_documents(data["documents"])

    print("✓ Seeding completed")


def seed_rag_sources(sources: list):
    """seed document sources for RAG provenance tracking."""
    print("Seeding RAG sources...")

    stored_count = 0
    for source in sources:
        try:
            store_source(
                source_id=source["source_id"],
                name=source["name"],
                source_type=source["source_type"],
                country_context_id=source.get("country_context_id"),
                version=source.get("version"),
                url=source.get("url"),
                publisher=source.get("publisher"),
                effective_date=source.get("effective_date"),
                metadata=source.get("metadata"),
            )
            print(f"  ✓ Stored source: {source['name']}")
            stored_count += 1
        except Exception as e:
            print(f"  ✗ Error storing source {source['name']}: {e}")

    print(f"  ✓ Seeded {stored_count} RAG source(s)")


def seed_rag_documents(documents: list):
    """seed healthcare documents for RAG."""
    print("Seeding RAG documents...")

    stored_count = 0
    for doc in documents:
        try:
            document_id = store_document(
                title=doc["title"],
                content=doc["content"],
                content_type=doc["content_type"],
                source_id=doc.get("source_id"),
                section_path=doc.get("section_path"),
                country_context_id=doc.get("country_context_id"),
                conditions=doc.get("conditions"),
                metadata=doc.get("metadata"),
            )
            print(f"  ✓ Stored: {doc['title']}")
            stored_count += 1
        except Exception as e:
            print(f"  ✗ Error storing {doc['title']}: {e}")

    print(f"  ✓ Seeded {stored_count} RAG document(s)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="seed database with seed data")
    parser.add_argument("--file", default="demo.json", help="seed file name")
    parser.add_argument(
        "--clear", action="store_true", help="clear existing data before seeding"
    )
    parser.add_argument(
        "--table",
        choices=["users", "interactions", "consents", "providers", "appointments"],
        help="seed only a specific table",
    )

    args = parser.parse_args()
    seed_all(args.file, args.clear, args.table)
