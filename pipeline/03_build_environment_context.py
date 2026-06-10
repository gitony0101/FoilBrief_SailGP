#!/usr/bin/env python
"""Build supplementary environment context from externalized inputs.

Raw SailGP challenge data is not committed to this repository. When raw
telemetry, race metadata, and processed maneuver inputs are available
separately, this script reproduces supplementary environment-context artifacts.
Small curated runtime assets are already committed under
``apps/web/public/foilbrief-data`` for the web demo.

Environment context does not assign causality.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import datetime as dt
import shutil
from typing import List, Dict, Any

import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "external_pipeline_inputs" / "environment_work"
TELEMETRY_PATH = ROOT / "external_pipeline_inputs" / "telemetry.csv"
RACE_METADATA_PATH = ROOT / "external_pipeline_inputs" / "race_metadata_clean.csv"
MANEUVERS_PATH = ROOT / "external_pipeline_inputs" / "processed" / "maneuvers_v1_refined_fixed.parquet"
LOCATION_SOURCES_PATH = ROOT / "external_pipeline_inputs" / "location_sources.json"
OUTPUT_DIR = ROOT / "outputs" / "environment_context"
WEB_OUT = ROOT / "apps" / "web" / "public" / "foilbrief-data" / "environment_context"

# ---------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------

def _ensure_dir(p: pathlib.Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _load_telemetry() -> pd.DataFrame:
    """Load externally supplied raw boat telemetry.
    Returns a DataFrame with `source_race_folder`, `datetime_utc` and
    `latitude`/`longitude` columns (standardised).
    """
    if TELEMETRY_PATH.suffix.lower() == ".parquet":
        df = pd.read_parquet(TELEMETRY_PATH)
    else:
        df = pd.read_csv(TELEMETRY_PATH)
    df["datetime_utc"] = pd.to_datetime(df["DATETIME"], utc=True, errors='coerce')
    # Detect latitude / longitude column names (case‑insensitive)
    lat_col = next((c for c in df.columns if "lat" in c.lower()), None)
    lon_col = next((c for c in df.columns if "lon" in c.lower()), None)
    if not lat_col or not lon_col:
        raise RuntimeError("Latitude or longitude column not found in telemetry CSVs")
    df = df.rename(columns={lat_col: "latitude", lon_col: "longitude"})
    return df


def _load_race_metadata() -> pd.DataFrame:
    df = pd.read_csv(RACE_METADATA_PATH)
    df = df.rename(columns={"race_label": "race_id"})
    return df

# ---------------------------------------------------------------------
# 1️⃣ Build race context base (if missing)
# ---------------------------------------------------------------------

def build_race_context_base() -> pd.DataFrame:
    telemetry = _load_telemetry()
    meta = _load_race_metadata()

    # Derive location from source_file path (e.g. "DataChallenge_Export/Bermuda/...")
    telemetry = telemetry.copy()
    telemetry["source_location"] = telemetry["source_file"].str.extract(r"DataChallenge_Export/([^/]+)/")[0]
    telemetry["canonical_race_id"] = telemetry["source_location"] + "_" + telemetry["source_race_folder"].astype(str)

    # Derive venue from metadata source_file path
    meta["venue_guess"] = meta["source_file"].str.extract(r"DataChallenge_Export/([^/]+)/")[0]

    records = []
    for canonical_race_id, grp in telemetry.groupby("canonical_race_id"):
        rows = len(grp)
        boat_cnt = grp["boat"].nunique() if "boat" in grp.columns else grp["BOAT"].nunique()
        min_lat, max_lat = grp["latitude"].min(), grp["latitude"].max()
        min_lon, max_lon = grp["longitude"].min(), grp["longitude"].max()
        center_lat = grp["latitude"].median()
        center_lon = grp["longitude"].median()
        start = grp["datetime_utc"].min()
        end = grp["datetime_utc"].max()
        location = grp["source_location"].iloc[0]
        race_folder = grp["source_race_folder"].iloc[0]
        # Match metadata on venue + race_label
        md_row = meta[(meta["venue_guess"] == location) & (meta["race_id"] == race_folder)]
        event_name = location  # derive event from location (Bermuda / Halifax)
        venue_guess = location
        source_conf = 1.0 if not md_row.empty else 0.5
        records.append({
            "race_id": canonical_race_id,
            "event_name": event_name,
            "venue_guess": venue_guess,
            "race_start_utc": start,
            "race_end_utc": end,
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon,
            "course_center_lat": center_lat,
            "course_center_lon": center_lon,
            "telemetry_rows": rows,
            "boat_count": boat_cnt,
            "source_confidence": source_conf,
        })
    out = pd.DataFrame(records)
    out_path = WORK_DIR / "processed" / "race_context_base.parquet"
    _ensure_dir(out_path.parent)
    out.to_parquet(out_path, index=False)
    return out

# ---------------------------------------------------------------------
# 2️⃣ Open‑Meteo fetch helpers
# ---------------------------------------------------------------------

def fetch_open_meteo_weather(lat: float, lon: float, start: dt.date, end: dt.date) -> (str, pd.DataFrame, str):
    # Use the archive (historical) API, not forecast — forecast only covers ~14 days.
    # https://open-meteo.com/en/docs/historical-weather-api
    base = "https://archive-api.open-meteo.com/v1/archive"
    hourly = [
        "temperature_2m",
        "relative_humidity_2m",
        "pressure_msl",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "precipitation",
        "cloud_cover",
        "wave_height",
        "wave_direction",
        "wave_period",
        "wind_wave_height",
        "swell_wave_height",
    ]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": "UTC",
        "hourly": ",".join(hourly),
        "wind_speed_unit": "ms",   # request m/s instead of default km/h
    }
    try:
        r = requests.get(base, params=params, timeout=30)
        r.raise_for_status()
        raw = r.text
        payload = r.json()
        df = pd.DataFrame(payload.get("hourly", {}))
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], utc=True)
        # Convert any km/h wind columns to m/s if unit parameter was ignored
        for col in ["wind_speed_10m", "wind_gusts_10m"]:
            if col in df.columns and df[col].max() > 80:
                df[col] = df[col] / 3.6
        return raw, df, ""
    except Exception as e:
        return "", pd.DataFrame(), f"Open‑Meteo error: {e}"


def cache_open_meteo(race: pd.Series, raw_dir: pathlib.Path, proc_dir: pathlib.Path, force: bool) -> str:
    raw_path = raw_dir / f"{race['race_id']}_open_meteo.json"
    proc_path = proc_dir / f"{race['race_id']}_open_meteo.parquet"
    if proc_path.exists() and not force:
        return f"Open‑Meteo cached for {race['race_id']}"
    lat = float(race["course_center_lat"])
    lon = float(race["course_center_lon"])
    start = race["race_start_utc"].date()
    end = race["race_end_utc"].date()
    raw, df, log = fetch_open_meteo_weather(lat, lon, start, end)
    if raw:
        _ensure_dir(raw_path.parent)
        raw_path.write_text(raw, encoding="utf-8")
    if not df.empty:
        _ensure_dir(proc_path.parent)
        df.to_parquet(proc_path, index=False)
        return f"Fetched Open‑Meteo for {race['race_id']}"
    else:
        return f"Open‑Meteo fetch failed for {race['race_id']}: {log}"

# ---------------------------------------------------------------------
# 3️⃣ NOAA NDBC fetch (simple raw download & parquet conversion)
# ---------------------------------------------------------------------

def download_ndbc_station(station_id: str, year: int, raw_dir: pathlib.Path) -> pathlib.Path | None:
    url = f"https://www.ndbc.noaa.gov/data/historical/stdmet/{station_id}h{year}.txt.gz"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return None
        dest = raw_dir / f"{station_id}_{year}.txt.gz"
        _ensure_dir(dest.parent)
        dest.write_bytes(r.content)
        return dest
    except Exception:
        return None


def fetch_ndbc_for_race(race: pd.Series, candidates: List[Dict[str, Any]], raw_dir: pathlib.Path, proc_dir: pathlib.Path, force: bool) -> str:
    start_year = race["race_start_utc"].year
    end_year = race["race_end_utc"].year
    for cand in sorted(candidates, key=lambda x: x.get("priority", 999)):
        station = cand["station_id"]
        raw_paths: List[pathlib.Path] = []
        for yr in range(start_year, end_year + 1):
            raw_path = raw_dir / f"{station}_{yr}.txt.gz"
            if not raw_path.exists() or force:
                rp = download_ndbc_station(station, yr, raw_dir)
                if rp:
                    raw_paths.append(rp)
            else:
                raw_paths.append(raw_path)
        if not raw_paths:
            continue
        frames = []
        for rp in raw_paths:
            try:
                df = pd.read_csv(
                    rp,
                    compression="gzip",
                    delim_whitespace=True,
                    comment="#",
                    na_values=["99", "999", "9999", "MM"],
                )
                frames.append(df)
            except Exception:
                continue
        if not frames:
            continue
        full = pd.concat(frames, ignore_index=True)
        # Attempt to build a datetime column if standard columns are present
        dt_cols = {"YY", "MM", "DD", "hh", "mm"}
        if dt_cols.issubset(set(full.columns)):
            full["datetime_utc"] = pd.to_datetime(
                full[["YY", "MM", "DD", "hh", "mm"]].astype(str).agg("-".join, axis=1),
                format="%y-%m-%d-%H-%M",
                utc=True,
                errors="coerce",
            )
            full = full.drop(columns=["YY", "MM", "DD", "hh", "mm"], errors="ignore")
        out_path = proc_dir / f"{race['race_id']}_{station}_ndbc.parquet"
        if out_path.exists() and not force:
            return f"NDBC cached for {race['race_id']} ({station})"
        _ensure_dir(out_path.parent)
        full.to_parquet(out_path, index=False)
        return f"Fetched NDBC {station} for {race['race_id']}"
    return f"No NDBC data available for {race['race_id']}"

# ---------------------------------------------------------------------
# 4️⃣ Race‑level summary statistics
# ---------------------------------------------------------------------

def compute_race_summary(race_ctx: pd.DataFrame) -> pd.DataFrame:
    om_dir = WORK_DIR / "open_meteo" / "processed"
    ndbc_dir = WORK_DIR / "ndbc" / "processed"
    summaries = []
    for _, r in race_ctx.iterrows():
        # Open‑Meteo — use all hourly data for the race date(s)
        om_path = om_dir / f"{r['race_id']}_open_meteo.parquet"
        if om_path.exists():
            om = pd.read_parquet(om_path)
            # Use all rows (API already constrains to race date range)
            om_win = om
            rows_om = len(om_win)
        else:
            om_win = pd.DataFrame()
            rows_om = 0
        # NDBC (first matching file for this race)
        ndbc_matches = list(ndbc_dir.glob(f"{r['race_id']}_*_ndbc.parquet"))
        if ndbc_matches:
            ndbc = pd.read_parquet(ndbc_matches[0])
            ndbc_win = ndbc  # use all available buoy observations
            rows_ndbc = len(ndbc_win)
            station_used = ndbc_matches[0].stem.split("_")[1]
        else:
            ndbc_win = pd.DataFrame()
            rows_ndbc = 0
            station_used = ""
        # Helper for safe statistics
        def _mean(df, col):
            return df[col].mean() if col in df.columns else np.nan
        def _max(df, col):
            return df[col].max() if col in df.columns else np.nan
        def _median(df, col):
            return df[col].median() if col in df.columns else np.nan
        summary = {
            **r.to_dict(),
            "open_meteo_wind_speed_mean": _mean(om_win, "wind_speed_10m"),
            "open_meteo_wind_speed_max": _max(om_win, "wind_speed_10m"),
            "open_meteo_wind_direction_median": _median(om_win, "wind_direction_10m"),
            "open_meteo_wind_gust_max": _max(om_win, "wind_gusts_10m"),
            "open_meteo_pressure_mean": _mean(om_win, "pressure_msl"),
            "open_meteo_temperature_mean": _mean(om_win, "temperature_2m"),
            "open_meteo_wave_height_mean": _mean(om_win, "wave_height"),
            "open_meteo_wave_height_max": _max(om_win, "wave_height"),
            "open_meteo_rows_used": rows_om,
            "ndbc_wind_speed_mean": _mean(ndbc_win, "WSPD"),
            "ndbc_wind_speed_max": _max(ndbc_win, "WSPD"),
            "ndbc_wind_direction_median": _median(ndbc_win, "WDIR"),
            "ndbc_gust_max": _max(ndbc_win, "GST"),
            "ndbc_wave_height_mean": _mean(ndbc_win, "WVHT"),
            "ndbc_wave_height_max": _max(ndbc_win, "WVHT"),
            "ndbc_pressure_mean": _mean(ndbc_win, "PRES"),
            "ndbc_air_temp_mean": _mean(ndbc_win, "ATMP"),
            "ndbc_water_temp_mean": _mean(ndbc_win, "WTMP"),
            "ndbc_rows_used": rows_ndbc,
            "ndbc_station_used": station_used,
            "environment_source_confidence": (rows_om > 0) + (rows_ndbc > 0),
            "environment_context_note": "",
        }
        summaries.append(summary)
    out_df = pd.DataFrame(summaries)
    out_path = WORK_DIR / "processed" / "race_environment_context.parquet"
    _ensure_dir(out_path.parent)
    out_df.to_parquet(out_path, index=False)
    return out_df

# ---------------------------------------------------------------------
# 5️⃣ Manoeuvre‑level join (nearest hourly observation, max 90 min diff)
# ---------------------------------------------------------------------

def join_maneuver_environment() -> None:
    # Locate manoeuvre file (prefer refined versions)
    candidates = [MANEUVERS_PATH]
    mane_path = next((p for p in candidates if p.exists()), None)
    if not mane_path:
        print("No manoeuvre file found – skipping manoeuvre‑level join.")
        return
    mane = pd.read_parquet(mane_path)
    if "center_time" not in mane.columns:
        print("Manoeuvre data lacks 'center_time' column – cannot join.")
        return
    mane["center_time"] = pd.to_datetime(mane["center_time"], utc=True)
    # Use canonical_race_id if available, else build from source_location + race_id
    if "canonical_race_id" not in mane.columns or mane["canonical_race_id"].isna().all():
        # Build canonical from source_file path
        mane["_location"] = mane["source_file"].str.extract(r"DataChallenge_Export/([^/]+)/")[0]
        mane["canonical_race_id"] = mane["_location"] + "_" + mane["race_id"].astype(str)

    # Load weather tables into dictionaries keyed by canonical race_id
    om_dict = {}
    for p in (WORK_DIR / "open_meteo" / "processed").glob("*_open_meteo.parquet"):
        # File name format: {canonical_race_id}_open_meteo.parquet
        race_key = p.stem.rsplit("_open_meteo", 1)[0]
        om_dict[race_key] = pd.read_parquet(p)

    ndbc_dict: Dict[str, List[pd.DataFrame]] = {}
    for p in (WORK_DIR / "ndbc" / "processed").glob("*_ndbc.parquet"):
        # File name format: {canonical_race_id}_{station}_ndbc.parquet
        parts = p.stem.rsplit("_", 1)  # remove _ndbc
        if len(parts) >= 1:
            remainder = parts[0]
            # The canonical_race_id has format like "Bermuda_Race_2"
            # Find where the station name starts by trying splits
            for sep_idx in range(1, 4):  # try 1, 2, 3 underscores
                race_key = "_".join(remainder.split("_")[:sep_idx + 1])
                if race_key.endswith(tuple(f"_Race_{i}" for i in range(1, 11))):
                    ndbc_dict.setdefault(race_key, []).append(pd.read_parquet(p))
                    break
            else:
                # fallback: use everything before the last underscore segment as race key
                ndbc_dict.setdefault(remainder.rsplit("_", 1)[0], []).append(pd.read_parquet(p))

    rows = []
    for _, m in mane.iterrows():
        race_id = m["canonical_race_id"]
        short_race_id = m.get("race_id", "")
        # Open‑Meteo nearest row
        om_df = om_dict.get(race_id)
        if om_df is not None:
            diffs = (om_df["time"] - m["center_time"]).abs()
            idx = diffs.idxmin()
            nearest = om_df.loc[idx]
            nearest_time = nearest["time"]
            delta_min = diffs.min().total_seconds() / 60.0
        else:
            nearest = pd.Series()
            nearest_time = pd.NaT
            delta_min = np.nan
        # NDBC – pick first station with a row within 90 min
        ndbc_station = ""
        ndbc_row = pd.Series()
        if race_id in ndbc_dict:
            for df in ndbc_dict[race_id]:
                diffs_n = (df["datetime_utc"] - m["center_time"]).abs()
                if diffs_n.empty:
                    continue
                min_idx = diffs_n.idxmin()
                if diffs_n[min_idx].total_seconds() / 60.0 <= 90:
                    ndbc_row = df.loc[min_idx]
                    # Extract station from filename lookup
                    ndbc_station = "unknown"
                    break
        # Determine environment_join_confidence
        has_om = not pd.isna(nearest_time)
        has_ndbc = ndbc_station != ""
        join_conf = 0.0
        if has_om and has_ndbc:
            join_conf = 3.0
        elif has_om:
            join_conf = 2.0
        elif has_ndbc:
            join_conf = 1.0

        out = {
            "maneuver_id": m.get("maneuver_id"),
            "race_id": short_race_id,
            "canonical_race_id": race_id,
            "team": m.get("team"),
            "boat": m.get("boat"),
            "maneuver_type": m.get("maneuver_type"),
            "center_time": m["center_time"],
            "nearest_weather_time_utc": nearest_time,
            "weather_time_delta_minutes": delta_min,
            "open_meteo_wind_speed_10m": nearest.get("wind_speed_10m", np.nan),
            "open_meteo_wind_direction_10m": nearest.get("wind_direction_10m", np.nan),
            "open_meteo_wind_gusts_10m": nearest.get("wind_gusts_10m", np.nan),
            "open_meteo_pressure_msl": nearest.get("pressure_msl", np.nan),
            "open_meteo_temperature_2m": nearest.get("temperature_2m", np.nan),
            "open_meteo_wave_height": nearest.get("wave_height", np.nan),
            "ndbc_station_used": ndbc_station,
            "ndbc_wind_speed": ndbc_row.get("WSPD", np.nan),
            "ndbc_wind_direction": ndbc_row.get("WDIR", np.nan),
            "ndbc_gust": ndbc_row.get("GST", np.nan),
            "ndbc_wave_height": ndbc_row.get("WVHT", np.nan),
            "ndbc_pressure": ndbc_row.get("PRES", np.nan),
            "ndbc_air_temp": ndbc_row.get("ATMP", np.nan),
            "ndbc_water_temp": ndbc_row.get("WTMP", np.nan),
            "environment_join_confidence": join_conf,
        }
        rows.append(out)
    out_df = pd.DataFrame(rows)
    out_path = WORK_DIR / "processed" / "maneuver_environment_context.parquet"
    _ensure_dir(out_path.parent)
    out_df.to_parquet(out_path, index=False)

# ---------------------------------------------------------------------
# 6️⃣ Reporting utilities
# ---------------------------------------------------------------------

def write_race_summary_md(summary: pd.DataFrame) -> None:
    out_md = OUTPUT_DIR / "race_environment_context_summary.md"
    _ensure_dir(out_md.parent)
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Race‑level Environment Summary\n\n")
        for _, r in summary.iterrows():
            f.write(f"## {r['race_id']}\n")
            f.write(f"- Event: {r.get('event_name','')}\n")
            f.write(f"- Venue guess: {r.get('venue_guess','')}\n")
            f.write(f"- Time window: {r['race_start_utc']} – {r['race_end_utc']}\n")
            f.write(f"- Open‑Meteo rows used: {int(r.get('open_meteo_rows_used',0))}\n")
            f.write(f"- NDBC rows used: {int(r.get('ndbc_rows_used',0))}\n\n")


def write_audit_md(om_logs: List[str], ndbc_logs: List[str]) -> None:
    audit_path = OUTPUT_DIR / "environment_data_audit.md"
    _ensure_dir(audit_path.parent)
    with audit_path.open("w", encoding="utf-8") as f:
        f.write("# Environment Data Audit\n\n")
        f.write("## Open‑Meteo fetch log\n\n")
        for l in om_logs:
            f.write(f"- {l}\n")
        f.write("\n## NDBC fetch log\n\n")
        for l in ndbc_logs:
            f.write(f"- {l}\n")

# ---------------------------------------------------------------------
def main() -> int:
    global WORK_DIR, TELEMETRY_PATH, RACE_METADATA_PATH, MANEUVERS_PATH, LOCATION_SOURCES_PATH, OUTPUT_DIR
    parser = argparse.ArgumentParser(description="Build supplementary FoilBrief environment context.")
    parser.add_argument("--telemetry", type=pathlib.Path, default=TELEMETRY_PATH, help="External raw SailGP telemetry CSV or parquet file.")
    parser.add_argument("--race-metadata", type=pathlib.Path, default=RACE_METADATA_PATH, help="External race metadata CSV.")
    parser.add_argument("--maneuvers", type=pathlib.Path, default=MANEUVERS_PATH, help="External processed maneuver parquet file.")
    parser.add_argument("--location-sources", type=pathlib.Path, default=LOCATION_SOURCES_PATH, help="External JSON configuration for public environment sources.")
    parser.add_argument("--work-dir", type=pathlib.Path, default=WORK_DIR, help="External/cache working directory for fetched and intermediate data.")
    parser.add_argument("--output-dir", type=pathlib.Path, default=OUTPUT_DIR, help="Directory for generated environment summaries and audits.")
    parser.add_argument("--publish-web-assets", action="store_true", help="Copy generated context table files into the web app public data directory.")
    parser.add_argument("--force", action="store_true", help="re-download public environment data even if cached")
    args = parser.parse_args()
    TELEMETRY_PATH = args.telemetry.resolve()
    RACE_METADATA_PATH = args.race_metadata.resolve()
    MANEUVERS_PATH = args.maneuvers.resolve()
    LOCATION_SOURCES_PATH = args.location_sources.resolve()
    WORK_DIR = args.work_dir.resolve()
    OUTPUT_DIR = args.output_dir.resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Race context
    race_ctx = build_race_context_base()

    # Load location configuration (must exist)
    loc_cfg_path = LOCATION_SOURCES_PATH
    if not loc_cfg_path.is_file():
        print("Location configuration not found – aborting external fetch.")
        return 1
    loc_cfg = json.loads(loc_cfg_path.read_text())

    om_raw = WORK_DIR / "open_meteo" / "raw"
    om_proc = WORK_DIR / "open_meteo" / "processed"
    ndbc_raw = WORK_DIR / "ndbc" / "raw"
    ndbc_proc = WORK_DIR / "ndbc" / "processed"
    for d in [om_raw, om_proc, ndbc_raw, ndbc_proc]:
        _ensure_dir(d)

    # 2. Open-Meteo fetch per race
    om_logs = []
    for _, race in tqdm(race_ctx.iterrows(), total=len(race_ctx), desc="Open‑Meteo fetch"):
        msg = cache_open_meteo(race, om_raw, om_proc, args.force)
        om_logs.append(msg)

    # 3. NDBC fetch per race using location config
    ndbc_logs = []
    for _, race in tqdm(race_ctx.iterrows(), total=len(race_ctx), desc="NDBC fetch"):
        venue_key = race["race_id"].split("_")[0].lower()
        venue_cfg = loc_cfg.get(venue_key, {})
        candidates = venue_cfg.get("ndbc_candidates", [])
        msg = fetch_ndbc_for_race(race, candidates, ndbc_raw, ndbc_proc, args.force)
        ndbc_logs.append(msg)

    # 4. Race-level summary
    race_summary = compute_race_summary(race_ctx)
    write_race_summary_md(race_summary)

    # 5. Maneuver-level join
    join_maneuver_environment()

    # 6. Runtime table generation
    demo_path_csv = OUTPUT_DIR / "maneuver_environment_context_web.csv"
    demo_path_json = OUTPUT_DIR / "maneuver_environment_context_web.json"
    demo_path_md = OUTPUT_DIR / "demo_environment_context_table.md"
    _ensure_dir(demo_path_csv.parent)
    try:
        demo_df = pd.read_parquet(WORK_DIR / "processed" / "maneuver_environment_context.parquet")
        if not demo_df.empty:
            demo_sample = demo_df.sample(n=min(10, len(demo_df)), random_state=42)
            demo_cols = [
                "race_id",
                "venue_guess",
                "team",
                "boat",
                "maneuver_type",
                "center_time",
                "weather_time_delta_minutes",
                "open_meteo_wind_speed_10m",
                "open_meteo_wind_direction_10m",
                "open_meteo_wave_height",
                "environment_context_note",
            ]
            demo_sample = demo_sample[[c for c in demo_cols if c in demo_sample.columns]]
            demo_df.to_csv(demo_path_csv, index=False)
            demo_df.to_json(demo_path_json, orient="records", date_format="iso", indent=2)
            with demo_path_md.open("w", encoding="utf-8") as f_md:
                f_md.write("# Demo Environment Context Table\n\n")
                f_md.write(demo_sample.to_markdown(index=False))
                f_md.write("\n")
    except Exception as e:
        print(f"Demo table generation failed: {e}")

    # 6️⃣ Audit report
    write_audit_md(om_logs, ndbc_logs)
    if args.publish_web_assets:
        WEB_OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy2(demo_path_csv, WEB_OUT / demo_path_csv.name)
        shutil.copy2(demo_path_json, WEB_OUT / demo_path_json.name)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
