import { ManeuverTable } from "@/components/ManeuverTable";
import { SafeCaveat } from "@/components/SafeCaveat";
import { getManeuvers } from "@/lib/data";

export default async function ReviewIndexPage() {
  const maneuvers = await getManeuvers();
  return (
    <>
      <section className="page-heading">
        <div className="eyebrow">Fleet scan · sorted by review signal</div>
        <h1>All-Maneuver Review Index</h1>
        <p>Filter 1,336 candidates by team, maneuver type, and review tier. Maneuver 413 is the curated full-card demonstration.</p>
      </section>
      <SafeCaveat />
      <ManeuverTable maneuvers={maneuvers} />
    </>
  );
}
