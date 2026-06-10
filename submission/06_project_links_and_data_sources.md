# Project Links And Data Sources

## Submission Links

- Production demo: `https://foil-brief-sail-gp-hackathon.vercel.app`

The final video link must be YouTube or Vimeo, and the video must be no longer than 3 minutes.

## Primary SailGP Challenge Data

FoilBrief uses SailGP-provided data from **Ocean of Data Challenge: Foil Forward** as its primary evidence source. The local challenge documentation records this data link:

`https://drive.google.com/file/d/1yXLn4tzXRdJ2C-udGX4OavMSsRIeAblx/view`

The product uses challenge telemetry, mark-position data, and race metadata to create maneuver candidates, same-race fleet comparisons, recovery evidence, and the all-maneuver review queue.

## Supplementary Environment Context

Open-Meteo reanalysis is displayed only as supplementary environment context with availability and confidence caveats. It can help frame analyst review, but it does not replace SailGP telemetry or support weather attribution. SailGP telemetry remains the primary evidence.

## Optional Saga Provider

The optional Saga provider is a grounded brief-generation layer behind Saga, the Coach Analyst Agent. It receives a compact selected-evidence packet and produces a coach-readable summary. Deterministic request checks, generated-language checks, and grounded fallback preserve the product safety boundary. The human analyst makes the final decision.
