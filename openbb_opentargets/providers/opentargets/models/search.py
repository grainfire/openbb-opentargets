"""Open Targets free-text search fetcher."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_opentargets.providers.opentargets.utils.helpers import graphql_request

_QUERY = """
query Search($q: String!, $entity: [String!], $size: Int!) {
  search(queryString: $q, entityNames: $entity, page: {index: 0, size: $size}) {
    hits {
      id
      entity
      name
      description
      score
    }
    total
  }
}
"""


class OpenTargetsSearchQueryParams(QueryParams):
    """Query parameters for Open Targets search."""

    query: str = Field(description="Free-text search string (gene, disease, or drug).")
    entity: str | None = Field(
        default=None,
        description=(
            "Restrict to a single entity type: target, disease, or drug. "
            "Leave unset to search all three."
        ),
    )
    limit: int = Field(default=25, ge=1, le=100, description="Max number of hits.")


class OpenTargetsSearchData(Data):
    """A single search hit."""

    id: str = Field(description="Stable identifier (Ensembl gene / EFO / ChEMBL).")
    entity: str = Field(description="Entity kind: target, disease, or drug.")
    name: str | None = Field(default=None, description="Display name.")
    description: str | None = Field(
        default=None, description="Short description if available."
    )
    score: float | None = Field(default=None, description="Search relevance score.")


class OpenTargetsSearchFetcher(
    Fetcher[OpenTargetsSearchQueryParams, list[OpenTargetsSearchData]]
):
    """Fetcher for the Open Targets Platform ``search`` query."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OpenTargetsSearchQueryParams:
        return OpenTargetsSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: OpenTargetsSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        entity = [query.entity] if query.entity else ["target", "disease", "drug"]
        data = graphql_request(
            _QUERY,
            {"q": query.query, "entity": entity, "size": query.limit},
        )
        return ((data.get("search") or {}).get("hits")) or []

    @staticmethod
    def transform_data(
        query: OpenTargetsSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OpenTargetsSearchData]:
        return [OpenTargetsSearchData.model_validate(row) for row in data]
