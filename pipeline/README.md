# FoilBrief Analysis Pipeline

This folder contains the minimal final analysis scripts used to generate the derived runtime artifacts included in the FoilBrief web app.

Raw SailGP challenge data is not committed to this repository. It must be obtained from the official challenge data source. The committed files under `apps/web/public/foilbrief-data/` are small curated derived runtime assets used by the web app. These scripts are included for method transparency, not to redistribute raw data.

The pipeline is app-supporting and reproducibility-oriented; the web demo runs without raw data. Environment context is supplementary and does not assign causality. Queue score only orders review candidates, and coach review relies on visible telemetry evidence. FoilBrief does not claim exact time loss or issue control commands. The human analyst makes the final decision.

## Scripts

- `01_build_maneuver_review_index.py`: Builds the maneuver review index used by the web app.
- `02_build_demo_case_413.py`: Builds the curated Demo 413 evidence package.
- `03_build_environment_context.py`: Builds supplementary environment context for the web app.

## Expected Inputs

- External raw SailGP challenge telemetry
- Mark position files
- Race metadata
- Optional public environment data where applicable
- Externalized processed intermediate tables documented by each script's CLI help

## Expected Outputs

- `apps/web/public/foilbrief-data/maneuver_index/`
- `apps/web/public/foilbrief-data/demo_case_413/`
- `apps/web/public/foilbrief-data/environment_context/`
- `outputs/demo_case_413/`
- `outputs/maneuver_index/`
- `outputs/environment_context/`

Generated assets are written to `outputs/` by default. Pass `--publish-web-assets` only after human review to refresh the corresponding curated web runtime directory. Use each script's `--help` output to configure external input and working paths.
