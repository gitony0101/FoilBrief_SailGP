import {
  getDemoBundle,
  getEnvironmentContextByManeuverId,
  getManeuver,
} from "@/lib/data";

const ENVIRONMENT_FALLBACK =
  "Environment context is unavailable for this maneuver. SailGP telemetry remains the primary review evidence.";
const ENVIRONMENT_CONTEXT_NOTE =
  "External environment data is supplementary review context. SailGP telemetry remains the primary evidence.";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [maneuver, environmentContext] = await Promise.all([
    getManeuver(id),
    getEnvironmentContextByManeuverId(id),
  ]);
  if (!maneuver) return Response.json({ error: "Maneuver not found" }, { status: 404 });
  const environment = {
    environment_context: environmentContext,
    environment_context_available: Boolean(
      environmentContext?.open_meteo_available || environmentContext?.ndbc_available,
    ),
    environment_context_note:
      environmentContext?.environment_context_note ||
      (environmentContext ? ENVIRONMENT_CONTEXT_NOTE : ENVIRONMENT_FALLBACK),
  };
  if (id !== "413") return Response.json({ maneuver, limited_detail: true, ...environment });
  return Response.json({
    maneuver,
    limited_detail: false,
    ...(await getDemoBundle()),
    ...environment,
  });
}
