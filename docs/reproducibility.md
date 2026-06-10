# Reproducibility Scope

Phase 2A reproduces the judge-ready Next.js application from the audited curated runtime assets included in `apps/web/public/foilbrief-data/`.

```bash
cd apps/web
npm ci
npm run lint
npm run build
```

The final minimal reproducibility scripts are included under `pipeline/`. Raw SailGP data, the experimental workspace, intermediate parquet files, and model artifacts remain externalized. The web demo does not require rerunning the pipeline. Full raw-data reproduction requires access to the official challenge dataset.

Selected final evidence and validation artifacts are retained under `outputs/`. See `externalized_artifacts_manifest/README.md` for the external artifact policy.
