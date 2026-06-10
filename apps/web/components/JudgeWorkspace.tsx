"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import type { EnvironmentContext, ManeuverIndexSummary, ManeuverRow } from "@/lib/types";

type WorkspaceTab = "overview" | "telemetry" | "environment" | "coach";

type JudgeWorkspaceProps = {
  maneuvers: ManeuverRow[];
  environments: Record<string, EnvironmentContext | null>;
  summary: ManeuverIndexSummary;
};

type SortMode = "signal" | "speed" | "vmg";

const pageSize = 25;

const tabs: { id: WorkspaceTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "telemetry", label: "Telemetry Signals" },
  { id: "environment", label: "Environment" },
  { id: "coach", label: "Coach Focus" },
];

function display(value: string) {
  return value.replaceAll("_", " ");
}

function number(value: string | number | null, digits = 1) {
  if (value === null || value === "") return "not available in index view";
  return Number(value).toFixed(digits);
}

export function JudgeWorkspace({ maneuvers, environments, summary }: JudgeWorkspaceProps) {
  const [selectedId, setSelectedId] = useState("413");
  const [tab, setTab] = useState<WorkspaceTab>("overview");
  const [search, setSearch] = useState("");
  const [venue, setVenue] = useState("");
  const [race, setRace] = useState("");
  const [team, setTeam] = useState("");
  const [maneuverType, setManeuverType] = useState("");
  const [priority, setPriority] = useState("");
  const [sortMode, setSortMode] = useState<SortMode>("signal");
  const [page, setPage] = useState(1);
  const [prompt, setPrompt] = useState("Summarize the selected index evidence and review focus.");
  const [response, setResponse] = useState("");
  const [mode, setMode] = useState("");
  const [idOverride, setIdOverride] = useState("");
  const [loading, setLoading] = useState(false);

  const selected = maneuvers.find((row) => row.maneuver_id === selectedId) || maneuvers[0];
  const environment = environments[selected.maneuver_id];
  const isDemo = selected.maneuver_id === "413";
  const optionValues = (key: keyof ManeuverRow) =>
    [...new Set(maneuvers.map((row) => row[key]).filter(Boolean))].sort();
  const races = useMemo(
    () =>
      [...new Set(
        maneuvers
          .filter((row) => !venue || row.source_location === venue)
          .map((row) => row.canonical_race_id),
      )].sort(),
    [maneuvers, venue],
  );
  const filtered = useMemo(() => {
    const rows = maneuvers.filter(
      (row) =>
        (!search || row.maneuver_id.includes(search.trim().replace("#", ""))) &&
        (!venue || row.source_location === venue) &&
        (!race || row.canonical_race_id === race) &&
        (!team || row.team === team) &&
        (!maneuverType || row.maneuver_type === maneuverType) &&
        (!priority || row.review_tier === priority),
    );
    return rows.sort((a, b) => {
      if (sortMode === "speed") return Number(b.relative_speed_loss_area || -1) - Number(a.relative_speed_loss_area || -1);
      if (sortMode === "vmg") return Number(b.abs_relative_vmg_loss_area || -1) - Number(a.abs_relative_vmg_loss_area || -1);
      return Number(b.demo_triage_score || -1) - Number(a.demo_triage_score || -1);
    });
  }, [maneuvers, maneuverType, priority, race, search, sortMode, team, venue]);
  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
  const visibleRows = filtered.slice((page - 1) * pageSize, page * pageSize);
  const venueCounts = useMemo(
    () => Object.fromEntries(["Bermuda", "Halifax"].map((name) => [name, maneuvers.filter((row) => row.source_location === name).length])),
    [maneuvers],
  );

  function selectManeuver(id: string) {
    setSelectedId(id);
    setTab("overview");
    setResponse("");
    setMode("");
    setIdOverride("");
  }

  function resetFilters() {
    setSearch("");
    setVenue("");
    setRace("");
    setTeam("");
    setManeuverType("");
    setPriority("");
    setSortMode("signal");
    setPage(1);
  }

  async function askSaga(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setResponse("");
    setIdOverride("");
    const result = await fetch("/api/agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ maneuver_id: selected.maneuver_id, prompt }),
    });
    const data = (await result.json()) as {
      answer?: string;
      effective_maneuver_id?: string;
      error?: string;
      id_source?: "question" | "form";
      mode?: string;
      requested_maneuver_id?: string;
    };
    setResponse(data.answer || data.error || "No response available.");
    setMode(data.mode || "");
    setIdOverride(
      data.id_source === "question" && data.requested_maneuver_id !== data.effective_maneuver_id
        ? `Using maneuver ${data.effective_maneuver_id} from the question.`
        : "",
    );
    setLoading(false);
  }

  const responseLabel =
    mode === "nvidia_nim"
      ? "GROUNDED RESPONSE · SAGA"
      : mode === "safe_refusal"
        ? "SAFE REFUSAL · SAGA GUARDRAIL"
        : mode === "fallback" || mode === "fallback_after_safety_filter"
          ? "FALLBACK · GROUNDED RESPONSE"
          : "DETERMINISTIC · GROUNDED RESPONSE";

  return (
    <section className="fleet-workspace" id="top-maneuvers">
      <div className="queue-panel">
        <div className="snapshot-heading">
          <div>
            <div className="eyebrow">All-maneuver review queue</div>
            <h2>Fleet Review Index</h2>
          </div>
          <p>Browse, search, and filter all {summary.total_maneuvers.toLocaleString()} detected candidates. Select a row to inspect its index-level evidence.</p>
        </div>

        <div className="queue-context">
          <div className="queue-distribution">
            <span>Priority distribution</span>
            <div className="distribution-bar" aria-label="Review priority distribution">
              <i className="high" style={{ width: `${summary.counts_by_review_tier.high_review_priority / summary.total_maneuvers * 100}%` }} />
              <i className="medium" style={{ width: `${summary.counts_by_review_tier.medium_review_priority / summary.total_maneuvers * 100}%` }} />
              <i className="low" style={{ width: `${summary.counts_by_review_tier.low_review_priority / summary.total_maneuvers * 100}%` }} />
              <i className="excluded" style={{ width: `${summary.counts_by_review_tier.exclude_from_demo / summary.total_maneuvers * 100}%` }} />
            </div>
            <small>{summary.counts_by_review_tier.high_review_priority} high · {summary.counts_by_review_tier.medium_review_priority} medium · {summary.counts_by_review_tier.low_review_priority} low · {summary.counts_by_review_tier.exclude_from_demo} excluded</small>
          </div>
          <div className="type-chips">
            <span>Bermuda <strong>{venueCounts.Bermuda}</strong></span>
            <span>Halifax <strong>{venueCounts.Halifax}</strong></span>
            {Object.entries(summary.counts_by_maneuver_type).map(([type, count]) => (
              <span key={type}>{display(type)} <strong>{count}</strong></span>
            ))}
          </div>
        </div>

        <div className="queue-filters">
          <label>
            Maneuver ID
            <input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} placeholder="Search ID" />
          </label>
          <label>
            Venue
            <select value={venue} onChange={(event) => { setVenue(event.target.value); setRace(""); setPage(1); }}>
              <option value="">All venues</option>
              {optionValues("source_location").map((value) => <option key={value}>{value}</option>)}
            </select>
          </label>
          <label>
            Race
            <select value={race} onChange={(event) => { setRace(event.target.value); setPage(1); }}>
              <option value="">All races</option>
              {races.map((value) => <option key={value} value={value}>{display(value)}</option>)}
            </select>
          </label>
          <label>
            Team
            <select value={team} onChange={(event) => { setTeam(event.target.value); setPage(1); }}>
              <option value="">All teams</option>
              {optionValues("team").map((value) => <option key={value}>{value}</option>)}
            </select>
          </label>
          <label>
            Type
            <select value={maneuverType} onChange={(event) => { setManeuverType(event.target.value); setPage(1); }}>
              <option value="">All types</option>
              {optionValues("maneuver_type").map((value) => <option key={value} value={value}>{display(value)}</option>)}
            </select>
          </label>
          <label>
            Priority
            <select value={priority} onChange={(event) => { setPriority(event.target.value); setPage(1); }}>
              <option value="">All priorities</option>
              {optionValues("review_tier").map((value) => <option key={value} value={value}>{display(value)}</option>)}
            </select>
          </label>
          <label>
            Sort
            <select value={sortMode} onChange={(event) => { setSortMode(event.target.value as SortMode); setPage(1); }}>
              <option value="signal">Review signal descending</option>
              <option value="speed">Speed separation</option>
              <option value="vmg">VMG separation</option>
            </select>
          </label>
          <button type="button" className="button ghost reset-button" onClick={resetFilters}>Reset filters</button>
        </div>

        <div className="queue-status">
          <strong>Showing {visibleRows.length} of {filtered.length.toLocaleString()} maneuver candidates</strong>
          <span>{summary.total_maneuvers.toLocaleString()} total · page {page} of {pageCount}</span>
        </div>

        <div className="snapshot-table">
          <table>
            <thead>
              <tr><th>Rank</th><th>ID</th><th>Team</th><th>Type</th><th>Race</th><th>Priority</th><th>Signal</th></tr>
            </thead>
            <tbody>
              {visibleRows.map((row, index) => (
                <tr
                  key={row.maneuver_id}
                  className={row.maneuver_id === selected.maneuver_id ? "selected-row" : ""}
                  onClick={() => selectManeuver(row.maneuver_id)}
                >
                  <td>{String((page - 1) * pageSize + index + 1).padStart(2, "0")}</td>
                  <td><button type="button" className="row-select">#{row.maneuver_id}</button></td>
                  <td>{row.team}</td>
                  <td>{display(row.maneuver_type)}</td>
                  <td>{display(row.canonical_race_id)}</td>
                  <td><span className="priority-pill">{display(row.review_tier)}</span></td>
                  <td><strong>{number(row.demo_triage_score, 3)}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pagination">
          <button type="button" className="button ghost" disabled={page === 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>Previous</button>
          <span>Page {page} of {pageCount}</span>
          <button type="button" className="button ghost" disabled={page === pageCount} onClick={() => setPage((value) => Math.min(pageCount, value + 1))}>Next</button>
        </div>
      </div>

      <div className="workspace-columns" id="workspace">
        <div className="evidence-workspace">
          <div className="control-bar">
            <div>
              <span>Selected review</span>
              <strong>#{selected.maneuver_id} · {selected.team} {display(selected.maneuver_type)}</strong>
            </div>
            <label>
              Maneuver
              <select value={selected.maneuver_id} onChange={(event) => selectManeuver(event.target.value)}>
                {maneuvers.map((row) => (
                  <option key={row.maneuver_id} value={row.maneuver_id}>#{row.maneuver_id} · {row.team} {row.maneuver_type}</option>
                ))}
              </select>
            </label>
            <Link className="button demo-link" href="/maneuver/413">Open Demo 413 Deep Dive</Link>
          </div>

          <div className="workspace-body">
            <div className="workspace-title">
              <div>
                <div className="eyebrow">Selected index-level evidence</div>
                <h2>{selected.team} {display(selected.maneuver_type)} · {display(selected.canonical_race_id)}</h2>
              </div>
              <span className="priority-pill">{display(selected.review_tier)}</span>
            </div>

            <div className="four-metrics">
              <article><span>Review signal</span><strong>{number(selected.demo_triage_score, 3)}</strong></article>
              <article><span>Speed separation</span><strong>{number(selected.relative_speed_loss_area)}</strong></article>
              <article><span>VMG separation</span><strong>{number(selected.abs_relative_vmg_loss_area)}</strong></article>
              <article><span>Confidence</span><strong>{selected.loss_confidence || "not available"}</strong></article>
            </div>

            <div className="workspace-tabs" role="tablist" aria-label="Evidence views">
              {tabs.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={tab === item.id ? "active" : ""}
                  onClick={() => setTab(item.id)}
                  role="tab"
                  aria-selected={tab === item.id}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <div className="tab-panel">
              {tab === "overview" && (
                <div className="index-evidence-overview">
                  <article className="selected-receipt">
                    <div className="eyebrow">Index-level evidence</div>
                    <div className="selected-identity"><strong>#{selected.maneuver_id}</strong><span>{selected.team}</span></div>
                    <dl className="compact-list">
                      <div><dt>Maneuver / race</dt><dd>{display(selected.maneuver_type)} · {display(selected.canonical_race_id)}</dd></div>
                      <div><dt>Venue</dt><dd>{selected.source_location || "not available in index view"}</dd></div>
                      <div><dt>Review signal</dt><dd>{number(selected.demo_triage_score, 3)}</dd></div>
                      <div><dt>Speed separation</dt><dd>{number(selected.relative_speed_loss_area)}</dd></div>
                      <div><dt>Absolute VMG separation</dt><dd>{number(selected.abs_relative_vmg_loss_area)}</dd></div>
                      <div><dt>Confidence</dt><dd>{selected.baseline_confidence} baseline / {selected.loss_confidence} loss</dd></div>
                    </dl>
                  </article>
                  <article className="evidence-boundary">
                    <div className="eyebrow">{isDemo ? "Curated visual evidence available" : "Evidence availability"}</div>
                    <h3>{isDemo ? "Maneuver 413 has a separate audited visual deep dive." : "This selection has index-level evidence only."}</h3>
                    <p>{isDemo ? "Open the curated page for the race map, telemetry panel, Time Loss Receipt, Coach Loss Card, environment context, and Saga brief." : "Full visual deep dive is available for curated Demo 413. This workspace does not reuse Demo 413 evidence for other maneuvers."}</p>
                    <Link className="button ghost" href={isDemo ? "/maneuver/413" : `/maneuver/${selected.maneuver_id}`}>
                      {isDemo ? "Open curated Demo 413 deep dive" : `Open maneuver ${selected.maneuver_id} detail`}
                    </Link>
                  </article>
                </div>
              )}

              {tab === "telemetry" && (
                <div className="tab-copy">
                  <div className="eyebrow">Telemetry signals</div>
                  <h3>Telemetry suggests maneuver {selected.maneuver_id} is worth reviewing based on its fleet-relative index signals.</h3>
                  <dl className="compact-list">
                    <div><dt>Classification confidence</dt><dd>{selected.classification_confidence || "not available in index view"}</dd></div>
                    <div><dt>Time below fleet speed</dt><dd>{number(selected.time_below_fleet_speed)} s</dd></div>
                    <div><dt>Time below fleet VMG</dt><dd>{number(selected.time_below_fleet_vmg)} s</dd></div>
                    <div><dt>Recovery to 90%</dt><dd>{selected.recovery_time_to_90 ? `${number(selected.recovery_time_to_90)} s` : "not available in index view"}</dd></div>
                    <div><dt>Baseline confidence</dt><dd>{selected.baseline_confidence}</dd></div>
                    <div><dt>Data gap near center</dt><dd>{selected.data_gap_near_center}</dd></div>
                  </dl>
                </div>
              )}

              {tab === "environment" && (
                <div className="tab-copy">
                  <div className="eyebrow">Supplementary environment context</div>
                  <h3>{environment?.environment_brief_sentence || "Environment context is not available in this index view."}</h3>
                  <dl className="compact-list">
                    <div><dt>Location</dt><dd>{environment?.event_location || selected.source_location || "not available in index view"}</dd></div>
                    <div><dt>Estimated wind</dt><dd>{number(environment?.open_meteo_wind_speed_10m ?? null)} m/s</dd></div>
                    <div><dt>Estimated direction</dt><dd>{number(environment?.open_meteo_wind_direction_10m ?? null, 0)}°</dd></div>
                    <div><dt>Weather match delta</dt><dd>{number(environment?.weather_time_delta_minutes ?? null)} min</dd></div>
                    <div><dt>Wave context</dt><dd>{environment?.wave_context_flag || "not available in index view"}</dd></div>
                  </dl>
                </div>
              )}

              {tab === "coach" && (
                <div className="tab-copy">
                  <div className="eyebrow">Coach review focus</div>
                  <h3>Use selected index-level evidence to prioritize human review.</h3>
                  <ul>
                    <li>Review the {display(selected.maneuver_type)} window against the fleet median.</li>
                    <li>Inspect speed and absolute VMG separation alongside {selected.loss_confidence} loss confidence.</li>
                    <li>Treat the signal as a review priority for the human final decision.</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>

        <aside className="saga-workspace">
          <div className="saga-heading">
            <div className="eyebrow">Saga · Evidence-grounded assistant</div>
            <h2>Ask about selected evidence.</h2>
            <p>Ask a question about the selected maneuver. Saga answers only from selected index evidence, curated demo evidence, and allowed environment context.</p>
            <small className="saga-mode">LLM-backed when provider mode is enabled; deterministic grounded fallback otherwise.</small>
            <small className="saga-mode">A maneuver ID in the question overrides the current selection.</small>
          </div>
          <form onSubmit={askSaga}>
            <label>
              Analyst question
              <textarea rows={3} value={prompt} onChange={(event) => setPrompt(event.target.value)} />
            </label>
            <div className="saga-actions">
              <button type="button" className="prompt-chip" onClick={() => setPrompt(`Why is maneuver ${selected.maneuver_id} worth reviewing?`)}>Why review this?</button>
              <button type="button" className="prompt-chip" onClick={() => setPrompt("Did weather explain the maneuver loss?")}>Test guardrail</button>
            </div>
            <button type="submit" disabled={loading}>{loading ? "Reviewing evidence..." : "Ask Saga"}</button>
          </form>
          <div className="saga-response">
            <span>{mode === "safe_refusal" ? responseLabel : "GROUNDED RESPONSE · SAGA"}</span>
            {idOverride && <small>{idOverride}</small>}
            <p>{response || "Generate a grounded response for the selected maneuver."}</p>
          </div>
          <div className="saga-safety">Saga does not assign weather causality or issue control commands. Human analyst makes the final decision.</div>
        </aside>
      </div>
    </section>
  );
}
