# Safety, Limitations, And Human Decision

## Product Boundary

- FoilBrief is post-race decision support, not autonomous boat control.
- It prioritizes review candidates and summarizes evidence; it does not make the coaching decision.
- It does not issue prescriptive boat-setting instructions.
- The human analyst makes the final decision.

## Evidence Boundary

- Fleet-relative review signals are estimated triage aids, not exact time loss or measured seconds lost.
- Maneuver labels are candidate labels, not guaranteed ground-truth labels.
- Same-race fleet medians are comparison references, not optimal reference paths.
- Recovery status is limited to the available review window.
- Only curated Demo 413 has the full visual evidence bundle, Time Loss Receipt, and Coach Loss Card. Other maneuvers show index-level evidence and environment context.

## Environment Boundary

- SailGP telemetry remains the primary evidence.
- Open-Meteo reanalysis is supplementary environment context.
- Environment estimates include availability, resolution, and confidence limitations.
- FoilBrief does not make weather attribution.

## Saga Safety

- Saga answers only from selected local evidence and allowed environment context.
- Deterministic checks refuse unsupported attribution and prescriptive boat-setting requests.
- Generated responses are checked before display.
- A deterministic grounded fallback is used when the model is unavailable or a response fails safety checks.

## Forbidden Product Wording

Normal product claims must not use unsupported certainty, weather attribution, exactness, or prescriptive control wording. The safe-refusal demonstration intentionally tests this boundary.

Human analyst makes the final decision.
