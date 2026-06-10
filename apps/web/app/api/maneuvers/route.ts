import { getManeuvers } from "@/lib/data";

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams;
  const limit = Math.min(Math.max(Number(params.get("limit") || 1336), 1), 1336);
  const maneuvers = (await getManeuvers())
    .filter((row) => !params.get("team") || row.team === params.get("team"))
    .filter((row) => !params.get("maneuver_type") || row.maneuver_type === params.get("maneuver_type"))
    .filter((row) => !params.get("review_tier") || row.review_tier === params.get("review_tier"))
    .slice(0, limit);
  return Response.json({ count: maneuvers.length, maneuvers });
}
