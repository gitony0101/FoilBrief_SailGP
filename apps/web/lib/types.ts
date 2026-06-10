export type ManeuverRow = {
  maneuver_id: string;
  canonical_race_id: string;
  source_location: string;
  team: string;
  boat: string;
  maneuver_type: string;
  center_time: string;
  classification_confidence: string;
  baseline_confidence: string;
  loss_confidence: string;
  demo_triage_score: string;
  relative_speed_loss_area: string;
  abs_relative_vmg_loss_area: string;
  time_below_fleet_speed: string;
  time_below_fleet_vmg: string;
  recovery_time_to_90: string;
  recovery_time_to_95: string;
  data_gap_near_center: string;
  vmg_sign_mismatch_flag: string;
  unrecovered_flag: string;
  strict_demo_candidate: string;
  review_tier: string;
  recommended_use: string;
  final_card_available: string;
  final_card_path: string;
};

export type ManeuverIndexSummary = {
  total_maneuvers: number;
  unique_teams: number;
  total_races: number;
  counts_by_maneuver_type: Record<string, number>;
  counts_by_review_tier: Record<string, number>;
  primary_demo_maneuver_id: number;
};

export type DemoCaseSummary = {
  maneuver_id: number;
  canonical_race_id: string;
  team: string;
  maneuver_type: string;
  context: string;
  selected_because: string;
  demo_candidate_score: number;
  known_risks: string[];
  recommended_use: string;
  one_sentence_demo_story: string;
};

export type CoachLossCard = {
  header: Record<string, string | number>;
  estimated_review_signal: {
    demo_triage_score: number;
    normalized_review_signal_points: number;
    speed_separation: number;
    absolute_vmg_separation: number;
    recovery_status: string;
    confidence: string;
    risk_flags: string[];
  };
  telemetry_suggests: string[];
  evidence: Record<string, string | number | boolean | null>;
  coach_review_focus: string[];
  caveats: string[];
};

export type TimeLossReceipt = {
  label: string;
  formula: string;
  components: Record<string, Record<string, string | number | boolean>>;
  net_review_signal_points: number;
  interpretation: string;
};

export type EnvironmentContext = {
  maneuver_id: string;
  race_id: string | null;
  canonical_race_id: string | null;
  team: string | null;
  boat: string | null;
  maneuver_type: string | null;
  center_time: string | null;
  event_location: string | null;
  environment_confidence_label: string;
  environment_source_confidence: number | null;
  open_meteo_available: boolean;
  open_meteo_wind_speed_10m: number | null;
  open_meteo_wind_direction_10m: number | null;
  open_meteo_wind_gusts_10m: number | null;
  open_meteo_temperature_2m: number | null;
  open_meteo_precipitation: number | null;
  weather_time_delta_minutes: number | null;
  ndbc_available: boolean;
  ndbc_station: string | null;
  ndbc_wave_height: number | null;
  ndbc_wind_speed: number | null;
  ndbc_wind_direction: number | null;
  wave_context_flag: string;
  environment_brief_sentence: string;
  environment_context_note: string;
};
