"""Open Targets target → associated diseases fetcher."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_opentargets.providers.opentargets.utils.helpers import (
    flatten_datatype_scores,
    graphql_request,
    resolve_target_id,
)

_QUERY = """
query TargetAssociatedDiseases($id: String!, $size: Int!) {
  target(ensemblId: $id) {
    id
    approvedSymbol
    associatedDiseases(page: {index: 0, size: $size}) {
      count
      rows {
        score
        datatypeScores { id score }
        disease { id name therapeuticAreas { name } }
      }
    }
  }
}
"""


class TargetAssociatedDiseasesQueryParams(QueryParams):
    """Query parameters."""

    target: str = Field(
        description=(
            "Target identifier. Accepts an Ensembl gene ID (e.g. ENSG00000141510) "
            "or a free-text gene name (e.g. TP53) which will be resolved via search."
        )
    )
    limit: int = Field(
        default=25, ge=1, le=500, description="Max number of associated diseases."
    )


class TargetAssociatedDiseasesData(Data):
    """A single target → disease association row."""

    target_id: str = Field(description="Ensembl gene ID that was queried.")
    target_symbol: str | None = Field(default=None, description="Approved gene symbol.")
    disease_id: str = Field(description="Ontology disease ID.")
    disease_name: str | None = Field(default=None, description="Disease name.")
    therapeutic_areas: list[str] | None = Field(
        default=None, description="High-level therapeutic area names."
    )
    overall_score: float | None = Field(
        default=None, description="Overall association score (0..1)."
    )
    genetic_association: float | None = None
    somatic_mutation: float | None = None
    known_drug: float | None = None
    affected_pathway: float | None = None
    rna_expression: float | None = None
    literature: float | None = None
    animal_model: float | None = None


class TargetAssociatedDiseasesFetcher(
    Fetcher[
        TargetAssociatedDiseasesQueryParams, list[TargetAssociatedDiseasesData]
    ]
):
    """Fetcher for target → associated-diseases with per-datatype scores."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> TargetAssociatedDiseasesQueryParams:
        return TargetAssociatedDiseasesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TargetAssociatedDiseasesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        ensembl_id = resolve_target_id(query.target)
        if not ensembl_id:
            return []
        data = graphql_request(_QUERY, {"id": ensembl_id, "size": query.limit})
        target = data.get("target") or {}
        assoc = target.get("associatedDiseases") or {}
        rows = assoc.get("rows") or []

        flat: list[dict[str, Any]] = []
        for row in rows:
            disease = row.get("disease") or {}
            flat.append(
                {
                    "target_id": target.get("id") or ensembl_id,
                    "target_symbol": target.get("approvedSymbol"),
                    "disease_id": disease.get("id"),
                    "disease_name": disease.get("name"),
                    "therapeutic_areas": [
                        t.get("name") for t in (disease.get("therapeuticAreas") or []) if t.get("name")
                    ]
                    or None,
                    "overall_score": row.get("score"),
                    "datatypeScores": row.get("datatypeScores"),
                }
            )
        return flatten_datatype_scores(flat)

    @staticmethod
    def transform_data(
        query: TargetAssociatedDiseasesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TargetAssociatedDiseasesData]:
        return [TargetAssociatedDiseasesData.model_validate(r) for r in data]
