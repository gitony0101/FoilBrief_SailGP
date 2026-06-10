# FoilBrief Final Slide Outline

## Slide 1 | From Race Telemetry To The Next Coaching Conversation

**Headline:** FoilBrief ranks the maneuver windows most worth analyst review.

**Show:** Product screenshot with Review Index leading into a maneuver workspace.

**Say:** Built for a SailGP performance analyst or coach. Stream: On the Water.

## Slide 2 | The Decision Problem

**Headline:** The constraint is review time, not data availability.

**Show:** Dense telemetry on the left; short between-race review window on the right.

**Key points:**

- Race review requires finding meaningful maneuver windows quickly.
- A generic dashboard still leaves the analyst searching.
- FoilBrief creates a prioritized review queue and explains each review signal.

## Slide 3 | The Product Workflow

**Headline:** Scan, rank, inspect, brief, decide.

**Show:** Five-step workflow:

1. Scan detected maneuvers.
2. Rank internal review queue signals derived from fleet-relative telemetry evidence.
3. Inspect visual telemetry and recovery context.
4. Generate a grounded coach brief.
5. Keep the human final decision.

## Slide 4 | Review Index: Fleet-Wide Triage

**Headline:** One review workflow across 1,336 candidate maneuvers.

**Show:** Review Index screenshot and filters.

**Key facts:**

- 13 teams and 14 races.
- Tacks, gybes, mark roundings, and visible low-confidence candidates.
- Confidence and evidence gates prevent unsupported cases from becoming demo recommendations.

## Slide 5 | Demo 413: Explain Why It Was Flagged

**Headline:** Telemetry suggests the post-gybe recovery is worth analyst review.

**Show:** Race map, fingerprint, and Coach Loss Card for maneuver 413.

**Key facts:**

- ITA candidate gybe near LG2, Bermuda Race 2.
- Same-race fleet median excludes the selected boat.
- Persistent fleet-relative speed and absolute-VMG separation.
- Below fleet speed for 41 seconds; unrecovered in the +30-second review window.
- Estimated review signals, not measured elapsed-time attribution.

## Slide 6 | Context Without Overclaiming

**Headline:** Environment data supports interpretation; SailGP telemetry remains primary.

**Show:** Maneuver 636 environment-aware card.

**Key facts:**

- Supplementary Open-Meteo reanalysis context.
- Separate environment confidence and availability caveats.
- No weather attribution.

## Slide 7 | Safe optional Saga provider Coach Analyst Agent

**Headline:** Grounded narration with refusal and fallback guardrails.

**Show:** Safe question, grounded brief, unsafe question, safe refusal.

**Key facts:**

- Optional optional Saga provider narration over an audited evidence packet.
- Pre-request checks reject unsupported attribution and prescriptive-control requests.
- Post-generation checks discard unsafe output.
- Deterministic grounded fallback remains available.
- Human analyst makes the final decision.

## Slide 8 | Why FoilBrief Matters

**Headline:** Less time searching. More time reviewing the right maneuver.

**Show:** Review Index to Coach Brief transformation.

**Close:** FoilBrief is race performance decision support for SailGP teams, not a generic analytics dashboard and not a system that decides on behalf of the analyst.
