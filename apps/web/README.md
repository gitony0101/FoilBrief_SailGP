# FoilBrief Review Workspace

Next.js App Router client for reviewing FoilBrief maneuver candidates and querying Saga, the evidence-grounded assistant.

## Run Locally

```bash
npm ci
npm run dev
```

Open `http://localhost:3000`. The app works without credentials using deterministic grounded responses.

## Optional Saga Provider Setup

Deterministic mode is the default. To configure the optional server-side Saga provider, copy `.env.example` to `.env.local` and set the documented backend variables. Never expose provider credentials with a `NEXT_PUBLIC_` prefix.

Missing credentials, provider failures, empty answers, and rejected output fall back to deterministic Saga responses. Unsafe requests are refused before a provider request, and generated output is checked before it is returned.

## Data

Small audited runtime copies live under `public/foilbrief-data/`. SailGP telemetry remains the primary evidence. Environment context is supplementary and does not assign causality.

## Deploy To Vercel

1. Import the repository in Vercel.
2. Set the Root Directory to `apps/web`.
3. Keep deterministic mode or configure the optional Saga provider with server-side variables.
4. Deploy using the detected Next.js framework settings.

No database, Python service, or authentication layer is required for this MVP.
