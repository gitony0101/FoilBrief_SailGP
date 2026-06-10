import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CoachCard } from "@/components/CoachCard";
import { SafeCaveat } from "@/components/SafeCaveat";
import {
  getDemoBundle,
  getEnvironmentContextByManeuverId,
  getManeuver,
} from "@/lib/data";
import type { EnvironmentContext } from "@/lib/types";

function formatNumber(value: number | null, suffix = "") {
  return value === null ? "unavailable" : `${value.toFixed(1)}${suffix}`;
}

function EnvironmentContextSection({
  environmentContext,
}: {
  environmentContext: EnvironmentContext | null;
}) {
  if (!environmentContext) {
    return (
      <section className="panel">
        <div className="eyebrow">Environment Context</div>
        <h2>Context unavailable</h2>
        <p>No lightweight environment context is available for this maneuver.</p>
        <aside className="caveat">
          Environment data is review context only. SailGP telemetry remains the primary evidence;
          this section does not make causal claims.
        </aside>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="eyebrow">Environment Context</div>
      <h2>{environmentContext.event_location || "Maneuver environment review"}</h2>
      <dl className="metric-list">
        <div>
          <dt>Confidence label</dt>
          <dd>{environmentContext.environment_confidence_label}</dd>
        </div>
        <div>
          <dt>Source availability</dt>
          <dd>
            Open-Meteo {environmentContext.open_meteo_available ? "available" : "unavailable"} ·
            NOAA NDBC {environmentContext.ndbc_available ? "available" : "unavailable"}
          </dd>
        </div>
        <div>
          <dt>Wind estimate</dt>
          <dd>
            {formatNumber(environmentContext.open_meteo_wind_speed_10m, " m/s")} ·{" "}
            {formatNumber(environmentContext.open_meteo_wind_direction_10m, "°")}
          </dd>
        </div>
        <div>
          <dt>Weather time delta</dt>
          <dd>{formatNumber(environmentContext.weather_time_delta_minutes, " min")}</dd>
        </div>
        <div>
          <dt>Wave context</dt>
          <dd>{environmentContext.wave_context_flag}</dd>
        </div>
      </dl>
      <p>{environmentContext.environment_brief_sentence}</p>
      <aside className="caveat">
        Environment data is review context only. SailGP telemetry remains the primary evidence;
        this section does not make causal claims.
      </aside>
    </section>
  );
}


function receiptLabel(name: string) {
  const labels: Record<string, string> = {
    speed_separation_component: "Fleet-relative speed separation",
    abs_vmg_separation_component: "Fleet-relative VMG separation",
    recovery_delay_component: "Recovery status signal",
    review_uncertainty_component: "Review uncertainty",
  };
  return labels[name] ?? name.replaceAll("_", " ");
}

function receiptValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "not available";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(1);
  return String(value);
}

export default async function ManeuverPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [maneuver, environmentContext] = await Promise.all([
    getManeuver(id),
    getEnvironmentContextByManeuverId(id),
  ]);
  if (!maneuver) notFound();

  if (id !== "413") {
    return (
      <>
        <section className="page-heading">
          <div className="eyebrow">Limited evidence view</div>
          <h1>Maneuver {id}</h1>
          <p>{maneuver.team} · {maneuver.maneuver_type.replaceAll("_", " ")} · {maneuver.canonical_race_id.replaceAll("_", " ")}</p>
        </section>
        <SafeCaveat />
        <section className="panel">
          <div className="eyebrow">Compact review brief</div>
          <h2>Fleet-relative review evidence</h2>
          <dl className="metric-list">
            <div><dt>Team / boat</dt><dd>{maneuver.team} / {maneuver.boat}</dd></div>
            <div><dt>Center time</dt><dd>{maneuver.center_time}</dd></div>
            <div><dt>Review tier</dt><dd>{maneuver.review_tier.replaceAll("_", " ")}</dd></div>
            <div><dt>Review signal</dt><dd>{maneuver.demo_triage_score ? Number(maneuver.demo_triage_score).toFixed(3) : "n/a"}</dd></div>
            <div><dt>Baseline confidence</dt><dd>{maneuver.baseline_confidence}</dd></div>
            <div><dt>Loss confidence</dt><dd>{maneuver.loss_confidence}</dd></div>
          </dl>
          <p>A full Coach Loss Card is currently generated only for curated demo case 413.</p>
          {process.env.NODE_ENV === "development" && (
            <pre>python experiments/stage3_build_demo_case.py --maneuver-id {id}</pre>
          )}
          <Link className="button ghost" href="/review-index">Back to review index</Link>
        </section>
        <EnvironmentContextSection environmentContext={environmentContext} />
      </>
    );
  }

  const { demoCaseSummary, timeLossReceipt, coachLossCard } = await getDemoBundle();
  return (
    <>
      <section className="page-heading">
        <div className="eyebrow">Curated deep-dive demo · maneuver 413</div>
        <h1>{demoCaseSummary.team} {demoCaseSummary.maneuver_type} {demoCaseSummary.context}</h1>
        <p>{demoCaseSummary.one_sentence_demo_story}</p>
      </section>
      <SafeCaveat />
      <section className="detail-grid">
        <div className="panel image-panel">
          <Image src="/foilbrief-data/demo_case_413/05_demo_panel.png" alt="Maneuver 413 audited demo panel" width={1800} height={1100} priority />
        </div>
        <aside className="panel">
          <div className="eyebrow">Key review evidence</div>
          <dl className="metric-list">
            <p className="metric-caveat">Queue score is used only to order review candidates. Coach review should rely on the visible telemetry evidence below.</p>
            <div><dt>Internal queue score</dt><dd>{demoCaseSummary.demo_candidate_score.toFixed(3)}</dd></div>
            <div><dt>Index points</dt><dd>{coachLossCard.estimated_review_signal.normalized_review_signal_points.toFixed(1)}</dd></div>
            <div><dt>Confidence</dt><dd>{coachLossCard.estimated_review_signal.confidence}</dd></div>
            <div><dt>Recovery</dt><dd>{coachLossCard.estimated_review_signal.recovery_status}</dd></div>
          </dl>
          <Link className="button" href="/agent">Ask about maneuver 413</Link>
        </aside>
      </section>
      <section className="panel">
        <div className="eyebrow">Time Loss Receipt</div>
        <h2>Telemetry evidence receipt</h2>
        <p>This section summarizes observable review signals for manual analysis. It is not a measured elapsed-time loss attribution.</p>
        <dl className="metric-list">
          {Object.entries(timeLossReceipt.components).map(([name, component]) => (
            <div key={name}><dt>{receiptLabel(name)}</dt><dd>{receiptValue(component.points ?? component.status)}</dd></div>
          ))}
        </dl>
      </section>
      <EnvironmentContextSection environmentContext={environmentContext} />
      <CoachCard card={coachLossCard} />
    </>
  );
}
