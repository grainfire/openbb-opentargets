"""Open Targets Platform GraphQL helpers."""

import re
from typing import Any

from openbb_core.provider.utils.helpers import make_request

GRAPHQL_URL = "https://api.platform.opentargets.org/api/v4/graphql"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
}

_ENSEMBL_RE = re.compile(r"^ENSG\d+$")
_ONTOLOGY_RE = re.compile(r"^[A-Z]+_\d+$")

DATATYPE_COLUMNS = [
    "genetic_association",
    "somatic_mutation",
    "known_drug",
    "affected_pathway",
    "rna_expression",
    "literature",
    "animal_model",
]


def graphql_request(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    """POST a GraphQL query and return the ``data`` payload."""
    response = make_request(
        GRAPHQL_URL,
        method="POST",
        headers=_HEADERS,
        json={"query": query, "variables": variables},
    )
    response.raise_for_status()
    payload = response.json()
    if "errors" in payload and payload["errors"]:
        raise RuntimeError(f"Open Targets GraphQL error: {payload['errors']}")
    return payload.get("data") or {}


_SEARCH_QUERY = """
query Search($q: String!, $entity: [String!]) {
  search(queryString: $q, entityNames: $entity, page: {index: 0, size: 1}) {
    hits { id entity name }
  }
}
"""


def resolve_target_id(query: str) -> str | None:
    """Return an Ensembl gene ID for ``query`` (passthrough or search lookup)."""
    query = query.strip()
    if _ENSEMBL_RE.fullmatch(query):
        return query
    data = graphql_request(_SEARCH_QUERY, {"q": query, "entity": ["target"]})
    hits = ((data.get("search") or {}).get("hits")) or []
    return hits[0]["id"] if hits else None


def resolve_disease_id(query: str) -> str | None:
    """Return an ontology disease ID (EFO_, MONDO_, etc.) for ``query``."""
    query = query.strip()
    if _ONTOLOGY_RE.fullmatch(query) and not _ENSEMBL_RE.fullmatch(query):
        return query
    data = graphql_request(_SEARCH_QUERY, {"q": query, "entity": ["disease"]})
    hits = ((data.get("search") or {}).get("hits")) or []
    return hits[0]["id"] if hits else None


def flatten_datatype_scores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Lift ``datatypeScores`` array into one column per known datatype."""
    for row in rows:
        scores = {s["id"]: s["score"] for s in (row.pop("datatypeScores", None) or [])}
        for col in DATATYPE_COLUMNS:
            row[col] = scores.get(col)
    return rows
