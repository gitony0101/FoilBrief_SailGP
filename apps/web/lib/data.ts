import fs from "node:fs/promises";
import path from "node:path";
import { parseCsv } from "@/lib/csv";
import type {
  CoachLossCard,
  DemoCaseSummary,
  EnvironmentContext,
  ManeuverIndexSummary,
  ManeuverRow,
  TimeLossReceipt,
} from "@/lib/types";

const dataRoot = path.join(process.cwd(), "public", "foilbrief-data");

async function readText(relativePath: string) {
  return fs.readFile(path.join(dataRoot, relativePath), "utf8");
}

async function readJson<T>(relativePath: string): Promise<T> {
  return JSON.parse(await readText(relativePath)) as T;
}

export async function getManeuvers() {
  const text = await readText("maneuver_index/all_maneuver_review_index.csv");
  return parseCsv<ManeuverRow>(text).sort(
    (a, b) => Number(b.demo_triage_score || -1) - Number(a.demo_triage_score || -1),
  );
}

export async function getManeuver(id: string) {
  return (await getManeuvers()).find((row) => row.maneuver_id === id) ?? null;
}

export async function loadEnvironmentContext() {
  return readJson<EnvironmentContext[]>(
    "environment_context/maneuver_environment_context_web.json",
  );
}

export async function getEnvironmentContextByManeuverId(id: string) {
  return (await loadEnvironmentContext()).find((row) => row.maneuver_id === id) ?? null;
}

export async function getSummary() {
  return readJson<ManeuverIndexSummary>("maneuver_index/maneuver_index_summary.json");
}

export async function getDemoBundle() {
  const [demoCaseSummary, timeLossReceipt, coachLossCard, coachLossCardMarkdown] =
    await Promise.all([
      readJson<DemoCaseSummary>("demo_case_413/demo_case_summary.json"),
      readJson<TimeLossReceipt>("demo_case_413/time_loss_receipt.json"),
      readJson<CoachLossCard>("demo_case_413/coach_loss_card.json"),
      readText("demo_case_413/coach_loss_card.md"),
    ]);

  return { demoCaseSummary, timeLossReceipt, coachLossCard, coachLossCardMarkdown };
}
