"""test ORM setup and basic operations."""

import sys
from pathlib import Path

# add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.postgres.connection import get_db_session, test_connection
from src.infrastructure.postgres.models import Provider, Source, Document
from sqlalchemy import select


def test_connection_pool():
    """test basic database connection."""
    print("testing database connection...")
    result = test_connection()
    if result.get("connected"):
        print(f"  ✓ connected to database: {result['database']}")
        print(f"  ✓ postgres version: {result['postgres_version']}")
        return True
    else:
        print(f"  ✗ connection failed: {result.get('error')}")
        return False


def test_orm_session():
    """test ORM session creation."""
    print("\ntesting ORM session...")
    try:
        with get_db_session() as session:
            # simple query to verify session works
            result = session.execute(select(1)).scalar()
            assert result == 1
            print("  ✓ ORM session working")
            return True
    except Exception as e:
        print(f"  ✗ ORM session failed: {e}")
        return False


def test_model_queries():
    """test basic ORM model queries."""
    print("\ntesting ORM model queries...")
    try:
        with get_db_session() as session:
            # test provider query
            provider_count = session.query(Provider).count()
            print(f"  ✓ providers table: {provider_count} records")
            
            # test source query
            source_count = session.query(Source).count()
            print(f"  ✓ sources table: {source_count} records")
            
            # test document query
            document_count = session.query(Document).count()
            print(f"  ✓ documents table: {document_count} records")
            
            return True
    except Exception as e:
        print(f"  ✗ model queries failed: {e}")
        return False


def test_repository_compatibility():
    """test that repositories still work with ORM."""
    print("\ntesting repository compatibility...")
    try:
        from src.infrastructure.postgres.repositories.providers import search_providers
        from src.infrastructure.postgres.repositories.sources import get_sources_by_country
        from src.infrastructure.postgres.repositories.documents import get_documents_by_source
        
        # these should not raise exceptions even if they return empty results
        result1 = search_providers(limit=1)
        result2 = get_sources_by_country()
        result3 = get_documents_by_source("00000000-0000-0000-0000-000000000000")
        
        print("  ✓ repositories work with ORM")
        return True
    except Exception as e:
        print(f"  ✗ repository compatibility failed: {e}")
        return False


def main():
    """run all ORM tests."""
    print("=" * 60)
    print("ORM MIGRATION VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_connection_pool,
        test_orm_session,
        test_model_queries,
        test_repository_compatibility,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ✗ test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ ORM migration verified successfully!")
        return 0
    else:
        print("\n✗ some tests failed - please review")
        return 1


if __name__ == "__main__":
    sys.exit(main())
