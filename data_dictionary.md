# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `source_documents.csv` | source document | Tracks source type, desk, exclusivity level, buyer relevance, and extraction complexity. |
| `company_profiles.csv` | company | Holds synthetic private-company profile attributes used for enrichment. |
| `extracted_signals.csv` | extracted signal | Maps raw intelligence signals to target product schemas with confidence and validation status. |
| `taxonomy_terms.csv` | taxonomy term | Shows controlled vocabulary ownership, schema field mapping, and governance status. |
| `survey_sentiment.csv` | survey cut | Captures recurring sentiment benchmarks by audience, sector, and question theme. |
| `quality_checks.csv` | QA check | Captures field gaps, source conflicts, taxonomy mismatches, and owner SLAs. |
| `analysis/outputs/feed_launch_queue.csv` | feed | Ranked recurring data feed readiness queue. |
| `analysis/outputs/extraction_enrichment_queue.csv` | signal | Analyst queue for validation, enrichment, and schema completion. |
| `analysis/outputs/schema_governance_queue.csv` | feed schema | Schema and taxonomy readiness by target product. |
| `analysis/outputs/client_brief.csv` | feed | Buyer-facing launch rationale, proof points, blockers, and recommendation. |
