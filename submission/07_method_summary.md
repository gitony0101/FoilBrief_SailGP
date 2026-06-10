# Judge-Facing Method Summary

FoilBrief is an auditable post-race review workflow. The method is designed to help a SailGP performance analyst move from a full race dataset to a focused coaching conversation.

## Maneuver Candidate Ranking

FoilBrief scans SailGP challenge telemetry for candidate tacks, gybes, mark roundings, and lower-confidence turns. The current Fleet Review Index covers 1,336 candidates across 13 teams and 14 races. A queue score orders candidates for review; it does not determine the coaching conclusion.

## Fleet-Relative Review Signals

Each supported candidate is compared with a same-race fleet median that excludes the selected boat. FoilBrief surfaces estimated speed separation, absolute-VMG separation, time below fleet reference signals, recovery behavior, and confidence. These values are fleet-relative review signals for triage, not measured elapsed-time findings.

## Maneuver-Level Evidence

Selecting any queue row opens matching index-level evidence in the single-page workspace. Analysts can inspect Overview, Telemetry Signals, Environment, and Coach Focus tabs. Demo 413 is the separate curated deep dive with an audited visual panel, Time Loss Receipt, and structured Coach Loss Card.

The Time Loss Receipt organizes estimated signal components and uncertainty. The Coach Loss Card translates the evidence into what telemetry suggests, key evidence, caveats, and coach review focus.

## Environment Context

Open-Meteo reanalysis is shown as supplementary environment context with availability and confidence information. SailGP telemetry remains the primary evidence, and FoilBrief does not use environment context for weather attribution.

## Saga Coach Analyst Agent

Saga converts the selected evidence into a concise coach-ready brief. An optional provider can be used when provider mode is enabled. Otherwise, FoilBrief returns a deterministic grounded response.

## Deterministic Safety And Fallback

Deterministic request checks refuse unsupported attribution and prescriptive boat-setting requests before generation. Generated responses are checked again; an unsafe or unavailable model response is replaced by a grounded deterministic fallback. The human analyst makes the final decision.
