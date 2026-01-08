"""postgres repositories package (keep imports lazy).

Import repository modules directly to avoid loading database engines unless
needed, e.g.:
```
from src.infrastructure.postgres.repositories.documents import search_documents_by_embedding
```
"""
