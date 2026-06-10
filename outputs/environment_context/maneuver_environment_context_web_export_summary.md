# Maneuver Environment Context Web Export Audit

- Source: `data/processed/coach_card_environment_join.parquet`
- Source rows: 1336
- Source maneuver IDs: 1336
- Duplicate source maneuver rows removed: 0
- Exported maneuver IDs: 1336
- Maneuvers with environment context available: 1336
- CSV: `outputs/environment_context/maneuver_environment_context_web.csv`
- JSON: `outputs/environment_context/maneuver_environment_context_web.json`

The export contains lightweight review fields only. It excludes raw API payloads, cache paths, large arrays, and parquet artifacts.

SailGP telemetry remains the primary evidence. External environment data is context for coach review and is not a causal attribution.
