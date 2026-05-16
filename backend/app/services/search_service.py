"""OpenSearch integration for opportunity search."""

import logging
from typing import Any

try:
    from opensearchpy import AsyncOpenSearch
except ImportError:
    from opensearchpy._async import AsyncOpenSearch

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchService:
    """Manages opportunity indexing and search via OpenSearch.

    Provides full-text search, faceted filtering, and semantic search
    capabilities for internship opportunities.
    """

    def __init__(self) -> None:
        self._client: AsyncOpenSearch | None = None

    async def _get_client(self) -> AsyncOpenSearch:
        """Lazy-initialize the OpenSearch client."""
        if self._client is None:
            self._client = AsyncOpenSearch(
                hosts=[settings.OPENSEARCH_URL],
                http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
                use_ssl=True,
                verify_certs=False,
                ssl_show_warn=False,
            )
        return self._client

    async def ensure_index(self) -> None:
        """Create the opportunities index if it doesn't exist."""
        client = await self._get_client()
        index_name = settings.OPENSEARCH_INDEX

        if await client.indices.exists(index=index_name):
            return

        index_body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "opportunity_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"],
                        }
                    }
                },
            },
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "title": {
                        "type": "text",
                        "analyzer": "opportunity_analyzer",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "description": {"type": "text", "analyzer": "opportunity_analyzer"},
                    "sector": {"type": "keyword"},
                    "required_skills": {"type": "keyword"},
                    "location": {"type": "text"},
                    "state": {"type": "keyword"},
                    "district": {"type": "keyword"},
                    "work_mode": {"type": "keyword"},
                    "capacity": {"type": "integer"},
                    "stipend": {"type": "float"},
                    "duration_months": {"type": "integer"},
                    "is_active": {"type": "boolean"},
                    "employer_id": {"type": "integer"},
                }
            },
        }

        await client.indices.create(index=index_name, body=index_body)
        logger.info("Created OpenSearch index: %s", index_name)

    async def index_opportunity(self, opportunity_id: int, data: dict[str, Any]) -> None:
        """Index a single opportunity document."""
        client = await self._get_client()
        await client.index(
            index=settings.OPENSEARCH_INDEX,
            id=str(opportunity_id),
            body=data,
            refresh=True,
        )
        logger.debug("Indexed opportunity %d", opportunity_id)

    async def delete_opportunity(self, opportunity_id: int) -> None:
        """Remove an opportunity from the index."""
        client = await self._get_client()
        try:
            await client.delete(
                index=settings.OPENSEARCH_INDEX,
                id=str(opportunity_id),
                refresh=True,
            )
        except Exception:
            logger.warning("Opportunity %d not found in index", opportunity_id)

    async def search_opportunities(
        self,
        query: str | None = None,
        sector: str | None = None,
        state: str | None = None,
        work_mode: str | None = None,
        skills: list[str] | None = None,
        from_: int = 0,
        size: int = 20,
    ) -> dict[str, Any]:
        """Search opportunities with full-text and faceted filters.

        Args:
            query: Free-text search query.
            sector: Filter by sector.
            state: Filter by state.
            work_mode: Filter by work mode (remote/hybrid/onsite).
            skills: Filter by required skills.
            from_: Pagination offset.
            size: Page size.

        Returns:
            Search results with hits, total count, and aggregations.
        """
        client = await self._get_client()

        must_clauses: list[dict] = []
        filter_clauses: list[dict] = []

        if query:
            must_clauses.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description", "required_skills^2"],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            )

        filter_clauses.append({"term": {"is_active": True}})

        if sector:
            filter_clauses.append({"term": {"sector": sector}})
        if state:
            filter_clauses.append({"term": {"state": state}})
        if work_mode:
            filter_clauses.append({"term": {"work_mode": work_mode}})
        if skills:
            filter_clauses.append({"terms": {"required_skills": skills}})

        search_body: dict[str, Any] = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            },
            "from": from_,
            "size": size,
            "sort": [{"_score": "desc"}, {"created_at": "desc"}],
            "aggs": {
                "sectors": {"terms": {"field": "sector", "size": 20}},
                "states": {"terms": {"field": "state", "size": 50}},
                "work_modes": {"terms": {"field": "work_mode", "size": 5}},
                "avg_stipend": {"avg": {"field": "stipend"}},
            },
        }

        response = await client.search(index=settings.OPENSEARCH_INDEX, body=search_body)

        hits = response.get("hits", {})
        total = hits.get("total", {}).get("value", 0)
        results = [hit["_source"] for hit in hits.get("hits", [])]
        aggs = response.get("aggregations", {})

        return {
            "total": total,
            "results": results,
            "aggregations": aggs,
        }

    async def close(self) -> None:
        """Close the OpenSearch client connection."""
        if self._client:
            await self._client.close()
            self._client = None
