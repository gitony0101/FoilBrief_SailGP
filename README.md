# FoilBrief

FoilBrief is a SailGP post-race decision-support app that turns telemetry into a focused maneuver review workflow for performance analysts and coaches.

- **Challenge stream:** On the Water
- **Target user:** SailGP performance analysts and coaches
- **Demo website:** https://foil-brief-sail-gp-hackathon.vercel.app

## What FoilBrief Does

FoilBrief provides a full maneuver review queue, a curated Demo 413 deep dive, supplementary environment context, and Saga, an evidence-grounded assistant. The queue contains **1,336 maneuver candidates** and uses a queue score only to order review candidates. Selecting a candidate exposes visible telemetry evidence for coach review.

FoilBrief does not claim exact time loss or issue control commands. Environment context is supplementary and does not assign causality. The human analyst makes the final decision.

## Product Workflow

1. Scan and filter the full maneuver review queue.
2. Open a candidate and inspect visible telemetry, fleet-relative comparison, confidence, and recovery evidence.
3. Use the curated Demo 413 deep dive to review the richer evidence panel and coach card.
4. Ask Saga for a concise answer grounded in the selected evidence.
5. Let the human analyst decide what deserves follow-up.

## Data Sources And Policy

The primary evidence is derived from SailGP challenge telemetry, mark-position data, and race metadata. Open-Meteo context may be shown as supplementary environment context. Raw SailGP data is not committed or redistributed here. The small curated derived runtime data in `apps/web/public/foilbrief-data/` is committed only to run the app demo and remains subject to challenge data terms and human policy review.

## Run Locally

```bash
cd apps/web
npm ci
npm run dev
```

Open `http://localhost:3000`. The app works without provider credentials using deterministic grounded Saga responses.

## Environment Variables

Copy `apps/web/.env.example` to `apps/web/.env.local` for local configuration. Never commit `.env.local` or expose provider credentials with a `NEXT_PUBLIC_` prefix.

### Optional Saga Provider Setup

Keep `FOILBRIEF_AGENT_MODE=safe` for deterministic mode. Optional provider mode uses the server-side variables documented in `apps/web/.env.example`; failures and rejected output fall back to deterministic Saga responses.

## Vercel Deployment

Import the repository, set the Vercel Root Directory to `apps/web`, keep credentials server-side, and use the detected Next.js settings. No database, Python service, or authentication layer is required for this MVP.

## Repository Structure

- `apps/web/`: judge-ready Next.js app and curated public runtime assets
- `submission/`: final submission copy and supporting visuals
- `docs/`: selected method, safety, limitations, and scope notes
- `outputs/`: selected final evidence and validation artifacts
- `pipeline/`: minimal final analysis scripts for method transparency
- `externalized_artifacts_manifest/`: external artifact and reproduction policy

## Analysis Pipeline

The clean repository includes a minimal `pipeline/` folder for method transparency. Raw SailGP data is externalized and not committed, while the web app already includes small curated derived runtime data. Running the pipeline requires obtaining the official challenge data separately.

## Reproducibility Scope

The visible web app runs from audited final artifacts. The minimal final Python pipeline is included, while raw data, the experimental workspace, intermediate tables, and model artifacts remain externalized. Full raw-data reproduction requires official data access.

## Known Limitations And Safety Guardrails

- Queue score only orders review candidates.
- Coach review should rely on visible telemetry evidence.
- Environment context is supplementary and does not assign causality.
- FoilBrief does not issue control commands.
- FoilBrief does not claim exact time loss.
- Saga refuses unsupported causal, certainty, and prescriptive-control requests.
- Human analyst makes the final decision.

## License And Third-Party Assets

The source-code license decision is pending human review. SailGP challenge data, derived runtime assets, logos, brand assets, and external-source content remain subject to their respective terms. See `LICENSE.md`.
