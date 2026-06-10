# Stage 3A Validation Summary

- Overall validation: **PASS**
- Checks passed: 15/15

| check | status | detail |
|---|---|---|
| Refined maneuver table exists | PASS | data/processed/maneuvers_v1_refined_fixed.parquet |
| Loss metrics table exists | PASS | data/processed/maneuver_loss_metrics.parquet |
| Stage 2B candidate table exists | PASS | data/processed/stage2b_demo_candidates.parquet |
| All-maneuver review index exists and is non-empty | PASS | rows=1336 |
| Row count equals refined maneuver table row count | PASS | index=1336, refined=1336 |
| maneuver_id is unique | PASS | unique=1336 |
| Maneuver 413 exists | PASS | primary demo case |
| Maneuver 413 has final card available | PASS | outputs/demo_case_413/coach_loss_card.md |
| At least one team exists | PASS | teams=13 |
| At least one candidate tack exists when present in source | PASS | source_present=True, output_present=True |
| At least one candidate gybe exists when present in source | PASS | source_present=True, output_present=True |
| At least one mark rounding exists when present in source | PASS | source_present=True, output_present=True |
| No output file exceeds 10 MB | PASS | files=[] |
| Generated markdown uses accepted review language | PASS | hits=[] |
| No model artifacts are created | PASS | new=[] |

Stage 3A creates a compact analyst review index and does not create model artifacts.
