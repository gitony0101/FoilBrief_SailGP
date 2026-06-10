# Three-Minute Video Script

Target duration: maximum 3 minutes
Demo URL: `https://foil-brief-sail-gp-hackathon.vercel.app`

## 0:00-0:25 | Problem And Product

**Screen:** Open the production homepage and hold on the hero.

**Narration:**  
SailGP teams collect dense telemetry, but analysts and coaches have limited time to decide what deserves review before the next race. FoilBrief turns that telemetry into a coach-ready review workflow. It scans maneuver candidates, ranks fleet-relative review signals, presents the evidence, and helps the human analyst focus the next coaching conversation.

## 0:25-1:00 | Single-Page Fleet Review Queue

**Screen:** Scroll to Fleet Review Index. Show scope metrics, filters, priority distribution, and pagination.

**Narration:**  
The latest FoilBrief workspace starts with all-maneuver coverage: 1,336 candidates across 13 teams and 14 races. The analyst can search by maneuver ID, filter by venue, race, team, type, or priority, and sort by review signal, speed separation, or absolute-VMG separation. The queue keeps high, medium, low, and excluded candidates visible, so the analyst can see coverage rather than only a polished example. Selecting any row updates the evidence workspace below. This is a review queue, not an automated coaching verdict.

## 1:00-1:30 | Selected Evidence And Environment

**Screen:** Select a queue row and click Overview, Telemetry Signals, Environment, and Coach Focus.

**Narration:**  
For each selection, FoilBrief shows maneuver-level index evidence: the fleet-relative review signal, speed and VMG separation, confidence, recovery information, and coach review focus. The evidence boundary is explicit: most candidates have index-level evidence, while the richer audited visual bundle belongs to curated Demo 413. Environment information is shown only as supplementary context. SailGP telemetry remains the primary evidence.

## 1:30-2:10 | Curated Demo 413

**Screen:** Click Open Demo 413 Deep Dive. Show the audited visual panel, Time Loss Receipt, Environment Context, and Coach Loss Card.

**Narration:**  
Maneuver 413 is the curated deep dive: an ITA candidate gybe near LG2 in Bermuda Race 2. Telemetry suggests persistent fleet-relative speed and absolute-VMG separation after the maneuver, making recovery worth analyst review. The Time Loss Receipt organizes estimated review-signal components and uncertainty. The Coach Loss Card summarizes what telemetry suggests, key evidence, caveats, and coach review focus. It directs attention to the recovery window without prescribing the coaching conclusion. These are estimated triage aids, not measured elapsed-time findings.

## 2:10-2:42 | Saga Coach Analyst Agent

**Screen:** Return to the homepage. Select maneuver 636. Ask: `Why is maneuver 636 worth reviewing?`

**Narration:**  
Saga is FoilBrief’s safe Coach Analyst Agent. When enabled, an optional provider generates a concise brief grounded only in selected local evidence. Otherwise, a deterministic grounded fallback remains available. A maneuver ID in the question selects that maneuver’s evidence, and every response keeps the human decision boundary visible.

## 2:42-2:55 | Safe Refusal

**Screen:** Ask: `Was maneuver 636 caused by the weather?`

**Narration:**  
When asked for unsupported weather attribution, Saga refuses through a deterministic guardrail and redirects the analyst to fleet-relative telemetry evidence and environment context.

## 2:55-3:00 | Close

**Screen:** Return to the fleet review workspace and human-decision statement.

**Narration:**  
FoilBrief moves teams from telemetry overload to focused coach review. Human analyst makes the final decision.
