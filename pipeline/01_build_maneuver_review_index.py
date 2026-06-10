#!/usr/bin/env python3
"""Build the FoilBrief maneuver review index from externalized inputs.

Raw SailGP challenge data and intermediate parquet files are not committed to
this repository. When those inputs are available separately, this script
reproduces the derived review-index artifacts. Small curated runtime assets are
already committed under ``apps/web/public/foilbrief-data`` for the web demo.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "maneuver_index"
DEMO = ROOT / "outputs" / "demo_case_413"
WEB_OUT = ROOT / "apps" / "web" / "public" / "foilbrief-data" / "maneuver_index"
DATA = ROOT / "external_pipeline_inputs" / "processed"
INPUTS = {
    "refined maneuver table": DATA / "maneuvers_v1_refined_fixed.parquet",
    "loss metrics table": DATA / "maneuver_loss_metrics.parquet",
    "Stage 2B candidate table": DATA / "stage2b_demo_candidates.parquet",
}
PREVIOUS_STAGES = {
    "refined maneuver table": "the externalized refined maneuver-table build",
    "loss metrics table": "the externalized fleet-baseline and loss-metrics build",
    "Stage 2B candidate table": "the externalized demo-candidate build",
}
CARD_PATH = DEMO / "coach_loss_card.md"
PANEL_PATH = DEMO / "05_demo_panel.png"
MODEL_SUFFIXES = {".pkl", ".pickle", ".joblib", ".pt", ".pth", ".onnx", ".h5"}
FORBIDDEN = [
    "caused", "proved", "optimal", "guaranteed", "exact time loss",
    "exact seconds lost", "true gybe", "true tack", "autonomous decision",
    "control command", "best possible maneuver",
]
INDEX_COLUMNS = [
    "maneuver_id", "canonical_race_id", "source_location", "team", "boat",
    "maneuver_type", "center_time", "classification_confidence",
    "baseline_confidence", "loss_confidence", "demo_triage_score",
    "relative_speed_loss_area", "abs_relative_vmg_loss_area",
    "time_below_fleet_speed", "time_below_fleet_vmg", "recovery_time_to_90",
    "recovery_time_to_95", "data_gap_near_center", "vmg_sign_mismatch_flag",
    "unrecovered_flag", "strict_demo_candidate", "review_tier",
    "recommended_use", "final_card_available", "final_card_path",
]
USE_PRIORITY = {"primary_demo": 0, "candidate_review": 1, "backup_review": 2, "archive_only": 3, "exclude": 4}
TIER_PRIORITY = {"high_review_priority": 0, "medium_review_priority": 1, "low_review_priority": 2, "exclude_from_demo": 3}


def snapshot_models() -> set[str]:
    return {str(path.relative_to(ROOT)) for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in MODEL_SUFFIXES}


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def require_inputs() -> None:
    missing = [(name, path) for name, path in INPUTS.items() if not path.exists()]
    if missing:
        details = "\n".join(f"- Missing {name}: {display_path(path)}. Reproduce {PREVIOUS_STAGES[name]}." for name, path in missing)
        raise FileNotFoundError(f"Stage 3A cannot run because accepted processed inputs are missing:\n{details}")


def json_value(value: object) -> object:
    if value is None or value is pd.NA or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def records(frame: pd.DataFrame) -> list[dict[str, object]]:
    return [{key: json_value(value) for key, value in row.items()} for row in frame.to_dict(orient="records")]


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    clean = frame.copy()
    for column in clean:
        clean[column] = clean[column].map(
            lambda value: "" if pd.isna(value) else f"{value:.3f}" if isinstance(value, (float, np.floating)) else str(value)
        )
    lines = [
        "| " + " | ".join(clean.columns) + " |",
        "|" + "|".join(["---"] * len(clean.columns)) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in clean.astype(str).values.tolist())
    return "\n".join(lines)


def build_index() -> pd.DataFrame:
    refined = pd.read_parquet(INPUTS["refined maneuver table"])
    losses = pd.read_parquet(INPUTS["loss metrics table"])
    candidates = pd.read_parquet(INPUTS["Stage 2B candidate table"])
    if refined["maneuver_id"].duplicated().any():
        raise ValueError("The refined maneuver table must contain one row per maneuver_id before Stage 3A can run.")

    base_columns = [
        "maneuver_id", "canonical_race_id", "source_location", "team", "boat",
        "maneuver_type", "center_time", "classification_confidence",
        "classification_confidence_label", "data_gap_near_center",
    ]
    index = refined[base_columns].copy()
    loss_columns = [
        "maneuver_id", "baseline_confidence", "loss_confidence",
        "relative_speed_loss_area", "time_below_fleet_speed", "time_below_fleet_vmg",
        "recovery_time_to_90", "recovery_time_to_95", "pre_window_n",
        "post_window_n", "baseline_sample_count_median",
    ]
    index = index.merge(losses[loss_columns], on="maneuver_id", how="left", validate="one_to_one")
    candidate_columns = [
        "maneuver_id", "demo_candidate_score", "abs_relative_vmg_loss_area",
        "suspicious_vmg_sign_mismatch",
    ]
    index = index.merge(candidates[candidate_columns], on="maneuver_id", how="left", validate="one_to_one")
    index = index.rename(columns={
        "demo_candidate_score": "demo_triage_score",
        "suspicious_vmg_sign_mismatch": "vmg_sign_mismatch_flag",
    })
    index["strict_demo_candidate"] = index["demo_triage_score"].notna()
    index["vmg_sign_mismatch_flag"] = index["vmg_sign_mismatch_flag"].eq(True)
    index["data_gap_near_center"] = index["data_gap_near_center"].fillna(True).astype(bool)
    index["unrecovered_flag"] = index["recovery_time_to_90"].isna() & index["strict_demo_candidate"]

    supported_confidence = (
        index["baseline_confidence"].isin(["high", "medium"])
        & index["loss_confidence"].isin(["high", "medium"])
    )
    low_classification = (
        index["classification_confidence_label"].eq("low")
        | index["maneuver_type"].eq("low_confidence_turn")
        | index["classification_confidence"].lt(0.7)
    )
    insufficient_evidence = (
        index["pre_window_n"].fillna(0).lt(3)
        | index["post_window_n"].fillna(0).lt(5)
        | index["baseline_sample_count_median"].fillna(0).lt(3)
    )
    excluded = (
        index["data_gap_near_center"]
        | ~supported_confidence
        | low_classification
        | index["vmg_sign_mismatch_flag"]
        | insufficient_evidence
    )
    eligible = ~excluded & index["demo_triage_score"].notna()
    threshold = index.loc[eligible, "demo_triage_score"].quantile(0.75)

    index["review_tier"] = "low_review_priority"
    index.loc[supported_confidence & ~excluded & index["demo_triage_score"].notna(), "review_tier"] = "medium_review_priority"
    index.loc[eligible & index["demo_triage_score"].ge(threshold), "review_tier"] = "high_review_priority"
    index.loc[excluded, "review_tier"] = "exclude_from_demo"

    index["recommended_use"] = index["review_tier"].map({
        "high_review_priority": "candidate_review",
        "medium_review_priority": "backup_review",
        "low_review_priority": "archive_only",
        "exclude_from_demo": "exclude",
    })
    index.loc[index["maneuver_id"].eq(413), "recommended_use"] = "primary_demo"
    card_available = CARD_PATH.exists() and PANEL_PATH.exists()
    index["final_card_available"] = index["maneuver_id"].eq(413) & card_available
    index["final_card_path"] = ""
    if card_available:
        index.loc[index["maneuver_id"].eq(413), "final_card_path"] = display_path(CARD_PATH)
    index["center_time"] = pd.to_datetime(index["center_time"], utc=True, errors="coerce")
    return index[INDEX_COLUMNS].sort_values("maneuver_id").reset_index(drop=True)


def sorted_candidates(index: pd.DataFrame, limit: int) -> pd.DataFrame:
    ranked = index.copy()
    ranked["_use_priority"] = ranked["recommended_use"].map(USE_PRIORITY)
    ranked["_tier_priority"] = ranked["review_tier"].map(TIER_PRIORITY)
    ranked = ranked.sort_values(
        ["_use_priority", "_tier_priority", "demo_triage_score", "maneuver_id"],
        ascending=[True, True, False, True],
        na_position="last",
    )
    selected = ranked.head(limit)
    if index["maneuver_id"].eq(413).any() and not selected["maneuver_id"].eq(413).any():
        selected = pd.concat([index[index["maneuver_id"].eq(413)], selected.head(limit - 1)], ignore_index=True)
    return selected.drop(columns=["_use_priority", "_tier_priority"], errors="ignore").reset_index(drop=True)


def build_team_summary(index: pd.DataFrame) -> pd.DataFrame:
    work = index.assign(
        high=index["review_tier"].eq("high_review_priority"),
        medium=index["review_tier"].eq("medium_review_priority"),
        low=index["review_tier"].eq("low_review_priority"),
        exclude=index["review_tier"].eq("exclude_from_demo"),
    )
    return work.groupby(["team", "maneuver_type"], dropna=False).agg(
        count=("maneuver_id", "count"),
        high_review_priority_count=("high", "sum"),
        medium_review_priority_count=("medium", "sum"),
        low_review_priority_count=("low", "sum"),
        exclude_count=("exclude", "sum"),
        median_demo_triage_score=("demo_triage_score", "median"),
        max_demo_triage_score=("demo_triage_score", "max"),
    ).reset_index()


def plot_counts(index: pd.DataFrame) -> None:
    counts = index["maneuver_type"].value_counts().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(counts.index.astype(str), counts.values)
    ax.set(title="All candidate maneuver counts by type", xlabel="Maneuver type", ylabel="Count")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "01_maneuver_counts_by_type.png", dpi=160)
    plt.close(fig)


def plot_score_distribution(index: pd.DataFrame) -> None:
    scores = index.loc[index["review_tier"].ne("exclude_from_demo"), "demo_triage_score"].dropna()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(scores, bins=20)
    ax.set(title="Eligible estimated review signal distribution", xlabel="Demo triage score", ylabel="Candidate maneuver count")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "02_review_score_distribution.png", dpi=160)
    plt.close(fig)


def plot_top_candidates(index: pd.DataFrame) -> None:
    top = sorted_candidates(index[index["demo_triage_score"].notna()], 15).sort_values("demo_triage_score")
    labels = top.apply(lambda row: f"ID {row['maneuver_id']} | {row['team']} | {str(row['maneuver_type']).replace('_', ' ')}", axis=1)
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(labels, top["demo_triage_score"])
    ax.set(title="Top review candidates", xlabel="Demo triage score")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "03_top_review_candidates.png", dpi=160)
    plt.close(fig)


def plot_team_coverage(index: pd.DataFrame) -> None:
    table = pd.crosstab(index["team"], index["maneuver_type"])
    fig, ax = plt.subplots(figsize=(12, 7))
    image = ax.imshow(table.values, aspect="auto")
    ax.set_xticks(range(len(table.columns)), labels=[str(value).replace("_", " ") for value in table.columns], rotation=20)
    ax.set_yticks(range(len(table.index)), labels=table.index)
    ax.set(title="Team coverage by candidate maneuver type", xlabel="Maneuver type", ylabel="Team")
    for row in range(table.shape[0]):
        for column in range(table.shape[1]):
            ax.text(column, row, int(table.iloc[row, column]), ha="center", va="center")
    fig.colorbar(image, ax=ax, label="Count")
    fig.tight_layout()
    fig.savefig(OUT / "04_team_coverage_summary.png", dpi=160)
    plt.close(fig)


def plot_workflow() -> None:
    labels = [
        "All candidate\nmaneuvers",
        "All-maneuver\nreview index",
        "Selected\nmaneuver 413",
        "Coach Loss Card",
    ]
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)
    ax.axis("off")
    positions = [0.5, 4.0, 7.5, 11.0]
    for position, label in zip(positions, labels):
        ax.add_patch(FancyBboxPatch((position, 1.25), 2.5, 1.4, boxstyle="round,pad=0.15"))
        ax.text(position + 1.25, 1.95, label, ha="center", va="center", fontsize=12)
    for position in positions[:-1]:
        ax.add_patch(FancyArrowPatch((position + 2.55, 1.95), (position + 3.4, 1.95), arrowstyle="->", mutation_scale=18))
    ax.set_title("FoilBrief analyst review workflow", fontsize=15)
    fig.tight_layout()
    fig.savefig(OUT / "05_index_to_card_workflow.png", dpi=160)
    plt.close(fig)


def write_summaries(index: pd.DataFrame, top_50: pd.DataFrame, team_summary: pd.DataFrame) -> None:
    type_counts = index["maneuver_type"].value_counts().sort_index()
    tier_counts = index["review_tier"].value_counts().reindex(TIER_PRIORITY, fill_value=0)
    top_columns = ["maneuver_id", "canonical_race_id", "team", "maneuver_type", "demo_triage_score", "review_tier", "recommended_use"]
    top_10 = sorted_candidates(index[index["demo_triage_score"].notna()], 10)[top_columns]
    lines = [
        "# All-Maneuver Review Index Summary", "",
        f"- Total candidate maneuvers: {len(index):,}",
        f"- Unique teams: {index['team'].nunique():,}",
        f"- Total races: {index['canonical_race_id'].nunique():,}", "",
        "## Counts By Maneuver Type", "",
        *[f"- `{name}`: {int(count)}" for name, count in type_counts.items()], "",
        "## Counts By Review Tier", "",
        *[f"- `{name}`: {int(count)}" for name, count in tier_counts.items()], "",
        "## Top 10 Review Candidates", "",
        markdown_table(top_10), "",
        "## Review Workflow", "",
        "FoilBrief detects every `maneuver_id` in the accepted refined maneuver table and attaches available fleet-relative scoring evidence before the analyst selects a deep-dive case.",
        "Maneuver `413` remains the single designated deep-dive demo case and links to its Coach Loss Card.",
        "Review scores are estimated fleet-relative review signals, not measured elapsed-time attribution. The human analyst decides which candidate maneuver is worth further review.", "",
    ]
    (OUT / "maneuver_index_summary.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "total_maneuvers": len(index),
        "unique_teams": int(index["team"].nunique()),
        "total_races": int(index["canonical_race_id"].nunique()),
        "counts_by_maneuver_type": {str(key): int(value) for key, value in type_counts.items()},
        "counts_by_review_tier": {str(key): int(value) for key, value in tier_counts.items()},
        "primary_demo_maneuver_id": 413,
        "primary_demo_final_card_available": bool(index.loc[index["maneuver_id"].eq(413), "final_card_available"].any()),
        "top_10_review_candidates": records(top_10),
        "team_maneuver_summary": records(team_summary),
        "notes": [
            "All maneuver_id values are indexed before the single deep-dive case is selected.",
            "Review scores are estimated fleet-relative review signals.",
            "The human analyst makes the final review decision.",
        ],
    }
    (OUT / "maneuver_index_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def validate(index: pd.DataFrame, refined_count: int, source_types: set[str], before_models: set[str], after_models: set[str]) -> bool:
    output_files = [path for path in OUT.rglob("*") if path.is_file()]
    markdown_files = [path for path in OUT.rglob("*.md")]
    unsafe_hits = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8").lower()
        unsafe_hits.extend(f"{path.name}: {term}" for term in FORBIDDEN if term in text)
    large_files = [str(path.relative_to(ROOT)) for path in output_files if path.stat().st_size > 10 * 1024 * 1024]
    type_checks = []
    for maneuver_type, label in [("tack", "candidate tack"), ("gybe", "candidate gybe"), ("mark_rounding", "mark rounding")]:
        source_has_type = maneuver_type in source_types
        output_has_type = index["maneuver_type"].eq(maneuver_type).any()
        type_checks.append((f"At least one {label} exists when present in source", not source_has_type or output_has_type, f"source_present={source_has_type}, output_present={output_has_type}"))
    checks = [
        ("Refined maneuver table exists", INPUTS["refined maneuver table"].exists(), display_path(INPUTS["refined maneuver table"])),
        ("Loss metrics table exists", INPUTS["loss metrics table"].exists(), display_path(INPUTS["loss metrics table"])),
        ("Stage 2B candidate table exists", INPUTS["Stage 2B candidate table"].exists(), display_path(INPUTS["Stage 2B candidate table"])),
        ("All-maneuver review index exists and is non-empty", (OUT / "all_maneuver_review_index.csv").exists() and len(index) > 0, f"rows={len(index)}"),
        ("Row count equals refined maneuver table row count", len(index) == refined_count, f"index={len(index)}, refined={refined_count}"),
        ("maneuver_id is unique", index["maneuver_id"].is_unique, f"unique={index['maneuver_id'].nunique()}"),
        ("Maneuver 413 exists", index["maneuver_id"].eq(413).any(), "primary demo case"),
        ("Maneuver 413 has final card available", bool(index.loc[index["maneuver_id"].eq(413), "final_card_available"].any()), display_path(CARD_PATH)),
        ("At least one team exists", index["team"].nunique() > 0, f"teams={index['team'].nunique()}"),
        *type_checks,
        ("No output file exceeds 10 MB", not large_files, f"files={large_files}"),
        ("Generated markdown uses accepted review language", not unsafe_hits, f"hits={unsafe_hits}"),
        ("No model artifacts are created", before_models == after_models, f"new={sorted(after_models - before_models)}"),
    ]
    passed = all(ok for _, ok, _ in checks)
    lines = [
        "# Stage 3A Validation Summary", "",
        f"- Overall validation: **{'PASS' if passed else 'FAIL'}**",
        f"- Checks passed: {sum(ok for _, ok, _ in checks)}/{len(checks)}", "",
        "| check | status | detail |", "|---|---|---|",
        *[f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |" for name, ok, detail in checks], "",
        "Stage 3A creates a compact analyst review index and does not create model artifacts.", "",
    ]
    (OUT / "stage3a_validation_summary.md").write_text("\n".join(lines), encoding="utf-8")
    return passed


def main() -> int:
    global DATA, OUT, DEMO, CARD_PATH, PANEL_PATH, INPUTS
    parser = argparse.ArgumentParser(description="Build the FoilBrief maneuver review index.")
    parser.add_argument("--processed-dir", type=Path, default=DATA, help="Directory containing externalized processed parquet inputs.")
    parser.add_argument("--output-dir", type=Path, default=OUT, help="Directory for generated analysis artifacts.")
    parser.add_argument("--demo-dir", type=Path, default=DEMO, help="Directory containing the generated Demo 413 card and panel.")
    parser.add_argument("--publish-web-assets", action="store_true", help="Copy curated runtime files into the web app public data directory.")
    args = parser.parse_args()

    DATA = args.processed_dir.resolve()
    OUT = args.output_dir.resolve()
    DEMO = args.demo_dir.resolve()
    INPUTS = {
        "refined maneuver table": DATA / "maneuvers_v1_refined_fixed.parquet",
        "loss metrics table": DATA / "maneuver_loss_metrics.parquet",
        "Stage 2B candidate table": DATA / "stage2b_demo_candidates.parquet",
    }
    CARD_PATH = DEMO / "coach_loss_card.md"
    PANEL_PATH = DEMO / "05_demo_panel.png"

    require_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    before_models = snapshot_models()
    refined = pd.read_parquet(INPUTS["refined maneuver table"], columns=["maneuver_id", "maneuver_type"])
    index = build_index()
    top_50 = sorted_candidates(index, 50)
    team_summary = build_team_summary(index)
    index.to_csv(OUT / "all_maneuver_review_index.csv", index=False)
    top_50.to_csv(OUT / "top_50_review_candidates.csv", index=False)
    team_summary.to_csv(OUT / "team_maneuver_summary.csv", index=False)
    plot_counts(index)
    plot_score_distribution(index)
    plot_top_candidates(index)
    plot_team_coverage(index)
    plot_workflow()
    write_summaries(index, top_50, team_summary)
    if args.publish_web_assets:
        WEB_OUT.mkdir(parents=True, exist_ok=True)
        for name in [
            "all_maneuver_review_index.csv",
            "top_50_review_candidates.csv",
            "team_maneuver_summary.csv",
            "maneuver_index_summary.md",
            "maneuver_index_summary.json",
        ]:
            shutil.copy2(OUT / name, WEB_OUT / name)
    after_models = snapshot_models()
    passed = validate(index, len(refined), set(refined["maneuver_type"].dropna().astype(str)), before_models, after_models)
    print(f"output_directory={display_path(OUT)}")
    print(f"maneuver_rows={len(index)}")
    print(f"unique_teams={index['team'].nunique()}")
    print(f"validation={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
