import { deterministicAgentResult, extractManeuverIdFromQuestion, type AgentResult } from "@/lib/agent";
import { getDemoBundle, getEnvironmentContextByManeuverId, getManeuver } from "@/lib/data";
import { generateNvidiaAgentResponse } from "@/lib/nvidiaAgent";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    analystQuestion?: string;
    maneuverId?: string | number;
    maneuver_id?: string | number;
    prompt?: string;
  };
  const prompt = (body.analystQuestion || body.prompt)?.trim();
  const requestedManeuverId = String(body.maneuverId || body.maneuver_id || "413");
  if (!prompt) return Response.json({ error: "A question is required." }, { status: 400 });

  const questionManeuverId = extractManeuverIdFromQuestion(prompt);
  const effectiveManeuverId = questionManeuverId || requestedManeuverId;
  const metadata = {
    requested_maneuver_id: requestedManeuverId,
    effective_maneuver_id: effectiveManeuverId,
    id_source: questionManeuverId ? "question" : "form",
  };
  const [maneuver, environmentContext] = await Promise.all([
    getManeuver(effectiveManeuverId),
    getEnvironmentContextByManeuverId(effectiveManeuverId),
  ]);
  if (!maneuver) return Response.json({ error: "Maneuver not found.", ...metadata }, { status: 404 });
  const evidence =
    effectiveManeuverId === "413"
      ? { maneuver, environmentContext, limitedDetail: false, ...(await getDemoBundle()) }
      : { maneuver, environmentContext, limitedDetail: true };

  let result: AgentResult;
  if (
    process.env.FOILBRIEF_AGENT_MODE === "llm" &&
    process.env.FOILBRIEF_AGENT_PROVIDER === "nvidia"
  ) {
    result = await generateNvidiaAgentResponse(prompt, evidence);
  } else {
    result = deterministicAgentResult(prompt, evidence);
  }
  return Response.json({ ...result, ...metadata });
}
