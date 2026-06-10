import type {
  CoachLossCard,
  DemoCaseSummary,
  EnvironmentContext,
  ManeuverRow,
  TimeLossReceipt,
} from "@/lib/types";
import {
  requestsUnsafeClaim,
  requestsWeatherAttribution,
  SAFE_REFUSAL,
  WEATHER_ATTRIBUTION_REFUSAL,
} from "@/lib/safety";

export type AgentEvidence = {
  maneuver: ManeuverRow;
  limitedDetail: boolean;
  demoCaseSummary?: DemoCaseSummary;
  coachLossCard?: CoachLossCard;
  timeLossReceipt?: TimeLossReceipt;
  environmentContext?: EnvironmentContext | null;
};

export type AgentResult = {
  mode: "deterministic" | "nvidia_nim" | "fallback" | "fallback_after_safety_filter" | "safe_refusal";
  provider: "deterministic" | "nvidia";
  response_type: "grounded_response" | "safe_refusal";
  answer: string;
  fallback_used: boolean;
  safety_filter_triggered: boolean;
};

export function extractManeuverIdFromQuestion(question: string): string | null {
  return question.match(/\bmaneuver\s+#?(\d{1,5})\b/i)?.[1] ?? null;
}

export function cleanAgentText(answer: string): string {
  return answer
    .replace(/\bdemo_triage_score\b/gi, "review priority score")
    .replace(/\bstrict_demo_candidate\b/gi, "high review priority")
    .replace(/\brelative_speed_loss_area\b/gi, "speed separation")
    .replace(/\babs_relative_vmg_loss_area\b/gi, "absolute VMG separation")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/^\s{0,3}#{1,6}\s*/gm, "")
    .replace(/^\s*[-*_]{3,}\s*$/gm, "")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

export function deterministicResponse(prompt: string, evidence: AgentEvidence) {
  if (requestsWeatherAttribution(prompt)) return WEATHER_ATTRIBUTION_REFUSAL;
  if (requestsUnsafeClaim(prompt)) return SAFE_REFUSAL;

  const row = evidence.maneuver;
  const environmentSentence = evidence.environmentContext?.environment_brief_sentence
    ? ` Environment context: ${evidence.environmentContext.environment_brief_sentence}`
    : "";
  if (!evidence.coachLossCard || !evidence.demoCaseSummary || !evidence.timeLossReceipt) {
    return `Maneuver ${row.maneuver_id} is a ${row.review_tier.replaceAll("_", " ")} ${row.maneuver_type} review candidate for ${row.team}. Its internal queue score is ${Number(row.demo_triage_score || 0).toFixed(3)} and is used only to order review candidates. Coach review should rely on the selected telemetry evidence before drawing a coaching conclusion.${environmentSentence}`;
  }

  const card = evidence.coachLossCard;
  return [
    evidence.demoCaseSummary.one_sentence_demo_story,
    `The Coach Loss Card reports an estimated normalized review signal of ${card.estimated_review_signal.normalized_review_signal_points.toFixed(1)} points with ${card.estimated_review_signal.confidence} confidence.`,
    `Telemetry suggests ${card.telemetry_suggests[0].toLowerCase()} ${card.telemetry_suggests[2]}`,
    `Key caveat: ${card.caveats[0]} The human analyst decides the coaching interpretation.${environmentSentence}`,
  ].join(" ");
}

export function deterministicAgentResult(prompt: string, evidence: AgentEvidence): AgentResult {
  const unsafe = requestsWeatherAttribution(prompt) || requestsUnsafeClaim(prompt);
  return {
    mode: unsafe ? "safe_refusal" : "deterministic",
    provider: "deterministic",
    response_type: unsafe ? "safe_refusal" : "grounded_response",
    answer: deterministicResponse(prompt, evidence),
    fallback_used: false,
    safety_filter_triggered: unsafe,
  };
}

export function fallbackAgentResult(
  prompt: string,
  evidence: AgentEvidence,
  safetyFilterTriggered = false,
): AgentResult {
  return {
    mode: safetyFilterTriggered ? "fallback_after_safety_filter" : "fallback",
    provider: "nvidia",
    response_type: "grounded_response",
    answer: deterministicResponse(prompt, evidence),
    fallback_used: true,
    safety_filter_triggered: safetyFilterTriggered,
  };
}
