"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { ManeuverRow } from "@/lib/types";

export function ManeuverTable({ maneuvers }: { maneuvers: ManeuverRow[] }) {
  const [team, setTeam] = useState("");
  const [maneuverType, setManeuverType] = useState("");
  const [reviewTier, setReviewTier] = useState("");

  const options = (key: keyof ManeuverRow) =>
    [...new Set(maneuvers.map((row) => row[key]).filter(Boolean))].sort();

  const filtered = useMemo(
    () =>
      maneuvers.filter(
        (row) =>
          (!team || row.team === team) &&
          (!maneuverType || row.maneuver_type === maneuverType) &&
          (!reviewTier || row.review_tier === reviewTier),
      ),
    [maneuvers, team, maneuverType, reviewTier],
  );

  return (
    <>
      <div className="filters panel">
        <label>
          Team
          <select value={team} onChange={(event) => setTeam(event.target.value)}>
            <option value="">All teams</option>
            {options("team").map((value) => <option key={value}>{value}</option>)}
          </select>
        </label>
        <label>
          Maneuver type
          <select value={maneuverType} onChange={(event) => setManeuverType(event.target.value)}>
            <option value="">All types</option>
            {options("maneuver_type").map((value) => <option key={value}>{value}</option>)}
          </select>
        </label>
        <label>
          Review tier
          <select value={reviewTier} onChange={(event) => setReviewTier(event.target.value)}>
            <option value="">All tiers</option>
            {options("review_tier").map((value) => <option key={value}>{value.replaceAll("_", " ")}</option>)}
          </select>
        </label>
        <div className="row-count">
          <strong>{filtered.length.toLocaleString()}</strong>
          <span>ranked candidates</span>
        </div>
      </div>

      <div className="table-wrap panel">
        <table>
          <thead>
            <tr>
              <th>Rank</th><th>ID</th><th>Team</th><th>Type</th><th>Race</th><th>Review tier</th><th>Signal</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row, index) => (
              <tr key={row.maneuver_id} className={row.maneuver_id === "413" ? "featured-row" : ""}>
                <td>{index + 1}</td>
                <td><Link href={`/maneuver/${row.maneuver_id}`}>{row.maneuver_id}</Link></td>
                <td>{row.team}</td>
                <td>{row.maneuver_type.replaceAll("_", " ")}</td>
                <td>{row.canonical_race_id.replaceAll("_", " ")}</td>
                <td><span className="badge">{row.review_tier.replaceAll("_", " ")}</span></td>
                <td>{row.demo_triage_score ? Number(row.demo_triage_score).toFixed(3) : "n/a"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
