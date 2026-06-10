# Team Concept Submission Form Draft

**Team Name:** FoilSaga Copilot

**Team Members:** Yifan Lu

**Concept Name:** FoilBrief: Race Performance Decision Support for SailGP Teams

**Stream:** On the Water

## Concept Summary

FoilBrief turns SailGP telemetry into a coach-ready race review workflow for SailGP performance analysts and coaches. After a race, the product scans maneuver candidates and presents all-maneuver coverage in one review queue, helping the analyst find moments worth reviewing before the next race.

The single-page workspace ranks internal review queue signals derived from fleet-relative telemetry evidence and lets the analyst filter by venue, race, team, maneuver type, and priority. Selecting a candidate reveals maneuver-level evidence, including speed and absolute-VMG separation, recovery behavior, confidence, and supplementary environment context. The richer curated Demo 413 adds a visual telemetry panel, Time Loss Receipt, and Coach Loss Card that turn evidence into a focused coaching conversation.

Saga, the safe Coach Analyst Agent, can use an optional provider to generate a concise brief grounded only in the selected local evidence. Deterministic checks refuse unsupported weather attribution and prescriptive boat-setting requests, while a grounded fallback keeps the workflow available.

FoilBrief reports estimated review signals rather than measured elapsed-time findings. SailGP telemetry remains the primary evidence; environment data is supporting context. The human analyst makes the final decision.

## Data

- Primary source: SailGP-provided challenge telemetry, mark-position data, and race metadata from **Ocean of Data Challenge: Foil Forward**
- Challenge data link: `https://drive.google.com/file/d/1yXLn4tzXRdJ2C-udGX4OavMSsRIeAblx/view`
- Supplementary context: Open-Meteo reanalysis shown only as environment review context

## Supporting Materials

- Production demo: `https://foil-brief-sail-gp-hackathon.vercel.app`
- Submission index: `submission/README.md`
- Video script and walkthrough: `submission/03_video_script_3min.md`, `submission/05_demo_walkthrough.md`
- Slides, method, safety, assets, and audits: `submission/04_slide_outline.md`, `submission/07_method_summary.md`, `submission/08_safety_limitations_and_human_decision.md`, `submission/assets/`, `submission/audits/`

Submit the completed official Team Concept Submission Form as a PDF. The final video link must be YouTube or Vimeo and the video must be no longer than 3 minutes.
