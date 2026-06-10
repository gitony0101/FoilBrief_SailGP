"use client";

import { FormEvent, useState } from "react";

type AgentPanelProps = {
  initialManeuverId?: string;
  initialPrompt?: string;
};

const reviewPrompt = "Why is maneuver 636 worth reviewing?";
const weatherPrompt = "Did weather explain the maneuver loss?";

export function AgentPanel({
  initialManeuverId = "413",
  initialPrompt = "Summarize the audited telemetry evidence and review focus.",
}: AgentPanelProps) {
  const [maneuverId, setManeuverId] = useState(initialManeuverId);
  const [prompt, setPrompt] = useState(initialPrompt);
  const [response, setResponse] = useState("");
  const [mode, setMode] = useState("");
  const [idOverride, setIdOverride] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setResponse("");
    setIdOverride("");
    const result = await fetch("/api/agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ maneuver_id: maneuverId, prompt }),
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
      data.id_source === "question" &&
        data.requested_maneuver_id !== data.effective_maneuver_id
        ? `Using maneuver ${data.effective_maneuver_id} from the question.`
        : "",
    );
    setLoading(false);
  }

  return (
    <div className="agent-grid">
      <form className="panel agent-form" onSubmit={submit}>
        <div>
          <div className="eyebrow">Ask Saga Coach</div>
          <h3>Turn evidence into a coach-ready review</h3>
        </div>
        <label>
          Maneuver ID
          <input value={maneuverId} onChange={(event) => setManeuverId(event.target.value)} />
        </label>
        <label>
          Analyst question
          <textarea rows={7} value={prompt} onChange={(event) => setPrompt(event.target.value)} />
        </label>
        <div className="prompt-presets" aria-label="Suggested Saga questions">
          <button type="button" className="prompt-chip" onClick={() => setPrompt(reviewPrompt)}>
            Why review maneuver 636?
          </button>
          <button type="button" className="prompt-chip" onClick={() => setPrompt(weatherPrompt)}>
            Test weather guardrail
          </button>
        </div>
        <p className="field-note">A maneuver ID written in the question overrides the form ID.</p>
        <button type="submit" disabled={loading}>{loading ? "Reviewing evidence..." : "Ask Saga"}</button>
      </form>
      <section className="panel response-panel">
        <div className="eyebrow">
          {mode === "nvidia_nim"
            ? "GROUNDED RESPONSE · SAGA"
            : mode === "safe_refusal"
              ? "SAGA GUARDRAIL · SAFE REFUSAL"
              : mode === "fallback" || mode === "fallback_after_safety_filter"
                ? "GROUNDED RESPONSE · SAGA FALLBACK"
                : "GROUNDED RESPONSE · SAGA"}
        </div>
        {idOverride && <p className="agent-helper">{idOverride}</p>}
        <p>{response || "Ask Saga to summarize local audited evidence for human review."}</p>
      </section>
    </div>
  );
}
