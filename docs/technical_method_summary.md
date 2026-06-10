# Technical Method Summary

FoilBrief is designed to be understandable to judges and useful to analysts. The main story is not a black-box model. It is an auditable telemetry workflow that turns race data into a focused maneuver review pack.

## Data Foundation

The pipeline starts from SailGP boat telemetry, mark files, and cleaned race metadata. Telemetry is sampled at 1 Hz and includes speed, VMG, GPS position, heading, TWA, yaw rate, and boat-control signals.

## Canonical Race ID Fix

The raw race folder label, such as `Race_2`, appears in more than one location. FoilBrief creates a `canonical_race_id`, such as `Bermuda_Race_2`, so Bermuda and Halifax rows never mix in the same analysis group.

## Maneuver Detection

Stage 1 builds maneuver windows from yaw-rate peaks and mark-rounding evidence. Stage 1B keeps every original maneuver row and adds window metrics such as speed drop, VMG drop, TWA change, heading change, yaw peak, data gaps, and pre/post row counts.

## Tack/Gybe Classification

Maneuver labels are rule-based candidate labels. A candidate tack uses upwind TWA side-change evidence plus heading/yaw support. A candidate gybe uses downwind TWA boundary evidence plus heading/yaw support. Sparse or contradictory windows become low-confidence turns.

## Fleet Median Baseline

Stage 2 compares each maneuver with peer maneuver fingerprints from the same `canonical_race_id`. The target team and boat are excluded. Baselines are labeled high, medium, or low confidence based on sample support.

## Conservative Hybrid VMG Handling

Signed VMG can flip polarity depending on course direction and side. Stage 2B audits signed VMG and uses speed-first plus absolute-VMG magnitude for the demo review signal.

## Maneuver Loss Metrics

FoilBrief computes fleet-relative speed separation, absolute-VMG separation, time below the fleet median, and recovery-window status. These metrics are review signals for triage, not measured elapsed-time attribution.

## Demo Triage Score

The internal queue score ranks high-confidence candidates using normalized speed separation, absolute-VMG separation, time below fleet speed, and recovery status. Low-confidence rows are retained in data outputs but excluded from primary demo selection.

## Coach Loss Card Generation

Stage 3 generates the final assets for maneuver 413: map context, fingerprint, telemetry semantics, estimated component waterfall, demo panel, JSON summaries, Time Loss Receipt, and Coach Loss Card. The card explains what telemetry suggests and what the coach may review next.
