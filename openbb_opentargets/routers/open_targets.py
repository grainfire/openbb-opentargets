"""Open Targets Platform router."""

# pylint: disable=unused-argument

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="")


@router.command(
    model="OpenTargetsSearch",
    examples=[
        APIEx(parameters={"query": "TP53", "provider": "opentargets"}),
        APIEx(
            parameters={
                "query": "rheumatoid arthritis",
                "entity": "disease",
                "provider": "opentargets",
            }
        ),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Free-text search across targets, diseases, and drugs."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TargetAssociatedDiseases",
    examples=[
        APIEx(parameters={"query": "TP53", "provider": "opentargets"}),
        APIEx(
            parameters={
                "query": "ENSG00000141510",
                "limit": 50,
                "provider": "opentargets",
            }
        ),
    ],
)
async def target_associated_diseases(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Diseases associated with a target, ranked by overall association score."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="DiseaseAssociatedTargets",
    examples=[
        APIEx(
            parameters={
                "query": "rheumatoid arthritis",
                "provider": "opentargets",
            }
        ),
        APIEx(
            parameters={
                "query": "EFO_0000685",
                "limit": 50,
                "provider": "opentargets",
            }
        ),
    ],
)
async def disease_associated_targets(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Targets associated with a disease, ranked by overall association score."""
    return await OBBject.from_query(Query(**locals()))
