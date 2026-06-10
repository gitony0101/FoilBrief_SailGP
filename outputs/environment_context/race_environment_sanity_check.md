# SailGP Telemetry vs Open-Meteo Wind Sanity Check

Compares SailGP race-average `avg_tws_km_h` (converted to m/s) with
Open-Meteo archive API `wind_speed_10m` mean for the same race window.

| Race | SailGP (m/s) | Open-Meteo (m/s) | Delta (m/s) | Ratio | TWD (°) | Flag |
|------|-------------|-------------------|-------------|-------|---------|------|
| Bermuda_Race_1 | 8.4 | 6.5 | -2.0 | 0.77 | 91 | ok |
| Bermuda_Race_2 | 8.9 | 6.5 | -2.4 | 0.73 | 92 | ok |
| Bermuda_Race_3 | 9.2 | 6.5 | -2.8 | 0.70 | 95 | ok |
| Bermuda_Race_4 | 8.3 | 6.5 | -1.8 | 0.78 | 94 | ok |
| Bermuda_Race_5 | 5.8 | 6.4 | +0.6 | 1.10 | 209 | ok |
| Bermuda_Race_6 | 5.8 | 6.4 | +0.6 | 1.10 | 207 | ok |
| Bermuda_Race_7 | 5.6 | 6.4 | +0.8 | 1.15 | 211 | ok |
| Bermuda_Race_8 | 6.0 | 6.4 | +0.4 | 1.06 | 211 | ok |
| Halifax_Race_1 | 7.2 | 4.2 | -3.0 | 0.58 | 147 | ok |
| Halifax_Race_2 | 8.0 | 4.2 | -3.8 | 0.52 | 152 | ok |
| Halifax_Race_3 | 8.4 | 4.2 | -4.2 | 0.50 | 132 | ok |
| Halifax_Race_4 | 9.7 | 6.3 | -3.3 | 0.66 | 340 | ok |
| Halifax_Race_5 | 7.8 | 6.3 | -1.4 | 0.81 | 228 | ok |
| Halifax_Race_6 | 8.9 | 6.3 | -2.6 | 0.71 | 343 | ok |

## Interpretation

- SailGP wind is measured on-course at ~5m height; Open-Meteo is regional ERA5 reanalysis at 10m.
- A ratio of 0.5–2.0 is expected; near 1.0 is ideal.
- Large deltas (>5 m/s) may indicate coarse reanalysis resolution or localized race conditions.
- This is a context check, not a validation — neither source is "ground truth".