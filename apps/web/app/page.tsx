import Image from "next/image";
import Link from "next/link";
import { JudgeWorkspace } from "@/components/JudgeWorkspace";
import { getManeuvers, getSummary, loadEnvironmentContext } from "@/lib/data";

export default async function Home() {
  const [maneuvers, summary, environmentRows] = await Promise.all([
    getManeuvers(),
    getSummary(),
    loadEnvironmentContext(),
  ]);
  const environments = Object.fromEntries(
    environmentRows.map((row) => [row.maneuver_id, row]),
  );

  return (
    <>
      <section className="compact-hero">
        <div>
          <div className="eyebrow">FoilBrief Race Intelligence</div>
          <h1>Fleet review queue for post-race maneuver decisions.</h1>
          <p>Select a maneuver candidate, inspect fleet-relative review signals, and ask Saga for a grounded coaching brief.</p>
          <div className="actions">
            <a className="button" href="#top-maneuvers">Open review queue</a>
            <Link className="button ghost" href="/maneuver/413">Open Demo 413 Deep Dive</Link>
          </div>
        </div>
        <aside>
          <span>Current decision</span>
          <strong>What should the coach review before the next race?</strong>
          <small>Estimated signals · index-level evidence · human final decision</small>
        </aside>
      </section>

      <section className="scope-metrics" aria-label="Fleet review scope">
        <article><strong>{summary.total_maneuvers.toLocaleString()}</strong><span>maneuver candidates</span><small>across {summary.total_races} races</small></article>
        <article><strong>{summary.unique_teams}</strong><span>teams</span><small>fleet-relative review</small></article>
        <article><strong>413</strong><span>curated deep dive</span><small>separate audited visual case</small></article>
        <article><strong>Human</strong><span>final decision</span><small>evidence-first guardrail</small></article>
      </section>

      <JudgeWorkspace maneuvers={maneuvers} environments={environments} summary={summary} />

      <section className="sponsor-strip" aria-label="Challenge and telemetry partners">
        <div>
          <span>Built for the Ocean of Data Challenge using SailGP-provided telemetry.</span>
          <small>Hackathon prototype. Not an official SailGP or NorthStar product.</small>
        </div>
        <div className="sponsor-logos">
          <Image src="/brand/sailgp-logo.png" alt="SailGP official logo" width={168} height={84} />
          <Image src="/brand/northstar.jpg" alt="NorthStar SailGP Team logo" width={400} height={120} />
          <Image src="/brand/challenge-partners.png" alt="ShiftKey Labs, COVE, and DeepSense logos" width={480} height={80} />
        </div>
      </section>
    </>
  );
}
