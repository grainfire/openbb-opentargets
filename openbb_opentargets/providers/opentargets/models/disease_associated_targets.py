"""Open Targets disease → associated targets fetcher."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_opentargets.providers.opentargets.utils.helpers import (
    flatten_datatype_scores,
    graphql_request,
    resolve_disease_id,
)

_QUERY = """
query DiseaseAssociatedTargets($id: String!, $size: Int!) {
  disease(efoId: $id) {
    id
    name
    associatedTargets(page: {index: 0, size: $size}) {
      count
      rows {
        score
        datatypeScores { id score }
        target { id approvedSymbol approvedName biotype }
      }
    }
  }
}
"""


class DiseaseAssociatedTargetsQueryParams(QueryParams):
    """Query parameters."""

    disease: str = Field(
        description=(
            "Disease identifier. Accepts an ontology ID (e.g. EFO_0000685, "
            "MONDO_0004979) or a free-text disease name, which will be resolved "
            "via search."
        )
    )
    limit: int = Field(
        default=25, ge=1, le=500, description="Max number of associated targets."
    )


class DiseaseAssociatedTargetsData(Data):
    """A single disease → target association row."""

    disease_id: str = Field(description="Ontology disease ID that was queried.")
    disease_name: str | None = Field(default=None, description="Disease name.")
    target_id: str = Field(description="Ensembl gene ID.")
    target_symbol: str | None = Field(default=None, description="Approved gene symbol.")
    target_name: str | None = Field(default=None, description="Approved gene name.")
    biotype: str | None = Field(default=None, description="Gene biotype.")
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


class DiseaseAssociatedTargetsFetcher(
    Fetcher[
        DiseaseAssociatedTargetsQueryParams, list[DiseaseAssociatedTargetsData]
    ]
):
    """Fetcher for disease → associated-targets with per-datatype scores."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> DiseaseAssociatedTargetsQueryParams:
        return DiseaseAssociatedTargetsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: DiseaseAssociatedTargetsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        efo_id = resolve_disease_id(query.disease)
        if not efo_id:
            return []
        data = graphql_request(_QUERY, {"id": efo_id, "size": query.limit})
        disease = data.get("disease") or {}
        assoc = disease.get("associatedTargets") or {}
        rows = assoc.get("rows") or []

        flat: list[dict[str, Any]] = []
        for row in rows:
            target = row.get("target") or {}
            flat.append(
                {
                    "disease_id": disease.get("id") or efo_id,
                    "disease_name": disease.get("name"),
                    "target_id": target.get("id"),
                    "target_symbol": target.get("approvedSymbol"),
                    "target_name": target.get("approvedName"),
                    "biotype": target.get("biotype"),
                    "overall_score": row.get("score"),
                    "datatypeScores": row.get("datatypeScores"),
                }
            )
        return flatten_datatype_scores(flat)

    @staticmethod
    def transform_data(
        query: DiseaseAssociatedTargetsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DiseaseAssociatedTargetsData]:
        return [DiseaseAssociatedTargetsData.model_validate(r) for r in data]
