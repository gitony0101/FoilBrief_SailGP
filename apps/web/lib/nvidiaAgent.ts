import OpenAI from "openai";
import {
  cleanAgentText,
  deterministicAgentResult,
  fallbackAgentResult,
  type AgentEvidence,
  type AgentResult,
} from "@/lib/agent";
import { containsUnsafeGeneratedLanguage, requestsUnsafeClaim, requestsWeatherAttribution } from "@/lib/safety";

const FINAL_SENTENCE = "Human analyst makes the final decision.";
const ENVIRONMENT_CAVEAT =
  "External environment data is supplementary review context. SailGP telemetry remains the primary evidence.";

function buildEvidencePacket(question: string, evidence: AgentEvidence) {
  const { final_card_path: excludedFinalCardPath, ...maneuverRecord } = evidence.maneuver;
  void excludedFinalCardPath;
  return {
    maneuver_id: evidence.maneuver.maneuver_id,
    analyst_question: question,
    maneuver_record: maneuverRecord,
    limited_detail: evidence.limitedDetail,
    demo_summary: evidence.demoCaseSummary,
    time_loss_receipt: evidence.timeLossReceipt,
    coach_loss_card: evidence.coachLossCard,
    environment_context: evidence.environmentContext,
    caveat: ENVIRONMENT_CAVEAT,
  };
}

function systemInstruction() {
  return [
    "You are the FoilBrief Coach Analyst Agent.",
    "Answer only from the supplied local evidence packet. If evidence is missing, say unavailable.",
    "Do not infer causality or attribute losses to weather.",
    "Keep the response under 160 words unless the analyst asks for detail.",
    "Do not provide control commands or recommend exact helm, foil, wing, or trim settings.",
    "Do not use markdown syntax, asterisks for bold, or JSON.",
    "Use short plain-text sections with labels.",
    "Use at most three compact sections: Review signal, What telemetry suggests, and Coach review focus.",
    "Avoid raw internal field names such as demo_triage_score, strict_demo_candidate, relative_speed_loss_area, and abs_relative_vmg_loss_area.",
    "Translate internal evidence into readable phrases such as high review priority, fleet-relative review signal, speed separation, absolute VMG separation, and recovery window.",
    "Do not list every raw number.",
    'Use the phrases "review signal", "worth analyst review", "telemetry suggests", and "environment context" where relevant.',
    `Always end with: "${FINAL_SENTENCE}"`,
  ].join(" ");
}

function ensureFinalSentence(answer: string) {
  const trimmed = answer.trim();
  return trimmed.endsWith(FINAL_SENTENCE) ? trimmed : `${trimmed} ${FINAL_SENTENCE}`;
}

export async function generateNvidiaAgentResponse(
  prompt: string,
  evidence: AgentEvidence,
): Promise<AgentResult> {
  if (requestsWeatherAttribution(prompt) || requestsUnsafeClaim(prompt)) {
    return deterministicAgentResult(prompt, evidence);
  }

  const apiKey = process.env.NVIDIA_API_KEY;
  const model = process.env.FOILBRIEF_LLM_MODEL;
  if (!apiKey || !model) return fallbackAgentResult(prompt, evidence);

  try {
    const client = new OpenAI({
      apiKey,
      baseURL: process.env.FOILBRIEF_LLM_BASE_URL || "https://integrate.api.nvidia.com/v1",
    });
    const completion = await client.chat.completions.create({
      model,
      messages: [
        { role: "system", content: systemInstruction() },
        { role: "user", content: JSON.stringify(buildEvidencePacket(prompt, evidence)) },
      ],
      temperature: 0.2,
      max_tokens: 700,
    });
    const content = completion.choices[0]?.message.content;
    const rawAnswer = typeof content === "string" ? ensureFinalSentence(content) : "";
    if (!rawAnswer) return fallbackAgentResult(prompt, evidence);
    if (containsUnsafeGeneratedLanguage(rawAnswer)) {
      return fallbackAgentResult(prompt, evidence, true);
    }
    const answer = cleanAgentText(rawAnswer);
    return {
      mode: "nvidia_nim",
      provider: "nvidia",
      response_type: "grounded_response",
      answer,
      fallback_used: false,
      safety_filter_triggered: false,
    };
  } catch {
    return fallbackAgentResult(prompt, evidence);
  }
}
