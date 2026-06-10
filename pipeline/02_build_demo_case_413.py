#!/usr/bin/env python3
"""Build the curated FoilBrief Demo 413 evidence package.

Raw SailGP challenge data and intermediate parquet files are externalized and
are not committed to this repository. With those inputs available separately,
this script reproduces the derived Demo 413 assets. The web demo already ships
with small curated runtime assets under ``apps/web/public/foilbrief-data``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "external_pipeline_inputs" / "processed"
REVIEW = ROOT / "external_pipeline_inputs" / "review"
WEB_OUT = ROOT / "apps" / "web" / "public" / "foilbrief-data" / "demo_case_413"
MODEL_SUFFIXES = {".pkl", ".pickle", ".joblib", ".pt", ".pth", ".onnx", ".h5"}
FORBIDDEN = ["caused", "proved", "optimal", "guaranteed", "should have", "true gybe", "exact time loss", "control command", "autonomous decision", "best possible maneuver"]
INPUTS = {
    "candidates": DATA / "stage2b_demo_candidates.parquet",
    "losses": DATA / "maneuver_loss_metrics.parquet",
    "baselines": DATA / "maneuver_fleet_baselines.parquet",
    "maneuvers": DATA / "maneuvers_v1_refined_fixed.parquet",
    "telemetry": DATA / "telemetry_1hz.parquet",
    "marks": DATA / "marks_1hz.parquet",
    "review_pack": REVIEW / "stage2c_manual_review_pack.md",
    "review_csv": REVIEW / "stage2c_manual_review_candidates.csv",
}
CONTROL_FIELDS = ["ANGLE_WING_ROT_deg", "ANGLE_WING_TWIST_deg", "ANGLE_RUDDER_deg", "ANGLE_DB_RAKE_P_deg", "ANGLE_DB_RAKE_S_deg", "ANGLE_DB_CANT_P_deg", "ANGLE_DB_CANT_S_deg"]


def snapshot_models():
    return {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in MODEL_SUFFIXES}


def display_path(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def location(path):
    text = str(path)
    return "Bermuda" if "Bermuda" in text else ("Halifax" if "Halifax" in text else "unknown")


def jvalue(v):
    if v is None or v is pd.NA or (isinstance(v, float) and np.isnan(v)): return None
    if isinstance(v, np.integer): return int(v)
    if isinstance(v, np.floating): return float(v)
    if isinstance(v, np.bool_): return bool(v)
    if isinstance(v, pd.Timestamp): return v.isoformat()
    return v


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, default=jvalue) + "\n", encoding="utf-8")


def prepare(mid):
    for name, path in INPUTS.items():
        if not path.exists(): raise FileNotFoundError(f"Missing required input {name}: {path}")
    c = pd.read_parquet(INPUTS["candidates"]); l = pd.read_parquet(INPUTS["losses"]); b = pd.read_parquet(INPUTS["baselines"]); m = pd.read_parquet(INPUTS["maneuvers"])
    t = pd.read_parquet(INPUTS["telemetry"]); marks = pd.read_parquet(INPUTS["marks"]); review = pd.read_csv(INPUTS["review_csv"])
    for df, col in [(c,"center_time"),(l,"center_time"),(m,"center_time"),(t,"datetime_utc"),(marks,"datetime_utc")]: df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    t["source_location"] = t["source_file"].map(location); t["canonical_race_id"] = t["source_location"] + "_" + t["source_race_folder"].astype(str)
    marks["source_location"] = marks["source_file"].map(location); marks["canonical_race_id"] = marks["source_location"] + "_" + marks["source_race_folder"].astype(str)
    cc, ll, mm = c[c.maneuver_id.eq(mid)], l[l.maneuver_id.eq(mid)], m[m.maneuver_id.eq(mid)]
    approved = review[(review.maneuver_id.eq(mid)) & review.recommended_use.eq("primary_demo")]
    if cc.empty or ll.empty or mm.empty or approved.empty: raise ValueError(f"Maneuver {mid} is not a complete approved Stage 2C primary case")
    row = cc.iloc[0].to_dict(); row.update({f"loss_{k}":v for k,v in ll.iloc[0].to_dict().items()}); row.update({f"maneuver_{k}":v for k,v in mm.iloc[0].to_dict().items()})
    return row, b[b.maneuver_id.eq(mid)].sort_values("relative_time_sec"), t, marks


def build_windows(row, baseline, telemetry):
    sub = telemetry[(telemetry.canonical_race_id.eq(row["canonical_race_id"])) & telemetry.team.eq(row["team"]) & telemetry.boat.eq(row["boat"])].copy().set_index("datetime_utc")
    rows = []
    for p in baseline.itertuples(index=False):
        ts = row["center_time"] + pd.Timedelta(seconds=int(p.relative_time_sec)); values = {}
        if ts in sub.index:
            item = sub.loc[ts]; item = item.iloc[0] if isinstance(item, pd.DataFrame) else item; values = item.to_dict()
        rows.append({"relative_time_sec":int(p.relative_time_sec),"target_speed":values.get("BOAT_SPEED_km_h_1",np.nan),"target_vmg":values.get("VMG_km_h_1",np.nan),"fleet_median_speed":p.fleet_median_speed,"fleet_median_vmg":p.fleet_median_vmg,"twa":values.get("TWA_SGP_deg",np.nan),"twd":values.get("TWD_SGP_deg",np.nan),"heading":values.get("HEADING_deg",np.nan),"yaw":values.get("RATE_YAW_deg_s_1",np.nan)})
    win = pd.DataFrame(rows); win["twa_used"] = win.twa.fillna(((win.heading-win.twd+180)%360)-180)
    flat = sub.reset_index(); sec = (flat.datetime_utc-row["center_time"]).dt.total_seconds(); track = flat.assign(relative_time_sec=sec)[sec.between(-30,45)].copy()
    return win, track


def nearby_marks(row, marks, track):
    rm = marks[marks.canonical_race_id.eq(row["canonical_race_id"])].copy(); rm["td"] = (rm.datetime_utc-row["center_time"]).dt.total_seconds().abs(); snap = rm.sort_values("td").groupby("MARK",as_index=False).first()
    center = track.iloc[track.relative_time_sec.abs().argmin()]; lat,lon = center.LATITUDE_GPS_unk,center.LONGITUDE_GPS_unk
    snap["distance_m"] = np.hypot((snap.LATITUDE_deg-lat)*111000,(snap.LONGITUDE_deg-lon)*111000*np.cos(np.deg2rad(lat)))
    return snap.nsmallest(7,"distance_m")


def make_receipt(row):
    speed_raw=float(row["relative_speed_loss_area"]); abs_raw=float(row["abs_relative_vmg_loss_area"]); opp=float(row["opposite_vmg_sign_rate"]); unrecovered=pd.isna(row["recovery_time_to_90"])
    speed=45*min(speed_raw/750,1); avmg=30*min(abs_raw/750,1); recovery=15 if unrecovered else 15*min(float(row["recovery_time_to_90"])/30,1)
    uf=.5*float(unrecovered)+.5*opp+.25*float(row["baseline_confidence"]=="medium")+.25*float(row["loss_confidence"]=="medium")+.25*float(bool(row["data_gap_near_center"])); uncertainty=10*min(uf,1)
    return {"label":"Estimated fleet-relative review signal","formula":"45*min(speed_area/750,1) + 30*min(abs_vmg_area/750,1) + recovery_signal - uncertainty_deduction","components":{"speed_separation_component":{"raw":speed_raw,"points":speed},"abs_vmg_separation_component":{"raw":abs_raw,"points":avmg},"recovery_delay_component":{"status":"unrecovered within +30s review window" if unrecovered else "recovered within review window","points":recovery},"review_uncertainty_component":{"opposite_vmg_sign_rate":opp,"unrecovered":unrecovered,"baseline_confidence":row["baseline_confidence"],"loss_confidence":row["loss_confidence"],"data_gap_near_center":bool(row["data_gap_near_center"]),"deduction_points":uncertainty}},"net_review_signal_points":speed+avmg+recovery-uncertainty,"interpretation":"Normalized triage aid for manual review; not a measured elapsed-time attribution."}


def plot_map(path, track, marks):
    fig,ax=plt.subplots(figsize=(9,8)); ax.plot(track.LONGITUDE_GPS_unk,track.LATITUDE_GPS_unk,color="#0072B2",lw=2,label="ITA track (-30s to +45s)"); first,last=track.iloc[0],track.iloc[-1]; center=track.iloc[track.relative_time_sec.abs().argmin()]
    ax.scatter(first.LONGITUDE_GPS_unk,first.LATITUDE_GPS_unk,marker="s",s=70,color="#009E73",label="Review start"); ax.scatter(last.LONGITUDE_GPS_unk,last.LATITUDE_GPS_unk,marker="X",s=80,color="#D55E00",label="Review end"); ax.scatter(center.LONGITUDE_GPS_unk,center.LATITUDE_GPS_unk,marker="*",s=190,color="black",label="Maneuver center")
    for mark in marks.itertuples(index=False):
        col="#D55E00" if str(mark.MARK)=="LG2" else "#CC79A7"; size=110 if str(mark.MARK)=="LG2" else 60; ax.scatter(mark.LONGITUDE_deg,mark.LATITUDE_deg,marker="^",s=size,color=col); ax.annotate(str(mark.MARK),(mark.LONGITUDE_deg,mark.LATITUDE_deg),xytext=(4,4),textcoords="offset points",fontsize=9)
    ax.set(title="Bermuda_Race_2 | ITA | candidate gybe | maneuver 413",xlabel="Longitude",ylabel="Latitude"); ax.legend(fontsize=8); ax.grid(alpha=.2); ax.set_aspect("equal",adjustable="datalim"); fig.tight_layout(); fig.savefig(path,dpi=180); plt.close(fig)


def plot_fingerprint(path,row,win):
    fig,axes=plt.subplots(3,1,figsize=(12,10),sharex=True); sb=win.target_speed<win.fleet_median_speed; ta,fa=win.target_vmg.abs(),win.fleet_median_vmg.abs(); vb=ta<fa
    axes[0].plot(win.relative_time_sec,win.target_speed,label="Target speed",color="#0072B2",lw=2); axes[0].plot(win.relative_time_sec,win.fleet_median_speed,label="Fleet median speed",color="#D55E00",lw=2); axes[0].fill_between(win.relative_time_sec,win.target_speed,win.fleet_median_speed,where=sb,color="#D55E00",alpha=.22,label="Persistent speed separation")
    axes[1].plot(win.relative_time_sec,ta,label="Target |VMG|",color="#009E73",lw=2); axes[1].plot(win.relative_time_sec,fa,label="Fleet median |VMG|",color="#CC79A7",lw=2); axes[1].fill_between(win.relative_time_sec,ta,fa,where=vb,color="#CC79A7",alpha=.22,label="Absolute-VMG separation")
    axes[2].plot(win.relative_time_sec,win.target_vmg,label="Target signed VMG context",color="#009E73",alpha=.45); axes[2].plot(win.relative_time_sec,win.fleet_median_vmg,label="Fleet signed VMG context",color="#CC79A7",alpha=.45)
    for ax in axes: ax.axvline(0,color="black",ls="--"); ax.grid(alpha=.2); ax.legend(fontsize=8); ax.set_ylabel("km/h")
    axes[-1].set_xlabel("Relative time (seconds)"); fig.suptitle(f"Maneuver 413 | demo triage score {row['demo_candidate_score']:.3f} | high confidence | risk: unrecovered within review window"); fig.tight_layout(); fig.savefig(path,dpi=180); plt.close(fig)


def plot_semantics(path,win):
    fig,axes=plt.subplots(4,1,figsize=(12,11),sharex=True); specs=[("twa_used","TWA / estimated TWA","deg","#009E73"),("heading","Heading","deg","#CC79A7"),("yaw","Yaw rate","deg/s","#D55E00"),("target_speed","Target speed","km/h","#0072B2")]
    for ax,(col,label,ylabel,color) in zip(axes,specs): ax.plot(win.relative_time_sec,win[col],label=label,color=color,lw=2); ax.axvline(0,color="black",ls="--"); ax.grid(alpha=.2); ax.legend(fontsize=8); ax.set_ylabel(ylabel)
    axes[0].axhline(0,color="gray",lw=.8); axes[2].axhline(0,color="gray",lw=.8); axes[-1].set_xlabel("Relative time (seconds)"); fig.suptitle("Candidate gybe visual evidence | TWA boundary transition, heading change, yaw peak, and speed response"); fig.tight_layout(); fig.savefig(path,dpi=180); plt.close(fig)


def plot_waterfall(path,rec):
    c=rec["components"]; vals=[c["speed_separation_component"]["points"],c["abs_vmg_separation_component"]["points"],c["recovery_delay_component"]["points"],-c["review_uncertainty_component"]["deduction_points"],rec["net_review_signal_points"]]; starts=[0,vals[0],vals[0]+vals[1],vals[0]+vals[1]+vals[2],0]; labels=["Speed separation","Absolute VMG separation","Recovery delay","Review uncertainty","Net review signal"]
    fig,ax=plt.subplots(figsize=(11,6)); ax.bar(labels,vals,bottom=starts,color=["#0072B2","#009E73","#D55E00","#777777","#CC79A7"]); ax.axhline(0,color="black",lw=.8); ax.set(title="Estimated fleet-relative review signal: normalized triage components",ylabel="Normalized review-signal points"); ax.tick_params(axis="x",rotation=15); ax.grid(axis="y",alpha=.2); ax.set_ylim(0, max(s+v for s,v in zip(starts,vals)) + 15)
    for i,(v,s) in enumerate(zip(vals,starts)): ax.text(i,s+v+(1 if v>=0 else -3),f"{v:+.1f}" if i<4 else f"{v:.1f}",ha="center",fontweight="bold")
    fig.tight_layout(); fig.savefig(path,dpi=180); plt.close(fig)


def plot_panel(path,row,rec,win,track,marks):
    fig=plt.figure(figsize=(16,10)); gs=GridSpec(2,3,figure=fig,width_ratios=[1.05,1.45,1.35]); mapax=fig.add_subplot(gs[:,0]); spax=fig.add_subplot(gs[0,1]); vax=fig.add_subplot(gs[1,1]); textax=fig.add_subplot(gs[:,2])
    mapax.plot(track.LONGITUDE_GPS_unk,track.LATITUDE_GPS_unk,color="#0072B2",lw=2); center=track.iloc[track.relative_time_sec.abs().argmin()]; mapax.scatter(center.LONGITUDE_GPS_unk,center.LATITUDE_GPS_unk,marker="*",s=150,color="black")
    for mark in marks.itertuples(index=False):
        if str(mark.MARK)=="LG2": mapax.scatter(mark.LONGITUDE_deg,mark.LATITUDE_deg,marker="^",s=100,color="#D55E00"); mapax.annotate("LG2",(mark.LONGITUDE_deg,mark.LATITUDE_deg),xytext=(3,3),textcoords="offset points")
    mapax.set_title("Turn near LG2"); mapax.set_xlabel("Longitude"); mapax.set_ylabel("Latitude"); mapax.grid(alpha=.2); mapax.ticklabel_format(useOffset=False); mapax.tick_params(axis="x",rotation=30,labelsize=8)
    sb=win.target_speed<win.fleet_median_speed; spax.plot(win.relative_time_sec,win.target_speed,label="ITA speed",color="#0072B2",lw=2); spax.plot(win.relative_time_sec,win.fleet_median_speed,label="Fleet median",color="#D55E00",lw=2); spax.fill_between(win.relative_time_sec,win.target_speed,win.fleet_median_speed,where=sb,color="#D55E00",alpha=.2); spax.set_title("Persistent speed separation"); spax.legend(fontsize=8); spax.grid(alpha=.2)
    ta,fa=win.target_vmg.abs(),win.fleet_median_vmg.abs(); vax.plot(win.relative_time_sec,ta,label="ITA |VMG|",color="#009E73",lw=2); vax.plot(win.relative_time_sec,fa,label="Fleet median |VMG|",color="#CC79A7",lw=2); vax.fill_between(win.relative_time_sec,ta,fa,where=ta<fa,color="#CC79A7",alpha=.2); vax.set_title("Absolute-VMG recovery separation"); vax.set_xlabel("Seconds from center"); vax.legend(fontsize=8); vax.grid(alpha=.2)
    for ax in [spax,vax]: ax.axvline(0,color="black",ls="--")
    textax.axis("off"); textax.text(0,1,"COACH REVIEW FOCUS",fontsize=15,fontweight="bold",va="top"); txt=f"Bermuda_Race_2 | ITA | candidate gybe\nManeuver 413 near LG2\n\nDemo triage score: {row['demo_candidate_score']:.3f}\nReview signal: {rec['net_review_signal_points']:.1f} points\nBaseline support: median {row['baseline_sample_count_median']:.0f}\nConfidence: high baseline / high loss\n\nTelemetry suggests persistent speed and\nabsolute-VMG separation after the gybe window.\n\nReview focus:\n• First 10–30 seconds after the gybe\n• Speed build versus fleet median\n• Absolute-VMG recovery\n• Wing, rudder, and foil/rake stabilization\n\nRisk: unrecovered within review window.\nRequires manual review."
    textax.text(0,.94,txt,fontsize=10,va="top",linespacing=1.45,wrap=True); fig.suptitle("FoilBrief demo case: estimated fleet-relative review signal",fontsize=18,fontweight="bold"); fig.tight_layout(rect=[0,0,1,.96]); fig.savefig(path,dpi=180); plt.close(fig)


def write_docs(out,row,rec,marks):
    context="near mark LG2" if marks.MARK.astype(str).eq("LG2").any() else "map context available"
    story="FoilBrief flags ITA's gybe near LG2 in Bermuda Race 2 because the boat shows persistent fleet-relative speed and absolute-VMG separation after the maneuver, making the recovery phase worth coach review."
    summary={"maneuver_id":413,"canonical_race_id":row["canonical_race_id"],"team":row["team"],"maneuver_type":"candidate gybe","context":context,"selected_because":"high-confidence candidate with readable turn context, clear TWA/yaw transition, and persistent fleet-relative speed and absolute-VMG separation","demo_candidate_score":float(row["demo_candidate_score"]),"known_risks":["unrecovered within +30s review window","signed VMG polarity requires caution"],"recommended_use":"Primary single-case demonstration after human approval","one_sentence_demo_story":story,"why_low_confidence_stage2_leaders_rejected":"Primary selection requires supported labels, baselines, and readable evidence."}
    evidence={k:jvalue(row[k]) for k in ["speed_drop_window","vmg_drop_window","relative_speed_loss_area","abs_relative_vmg_loss_area","time_below_fleet_speed","time_below_fleet_vmg","recovery_time_to_90","recovery_time_to_95","baseline_sample_count_median","baseline_confidence","loss_confidence","demo_candidate_score","opposite_vmg_sign_rate"]}
    card={"header":{"race":"Bermuda_Race_2","team":"ITA","maneuver":"candidate gybe","maneuver_id":413,"context":context},"estimated_review_signal":{"demo_triage_score":float(row["demo_candidate_score"]),"normalized_review_signal_points":rec["net_review_signal_points"],"speed_separation":float(row["relative_speed_loss_area"]),"absolute_vmg_separation":float(row["abs_relative_vmg_loss_area"]),"recovery_status":"unrecovered within +30s review window","confidence":"high baseline / high loss","risk_flags":["unrecovered within review window","signed VMG polarity caveat"]},"telemetry_suggests":["The boat showed persistent speed and absolute-VMG separation from the fleet median after the candidate gybe window.","The maneuver did not recover within the review window.","The post-gybe recovery phase is worth analyst review."],"evidence":evidence,"coach_review_focus":["Review the first 10 to 30 seconds after the candidate gybe.","Compare speed build and absolute VMG recovery against the fleet median.","Check whether wing trim, rudder angle, or foil/rake signals show delayed stabilization if available; treat these as review signals only."],"available_control_fields":CONTROL_FIELDS,"caveats":["Estimated fleet-relative review signal, not a measured elapsed-time attribution.","Signed VMG has polarity caveats; absolute VMG magnitude is used for safer demo evidence.","Requires human analyst review before any coaching decision."]}
    write_json(out/"demo_case_summary.json",summary); write_json(out/"time_loss_receipt.json",rec); write_json(out/"coach_loss_card.json",card)
    (out/"demo_case_summary.md").write_text("\n".join(["# Demo Case Summary: Maneuver 413","","## Selection","",f"Maneuver 413 is the human-selected primary demo case because it is a high-confidence candidate gybe with a readable turn {context}, a clear TWA/yaw transition, and persistent fleet-relative speed and absolute-VMG separation. Low-confidence Stage 2 leaders were excluded because primary demo selection requires supported labels, baselines, and readable evidence.","","## Known Risks","","- The maneuver is unrecovered within the +30 second review window.","- Signed VMG has polarity caveats, so absolute VMG magnitude is primary evidence.","- The evidence supports analyst triage and requires manual review.","","## Recommended Video Use","","Show the map context, then the candidate-gybe semantics, then the persistent recovery separation.","","## One-Sentence Demo Story","",story,""]),encoding="utf-8")
    c=rec["components"]
    (out/"time_loss_receipt.md").write_text("\n".join(["# Time Loss Receipt: Maneuver 413","","## What Was Measured","","Aligned ITA telemetry was compared with the same-race fleet median from -10 to +30 seconds around the candidate gybe. Speed and absolute VMG magnitude are the primary evidence.","","## Estimated Triage Components","","| Component | Raw evidence | Normalized points |","|---|---:|---:|",f"| Speed separation | {c['speed_separation_component']['raw']:.3f} | {c['speed_separation_component']['points']:.2f} |",f"| Absolute VMG separation | {c['abs_vmg_separation_component']['raw']:.3f} | {c['abs_vmg_separation_component']['points']:.2f} |",f"| Recovery delay | unrecovered within +30s | {c['recovery_delay_component']['points']:.2f} |",f"| Review uncertainty deduction | VMG polarity and unrecovered-window caution | -{c['review_uncertainty_component']['deduction_points']:.2f} |",f"| **Net estimated review signal** |  | **{rec['net_review_signal_points']:.2f}** |","",f"Formula: `{rec['formula']}`.","","## Interpretation","","This receipt is a normalized triage signal for review, not a measured elapsed-time attribution and not evidence of causation. The unrecovered window and VMG polarity require manual review.","","## Claims To Avoid","","Do not present the normalized components as measured seconds, do not attribute the separation to one telemetry variable, and do not present the review signal as a coaching decision.",""]),encoding="utf-8")
    (out/"coach_loss_card.md").write_text("\n".join(["# Coach Loss Card","","## Header","","- Race: Bermuda_Race_2","- Team: ITA","- Maneuver: candidate gybe","- Maneuver ID: 413",f"- Context: {context}","","## Estimated Review Signal","",f"- Demo triage score: {row['demo_candidate_score']:.3f}",f"- Normalized review signal: {rec['net_review_signal_points']:.2f}",f"- Speed separation: {row['relative_speed_loss_area']:.3f}",f"- Absolute VMG separation: {row['abs_relative_vmg_loss_area']:.3f}","- Recovery status: unrecovered within +30s review window","- Confidence: high baseline / high loss","- Risk flags: unrecovered window; signed VMG polarity caveat","","## What Telemetry Suggests","","The boat showed persistent speed and absolute-VMG separation from the fleet median after the candidate gybe window. The maneuver did not recover within the review window. This makes the post-gybe recovery phase worth analyst review.","","## Evidence","","| Metric | Value |","|---|---:|",f"| speed_drop_window | {row['speed_drop_window']:.3f} |",f"| vmg_drop_window | {row['vmg_drop_window']:.3f} |",f"| relative_speed_loss_area | {row['relative_speed_loss_area']:.3f} |",f"| abs_relative_vmg_loss_area | {row['abs_relative_vmg_loss_area']:.3f} |",f"| time_below_fleet_speed | {row['time_below_fleet_speed']:.0f} |",f"| time_below_fleet_vmg | {row['time_below_fleet_vmg']:.0f} |","| recovery_time_to_90 | unrecovered within window |","| recovery_time_to_95 | unrecovered within window |",f"| baseline_sample_count_median | {row['baseline_sample_count_median']:.0f} |",f"| baseline_confidence | {row['baseline_confidence']} |",f"| loss_confidence | {row['loss_confidence']} |","","## Coach Review Focus","","- Review the first 10 to 30 seconds after the candidate gybe.","- Compare speed build and absolute VMG recovery against the fleet median.","- Check whether wing trim, rudder angle, or foil/rake signals show delayed stabilization if available. Treat these as review signals only.","","## Caveats","","- Estimated fleet-relative review signal, not a measured elapsed-time attribution.","- Signed VMG has polarity caveats; absolute VMG magnitude is used for safer demo evidence.","- Requires human analyst review before any coaching decision.",""]),encoding="utf-8")


def validate(out,row,before,after):
    figs=[out/f for f in ["01_race_map_context.png","02_maneuver_fingerprint.png","03_telemetry_semantics.png","04_time_loss_receipt_waterfall.png","05_demo_panel.png"]]; js=[out/f for f in ["demo_case_summary.json","time_loss_receipt.json","coach_loss_card.json"]]; mds=[out/f for f in ["demo_case_summary.md","time_loss_receipt.md","coach_loss_card.md"]]
    parseable=True
    try:
        for p in js: json.loads(p.read_text())
    except Exception: parseable=False
    text="\n".join(p.read_text().lower() for p in mds); unsafe=[x for x in FORBIDDEN if x in text]
    return [("1. Maneuver 413 exists",int(row["maneuver_id"])==413,"413"),("2. Maneuver 413 is in Stage 2B candidates",True,"human-selected primary input"),("3. Classification confidence is high or medium",float(row["classification_confidence"])>=.7,str(row["classification_confidence"])),("4. Baseline confidence is high or medium",row["baseline_confidence"] in ["high","medium"],str(row["baseline_confidence"])),("5. Loss confidence is high or medium",row["loss_confidence"] in ["high","medium"],str(row["loss_confidence"])),("6. canonical_race_id is Bermuda_Race_2",row["canonical_race_id"]=="Bermuda_Race_2",str(row["canonical_race_id"])),("7. Team is ITA",row["team"]=="ITA",str(row["team"])),("8. Maneuver type is candidate gybe equivalent",row["maneuver_type"]=="gybe",str(row["maneuver_type"])),("9. No data gap near center",not bool(row["data_gap_near_center"]),str(row["data_gap_near_center"])),("10. Map figure exists and is non-empty",figs[0].exists() and figs[0].stat().st_size>0,str(figs[0].name)),("11. Fingerprint figure exists and is non-empty",figs[1].exists() and figs[1].stat().st_size>0,str(figs[1].name)),("12. Telemetry semantics figure exists and is non-empty",figs[2].exists() and figs[2].stat().st_size>0,str(figs[2].name)),("13. Waterfall figure exists and is non-empty",figs[3].exists() and figs[3].stat().st_size>0,str(figs[3].name)),("14. Demo panel exists and is non-empty",figs[4].exists() and figs[4].stat().st_size>0,str(figs[4].name)),("15. JSON outputs exist and are parseable",all(p.exists() for p in js) and parseable,"3/3"),("16. Markdown outputs exist and are non-empty",all(p.exists() and p.stat().st_size>0 for p in mds),"3/3"),("17. No model artifacts created",before==after,f"new={sorted(after-before)}"),("18. Prohibited-language scan clear",not unsafe,f"hits={unsafe}"),("19. Coach card avoids measured-time attribution","measured elapsed-time attribution" in (out/"coach_loss_card.md").read_text().lower(),"explicit caveat present"),("20. Stage 3 stops after demo case assets",True,"no final submission assets created")]


def main():
    global DATA, REVIEW, INPUTS
    ap=argparse.ArgumentParser(description="Build the curated FoilBrief Demo 413 evidence package.")
    ap.add_argument("--maneuver-id",type=int,default=413)
    ap.add_argument("--processed-dir",type=Path,default=DATA,help="Directory containing externalized processed parquet inputs.")
    ap.add_argument("--review-dir",type=Path,default=REVIEW,help="Directory containing the externalized manual review pack.")
    ap.add_argument("--output-dir",type=Path,default=ROOT/"outputs"/"demo_case_413")
    ap.add_argument("--publish-web-assets",action="store_true",help="Copy curated runtime files into the web app public data directory.")
    args=ap.parse_args()
    if args.maneuver_id != 413: raise ValueError("This final public pipeline script is scoped to the curated Demo 413 case.")
    DATA=args.processed_dir.resolve(); REVIEW=args.review_dir.resolve(); out=args.output_dir.resolve()
    INPUTS={"candidates":DATA/"stage2b_demo_candidates.parquet","losses":DATA/"maneuver_loss_metrics.parquet","baselines":DATA/"maneuver_fleet_baselines.parquet","maneuvers":DATA/"maneuvers_v1_refined_fixed.parquet","telemetry":DATA/"telemetry_1hz.parquet","marks":DATA/"marks_1hz.parquet","review_pack":REVIEW/"stage2c_manual_review_pack.md","review_csv":REVIEW/"stage2c_manual_review_candidates.csv"}
    out.mkdir(parents=True,exist_ok=True)
    before=snapshot_models(); row,base,t,marks=prepare(args.maneuver_id); win,track=build_windows(row,base,t); nearby=nearby_marks(row,marks,track); rec=make_receipt(row)
    plot_map(out/"01_race_map_context.png",track,nearby); plot_fingerprint(out/"02_maneuver_fingerprint.png",row,win); plot_semantics(out/"03_telemetry_semantics.png",win); plot_waterfall(out/"04_time_loss_receipt_waterfall.png",rec); plot_panel(out/"05_demo_panel.png",row,rec,win,track,nearby); write_docs(out,row,rec,nearby)
    after=snapshot_models(); checks=validate(out,row,before,after); lines=["# Stage 3 Validation Summary","",f"- Overall validation: **{'PASS' if all(ok for _,ok,_ in checks) else 'FAIL'}**",f"- Checks passed: {sum(ok for _,ok,_ in checks)}/{len(checks)}","","| check | status | detail |","|---|---|---|"]+[f"| {n} | {'PASS' if ok else 'FAIL'} | {d} |" for n,ok,d in checks]+["","Stage 3 stopped after human-selected demo-case assets. Final submission documents and slides were not created.",""]
    (out/"stage3_validation_summary.md").write_text("\n".join(lines),encoding="utf-8")
    if args.publish_web_assets:
        WEB_OUT.mkdir(parents=True,exist_ok=True)
        for name in ["05_demo_panel.png","coach_loss_card.json","coach_loss_card.md","demo_case_summary.json","time_loss_receipt.json"]:
            shutil.copy2(out/name,WEB_OUT/name)
    print(f"output_directory={display_path(out)}"); print(f"review_signal_components={rec['components']}"); print(f"net_review_signal_points={rec['net_review_signal_points']:.2f}"); print(f"validation={'PASS' if all(ok for _,ok,_ in checks) else 'FAIL'} ({sum(ok for _,ok,_ in checks)}/{len(checks)})"); return 0 if all(ok for _,ok,_ in checks) else 1


if __name__=="__main__": raise SystemExit(main())
