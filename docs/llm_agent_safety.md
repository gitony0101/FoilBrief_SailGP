# FoilBrief LLM Agent Safety

## Purpose

The Coach Analyst Agent uses an LLM only as an optional narration layer over audited local
evidence. The evidence packet can include a maneuver index row, curated demo evidence,
a time loss receipt, a Coach Loss Card, and lightweight environment context.

The Saga provider is optional. FoilBrief remains functional in deterministic mode without an API key.

## Evidence Boundary

The LLM receives a compact local evidence packet. It does not receive raw weather payloads,
private file paths, parquet paths, secrets, environment variable values, or external search
results. Missing evidence must be described as unavailable.

SailGP telemetry remains the primary evidence. Environment data is supplementary review
context for a human analyst and is not used for weather attribution.

## Safety Controls

Before any provider request, FoilBrief checks the analyst question for causal, certainty, direct
equipment-setting, and control-request wording. Unsafe questions return the deterministic safe
refusal without calling the provider.

After the provider returns an answer, FoilBrief scans the generated text for prohibited causal,
certainty, direct-setting, and control wording. Rejected output is discarded and replaced with
the deterministic grounded response.

Forbidden wording examples include `caused by weather`, `optimal maneuver`, and
`exact control command`. Wording that frames the review signal as loss attribution is also
rejected. These examples document language the product must reject, not product claims.

Every accepted provider answer must end with: "Human analyst makes the final decision."

## Fallback Behavior

FoilBrief returns a deterministic grounded response when:

- provider mode is disabled.
- The provider API key or model is unavailable.
- The provider request fails.
- The provider returns an empty answer.
- The post-generation safety check rejects the answer.

The Agent does not provide control commands, recommend exact equipment settings, infer
causality, or attribute maneuver loss to weather.
