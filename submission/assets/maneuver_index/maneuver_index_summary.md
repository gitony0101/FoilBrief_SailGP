# All-Maneuver Review Index Summary

- Total candidate maneuvers: 1,336
- Unique teams: 13
- Total races: 14

## Counts By Maneuver Type

- `gybe`: 267
- `low_confidence_turn`: 540
- `mark_rounding`: 43
- `tack`: 486

## Counts By Review Tier

- `high_review_priority`: 179
- `medium_review_priority`: 534
- `low_review_priority`: 24
- `exclude_from_demo`: 599

## Top 10 Review Candidates

| maneuver_id | canonical_race_id | team | maneuver_type | demo_triage_score | review_tier | recommended_use |
|---|---|---|---|---|---|---|
| 413 | Bermuda_Race_2 | ITA | gybe | 0.976 | high_review_priority | primary_demo |
| 238 | Halifax_Race_1 | USA | gybe | 0.975 | high_review_priority | candidate_review |
| 1051 | Bermuda_Race_6 | DEN | gybe | 0.972 | high_review_priority | candidate_review |
| 1 | Halifax_Race_1 | AUS | gybe | 0.966 | high_review_priority | candidate_review |
| 1238 | Bermuda_Race_7 | GBR | gybe | 0.963 | high_review_priority | candidate_review |
| 40 | Halifax_Race_1 | CAN | gybe | 0.960 | high_review_priority | candidate_review |
| 661 | Halifax_Race_4 | DEN | tack | 0.959 | high_review_priority | candidate_review |
| 612 | Halifax_Race_4 | AUS | tack | 0.958 | high_review_priority | candidate_review |
| 1268 | Bermuda_Race_7 | SUI | tack | 0.954 | high_review_priority | candidate_review |
| 528 | Bermuda_Race_3 | DEN | tack | 0.951 | high_review_priority | candidate_review |

## Review Workflow

FoilBrief detects every `maneuver_id` in the accepted refined maneuver table and attaches available fleet-relative scoring evidence before the analyst selects a deep-dive case.
Maneuver `413` remains the single designated deep-dive demo case and links to its Coach Loss Card.
Review scores are internal review queue signals derived from fleet-relative telemetry evidence, not measured elapsed-time attribution. The human analyst decides which candidate maneuver is worth further review.
