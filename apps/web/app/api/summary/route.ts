import { getSummary } from "@/lib/data";

export async function GET() {
  return Response.json(await getSummary());
}
