# Time Loss Receipt: Maneuver 413

## What Was Measured

Aligned ITA telemetry was compared with the same-race fleet median from -10 to +30 seconds around the candidate gybe. Speed and absolute VMG magnitude are the primary evidence.

## Estimated Triage Components

| Component | Raw evidence | Normalized points |
|---|---:|---:|
| Speed separation | 670.279 | 40.22 |
| Absolute VMG separation | 730.433 | 29.22 |
| Recovery delay | unrecovered within +30s | 15.00 |
| Review uncertainty deduction | VMG polarity and unrecovered-window caution | -7.07 |
| **Net estimated review signal** |  | **77.36** |

Formula: `45*min(speed_area/750,1) + 30*min(abs_vmg_area/750,1) + recovery_signal - uncertainty_deduction`.

## Interpretation

This receipt is a normalized triage signal for review, not a measured elapsed-time attribution and not evidence of causation. The unrecovered window and VMG polarity require manual review.

## Claims To Avoid

Do not present the normalized components as measured seconds, do not attribute the separation to one telemetry variable, and do not present the review signal as a coaching decision.
