# standards/ — tracked canon (never gitignored)

**Rule:** if the build reads it, tests against it, or must obey it, it lives here (or as `src/` package data). Working notes and drafts stay out of the repo.

- `ontology/` — working graphs (`risk.ttl`, `sites.ttl`, `risk_instance_pe_asset.ttl`). CI benchmark: core composes to 263 triples; +instance = 325 (`tests/test_standards_ontology.py`).
- `rules/` — system rules all agents and developers must obey.
