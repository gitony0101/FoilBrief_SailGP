# FoilBrief Final Submission Package

FoilBrief is a single-page SailGP race performance decision-support workspace for performance analysts and coaches in the **On the Water** stream. It turns SailGP telemetry into an all-maneuver review queue, selected maneuver evidence, supplementary environment context, and grounded Saga coach briefs. Saga can use an optional provider and has a deterministic grounded fallback. The human analyst makes the final decision.

## Open First

Open `01_team_concept_submission_form_draft.md` first. Copy its contents into the official Team Concept Submission Form, then export that completed form as PDF.

## Fixed Links

- Production demo: `https://foil-brief-sail-gp-hackathon.vercel.app`

## Submission Map

- Team Concept Submission Form: `01_team_concept_submission_form_draft.md`
- Concept summary, 250 words or less: `02_concept_summary_250_words.md`
- Video narration, maximum 3 minutes: `03_video_script_3min.md`
- Slide outline: `04_slide_outline.md`
- Exact demo route: `05_demo_walkthrough.md`

## Supporting Materials

- Project links and data sources: `06_project_links_and_data_sources.md`
- Method summary: `07_method_summary.md`
- Safety, limitations, and human decision boundary: `08_safety_limitations_and_human_decision.md`
- Curated Demo 413 assets: `assets/demo_case_413/`
- Maneuver index assets: `assets/maneuver_index/`
- Supporting audits: `audits/`

## Safety Boundary

FoilBrief supports post-race review; it does not operate the boat or make coaching decisions. Its fleet-relative review signals are estimated triage aids, not measured elapsed-time findings. SailGP telemetry remains the primary evidence, and environment context is supplementary. Saga refuses unsupported weather attribution and prescriptive boat-setting requests. The human analyst makes the final decision.
