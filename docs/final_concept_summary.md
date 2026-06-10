# FoilBrief Concept Summary

**Word count: 211**

FoilBrief turns SailGP telemetry into a coach-ready maneuver review workflow. Built for SailGP performance analysts and coaches, it answers a practical post-race question: which maneuver windows are most worth reviewing before the next race?

Using SailGP 1 Hz boat telemetry, mark positions, and race metadata, FoilBrief scans detected tacks, gybes, and mark roundings, then ranks them using internal review queue signals derived from fleet-relative telemetry evidence. Analysts can move from a full review index into a visual workspace showing race position, speed, VMG, recovery behavior, confidence, and comparison with a same-race fleet median that excludes the selected boat.

The primary demo, maneuver 413, shows how telemetry suggests persistent fleet-relative speed and absolute-VMG separation after an ITA gybe near LG2 in Bermuda Race 2, making the recovery phase worth analyst review. A second case, maneuver 636, demonstrates how supplementary environment context can support interpretation without being treated as causal.

FoilBrief also includes a safe optional Saga provider Coach Analyst Agent. It converts the supplied evidence into a concise grounded brief, refuses unsupported attribution or prescriptive-control requests, and falls back to a deterministic response when needed.

FoilBrief does not decide on behalf of the team or prescribe controls. It narrows the review queue, explains why a maneuver was flagged, and keeps the human analyst responsible for the final decision.
