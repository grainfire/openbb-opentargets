"""Open Targets Platform OpenBB Provider."""

from openbb_core.provider.abstract.provider import Provider

from openbb_opentargets.providers.opentargets.models.disease_associated_targets import (
    DiseaseAssociatedTargetsFetcher,
)
from openbb_opentargets.providers.opentargets.models.search import (
    OpenTargetsSearchFetcher,
)
from openbb_opentargets.providers.opentargets.models.target_associated_diseases import (
    TargetAssociatedDiseasesFetcher,
)

opentargets_provider = Provider(
    name="opentargets",
    description="Provider for the Open Targets Platform v4 GraphQL API.",
    website="https://platform.opentargets.org",
    fetcher_dict={
        "OpenTargetsSearch": OpenTargetsSearchFetcher,
        "TargetAssociatedDiseases": TargetAssociatedDiseasesFetcher,
        "DiseaseAssociatedTargets": DiseaseAssociatedTargetsFetcher,
    },
)
