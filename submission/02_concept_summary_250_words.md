# FoilBrief Concept Summary

FoilBrief turns SailGP telemetry into a coach-ready race review workflow for SailGP performance analysts and coaches. After a race, the product scans maneuver candidates and presents all-maneuver coverage in one review queue, helping the analyst find moments worth reviewing before the next race.

The single-page workspace ranks internal review queue signals derived from fleet-relative telemetry evidence and lets the analyst filter by venue, race, team, maneuver type, and priority. Selecting a candidate reveals maneuver-level evidence, including speed and absolute-VMG separation, recovery behavior, confidence, and supplementary environment context. The richer curated Demo 413 adds a visual telemetry panel, Time Loss Receipt, and Coach Loss Card that turn evidence into a focused coaching conversation.

Saga, the safe Coach Analyst Agent, can use an optional provider to generate a concise brief grounded only in the selected local evidence. Deterministic checks refuse unsupported weather attribution and prescriptive boat-setting requests, while a grounded fallback keeps the workflow available.

FoilBrief reports estimated review signals rather than measured elapsed-time findings. SailGP telemetry remains the primary evidence; environment data is supporting context. The human analyst makes the final decision.
