# Exact Demo Walkthrough

1. Open `https://foil-brief-sail-gp-hackathon.vercel.app`.
2. On the hero, say: “FoilBrief helps SailGP performance analysts find what deserves coach review before the next race.”
3. Scroll to **Fleet Review Index**. Show 1,336 maneuver candidates, 13 teams, 14 races, priority distribution, filters, and pagination.
4. Filter or select a row. Show that the selected maneuver, metrics, and **Overview**, **Telemetry Signals**, **Environment**, and **Coach Focus** tabs update together.
5. State: “Environment context is supplementary; SailGP telemetry remains the primary evidence.”
6. Select maneuver `413`, then click **Open Demo 413 Deep Dive**.
7. Show the audited visual panel, **Time Loss Receipt**, **Environment Context**, and structured **Coach Loss Card**. Point to internal review queue signals, recovery status, caveats, and coach review focus.
8. Return to the homepage and select maneuver `636`.
9. In Saga, ask: `Why is maneuver 636 worth reviewing?`
10. Show the grounded response and its use of selected evidence.
11. Ask the safe-refusal query: `Was maneuver 636 caused by the weather?`
12. Show the Saga guardrail response.
13. End with: “Human analyst makes the final decision.”
