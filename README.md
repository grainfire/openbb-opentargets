# openbb-opentargets

An [OpenBB Platform](https://docs.openbb.co/platform) extension that exposes the
[Open Targets Platform v4 GraphQL API](https://platform-docs.opentargets.org/data-access/graphql-api)
under the `obb.open_targets` namespace.

No API key is required — the Open Targets Platform API is fully public.

## Endpoints

| Command | Description |
| --- | --- |
| `obb.open_targets.search` | Free-text search across targets, diseases, and drugs. Returns typed hits with stable IDs. |
| `obb.open_targets.target_associated_diseases` | Diseases associated with a target, ranked by overall score, with per-datatype evidence scores. |
| `obb.open_targets.disease_associated_targets` | Targets associated with a disease, ranked by overall score, with per-datatype evidence scores. |

The two association endpoints accept **either** a stable ID (e.g.
`ENSG00000141510`, `EFO_0000685`) **or** a free-text name (e.g. `TP53`,
`rheumatoid arthritis`). If a name is passed, the fetcher calls Open Targets'
`search` query first and uses the top-ranked hit, costing one extra GraphQL
request. When a stable ID is passed, resolution is skipped entirely.

## Per-datatype evidence columns

Each association row includes the Open Targets per-datatype breakdown as
individual columns — useful for understanding *why* a given association is
strong:

- `genetic_association`
- `somatic_mutation`
- `known_drug`
- `affected_pathway`
- `rna_expression`
- `literature`
- `animal_model`

## Install

```bash
pip install -e .
openbb-build  # regenerates the static obb.* interface
```

Or straight from the GitHub tarball (useful for Dockerfiles without git):

```bash
pip install https://github.com/grainfire/openbb-opentargets/archive/refs/heads/main.tar.gz
```

## Usage

### Python

```python
from openbb import obb

# Free-text discovery
hits = obb.open_targets.search(query="TP53", provider="opentargets").to_df()

# Diseases linked to TP53, ranked by association score
diseases = obb.open_targets.target_associated_diseases(
    query="TP53", limit=50, provider="opentargets"
).to_df()

# Targets linked to rheumatoid arthritis
targets = obb.open_targets.disease_associated_targets(
    query="rheumatoid arthritis", limit=50, provider="opentargets"
).to_df()
```

### REST API

```
GET /api/v1/open_targets/search?query=TP53&provider=opentargets
GET /api/v1/open_targets/target_associated_diseases?query=TP53&provider=opentargets
GET /api/v1/open_targets/disease_associated_targets?query=EFO_0000685&provider=opentargets
```

## Charting

When `openbb-charting` is installed, both association endpoints render a
horizontal bar chart of the top 25 rows by `overall_score`. For a richer
view, the per-datatype columns on the raw rows make it trivial to pivot into
a target×datatype heatmap — the canonical Open Targets visualization.

## Implementation notes

- All HTTP calls go through `openbb_core.provider.utils.helpers.make_request`
  (the sync helper). Open Targets accepts both sync and async clients fine,
  but sync keeps this package's behaviour consistent with its sibling
  `openbb-clinicaltrials`.
- GraphQL errors are raised as `RuntimeError` with the upstream error body.
- ID detection uses simple regex: `^ENSG\d+$` for target passthrough,
  `^[A-Z]+_\d+$` for disease passthrough. Anything else triggers a
  `search` lookup restricted to the relevant entity type.

## License

AGPL-3.0-only, matching the OpenBB Platform.
