# Coach Loss Card

## Header

- Race: Bermuda_Race_2
- Team: ITA
- Maneuver: candidate gybe
- Maneuver ID: 413
- Context: near mark LG2

## Estimated Review Signal

- Internal queue score: 0.976
- Normalized review signal: 77.36
- Speed separation: 670.279
- Absolute VMG separation: 730.433
- Recovery status: unrecovered within +30s review window
- Confidence: high baseline / high loss
- Risk flags: unrecovered window; signed VMG polarity caveat

## What Telemetry Suggests

The boat showed persistent speed and absolute-VMG separation from the fleet median after the candidate gybe window. The maneuver did not recover within the review window. This makes the post-gybe recovery phase worth analyst review.

## Evidence

| Metric | Value |
|---|---:|
| speed_drop_window | 26.185 |
| vmg_drop_window | -1.580 |
| relative_speed_loss_area | 670.279 |
| abs_relative_vmg_loss_area | 730.433 |
| time_below_fleet_speed | 41 |
| time_below_fleet_vmg | 3 |
| recovery_time_to_90 | unrecovered within window |
| recovery_time_to_95 | unrecovered within window |
| baseline_sample_count_median | 7 |
| baseline_confidence | high |
| loss_confidence | high |

## Coach Review Focus

- Review the first 10 to 30 seconds after the candidate gybe.
- Compare speed build and absolute VMG recovery against the fleet median.
- Check whether wing trim, rudder angle, or foil/rake signals show delayed stabilization if available. Treat these as review signals only.

## Caveats

- Estimated fleet-relative review signal, not a measured elapsed-time attribution.
- Signed VMG has polarity caveats; absolute VMG magnitude is used for safer demo evidence.
- Requires human analyst review before any coaching decision.
