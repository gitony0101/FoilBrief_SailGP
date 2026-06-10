import type { CoachLossCard } from "@/lib/types";

function label(value: string) {
  return value.replaceAll("_", " ");
}

function safeFixed(value: number | undefined | null, digits = 1): string {
  if (value == null || Number.isNaN(value)) return "N/A";
  return value.toFixed(digits);
}

function formatEvidence(value: string | number | boolean | null) {
  if (value === null) return "not recovered within review window";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(3);
  return String(value);
}

export function CoachCard({ card }: { card: CoachLossCard }) {
  return (
    <article className="coach-loss-card">
      <header className="coach-card-header">
        <div>
          <div className="eyebrow">Coach Loss Card · curated case</div>
          <h2>{card.header.team} {card.header.maneuver} · maneuver {card.header.maneuver_id}</h2>
          <p>{label(String(card.header.race))} · {card.header.context}</p>
        </div>
        <div className="coach-signal">
          <span>Estimated review signal</span>
          <strong>{safeFixed(card.estimated_review_signal?.normalized_review_signal_points, 1)}</strong>
          <small>normalized points</small>
        </div>
      </header>

      <section className="coach-card-section">
        <div className="eyebrow">Estimated review signal</div>
        <div className="coach-card-metrics">
          <article><span>Internal queue score</span><strong>{safeFixed(card.estimated_review_signal?.demo_triage_score, 3)}</strong></article>
          <article><span>Speed separation</span><strong>{safeFixed(card.estimated_review_signal?.speed_separation, 1)}</strong></article>
          <article><span>Absolute VMG separation</span><strong>{safeFixed(card.estimated_review_signal?.absolute_vmg_separation, 1)}</strong></article>
          <article><span>Confidence</span><strong>{card.estimated_review_signal?.confidence ?? "N/A"}</strong></article>
        </div>
        <p className="recovery-line">{card.estimated_review_signal.recovery_status}</p>
      </section>

      <section className="coach-card-section">
        <div className="eyebrow">What telemetry suggests</div>
        <ul className="statement-list">
          {card.telemetry_suggests.map((statement, index) => <li key={`telemetry-${index}`}>{statement}</li>)}
        </ul>
      </section>

      <section className="coach-card-section">
        <div className="eyebrow">Key evidence</div>
        <div className="coach-evidence-grid">
          {Object.entries(card.evidence).map(([name, value]) => (
            <div key={name}><span>{label(name)}</span><strong>{formatEvidence(value)}</strong></div>
          ))}
        </div>
      </section>

      <div className="coach-card-bottom">
        <section className="coach-card-section">
          <div className="eyebrow">Coach review focus</div>
          <ol>
            {card.coach_review_focus.map((focus, index) => <li key={`focus-${index}`}>{focus}</li>)}
          </ol>
        </section>
        <section className="coach-card-section caveat-section">
          <div className="eyebrow">Caveats · human final decision</div>
          <ul>
            {card.caveats.map((caveat, index) => <li key={`caveat-${index}`}>{caveat}</li>)}
          </ul>
        </section>
      </div>
    </article>
  );
}
