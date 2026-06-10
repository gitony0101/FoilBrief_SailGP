# FoilBrief Three-Minute Video Script

**Target runtime:** 2:50-3:00

## 0:00-0:15 | The Product

**Visual:** FoilBrief title, then Review Index.

**Narration:**  
SailGP teams have dense telemetry and very little time between races. FoilBrief turns that data into a ranked, coach-ready maneuver review workflow, so analysts can quickly find the moments most worth reviewing.

## 0:15-0:40 | Review Index

**Visual:** Filter and scan the Review Index.

**Narration:**  
FoilBrief scans all detected tacks, gybes, and mark roundings. Here, the Review Index organizes 1,336 candidate maneuvers across 13 teams and 14 races. Each row shows confidence, an internal review queue signal derived from fleet-relative telemetry evidence, and recommended use. The analyst can filter the queue, inspect the evidence, and choose the deep dive. The human makes the final decision.

## 0:40-1:30 | Demo 413

**Visual:** Open maneuver 413; show race map, maneuver fingerprint, telemetry, and coach card.

**Narration:**  
Let’s open maneuver 413, an ITA candidate gybe near LG2 in Bermuda Race 2. The map establishes where it happened. The heading, true wind angle, and yaw transition support the candidate-gybe label.

The visual fingerprint compares ITA with a same-race fleet median that excludes ITA. Telemetry suggests persistent fleet-relative speed and absolute-VMG separation after the maneuver. The boat remains below fleet speed for 41 seconds and does not recover within the plus-30-second review window.

These are estimated review signals, not measured elapsed-time attribution. FoilBrief turns them into a focused review question: inspect speed build and absolute-VMG recovery in the first 10 to 30 seconds after the gybe.

## 1:30-2:00 | Maneuver 636 And Environment Context

**Visual:** Open maneuver 636 and its environment context.

**Narration:**  
Maneuver 636 shows how FoilBrief adds context without overclaiming. SailGP telemetry remains the primary evidence. Open-Meteo reanalysis is shown only as supplementary environment context, with separate confidence and availability caveats. It may support the analyst’s interpretation of recovery conditions, but it is not a weather attribution.

## 2:00-2:35 | Coach Analyst Agent

**Visual:** Ask a safe evidence question; show grounded answer.

**Narration:**  
The Coach Analyst Agent can use an optional provider as a narration layer over a compact, audited evidence packet. Ask what telemetry suggests, and it produces a concise brief grounded in the selected maneuver, fleet-relative evidence, confidence, and caveats. It cannot fill missing evidence, and every accepted response leaves the final decision with the human analyst.

## 2:35-2:50 | Safe Refusal

**Visual:** Ask for weather attribution or a prescriptive equipment instruction; show refusal.

**Narration:**  
Ask it to attribute the result to weather or prescribe an equipment instruction, and FoilBrief refuses before calling the model. Generated answers are also checked, with a deterministic safe fallback if needed.

## 2:50-3:00 | Close

**Visual:** Return to Review Index and FoilBrief title.

**Narration:**  
FoilBrief moves teams from a race full of telemetry to one clear coaching conversation: what is worth analyst review, what the evidence says, and where the human should look next.

## Recording Notes

- Keep the Review Index visible long enough for judges to see the ranked workflow.
- Do not read raw metric values beyond the two clear maneuver 413 facts.
- Show maneuver 636 only to demonstrate supplementary environment context.
- Show one grounded agent answer and one safe refusal.
- End before 3:00.
