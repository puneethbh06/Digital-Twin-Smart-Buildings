# 🏢 Intelligent Digital Twin for Smart Buildings

A fully software-based, multi-building Digital Twin simulation that models
thermal dynamics, energy consumption, occupancy, anomaly detection, and
real-time optimisation — all visualised through an interactive Streamlit dashboard.

---

## Architecture Overview

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  config.py  │───▶│  weather.py  │    │  building.py │
│  (settings) │    │  (sinusoidal │    │  (Room class │
│             │    │   climate)   │    │   physics)   │
└─────────────┘    └──────┬───────┘    └──────┬───────┘
                          │                   │
                          ▼                   ▼
                   ┌──────────────────────────────┐
                   │        simulator.py          │
                   │  (time-loop, fault injection)│
                   └──────────────┬───────────────┘
                                  │ data/realtime.csv
                    ┌─────────────┼──────────────┐
                    ▼             ▼               ▼
             ml_models.py    anomaly.py     optimizer.py
             (RF predict)   (IsoForest)   (rule engine)
                    │             │               │
                    └─────────────▼───────────────┘
                              dashboard.py
                          (Streamlit UI + Plotly 3D)
```

## Module Descriptions

| File | Responsibility |
|---|---|
| `config.py` | All constants: buildings, rooms, comfort bands, paths, random seed |
| `weather.py` | Sinusoidal daily temperature & humidity cycle with Gaussian noise |
| `building.py` | `Room` physics (HVAC bang-bang, occupancy, energy model) + `RoomState` dataclass |
| `simulator.py` | Time-loop, fault injection, record flattening |
| `ml_models.py` | Train/infer RandomForest energy & next-temp predictors |
| `anomaly.py` | Train/infer IsolationForest anomaly detector |
| `optimizer.py` | Rule-based comfort & energy optimiser |
| `visualization_3d.py` | Plotly 3-D scatter floor plan |
| `main.py` | CLI pipeline: simulate → train → optimise |
| `dashboard.py` | Streamlit real-time dashboard |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/<your-org>/digital-twin-smart-building.git
cd digital-twin-smart-building

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run simulation + train models
python main.py

# 5. Launch dashboard
streamlit run dashboard.py
# Open http://127.0.0.1:8501 in Chrome
```

---

## Features

- **Multi-building / multi-room** simulation (North & South Block, 6 rooms each)
- **Physics-based thermal model** — first-order ODE with outdoor coupling and HVAC control
- **Stochastic fault injection** — random energy spikes and overheating events
- **ML predictions** — RandomForest next-hour energy & temperature forecasts
- **Anomaly detection** — Isolation Forest (unsupervised, 5% contamination)
- **Rule-based optimiser** — prioritised HVAC / lighting recommendations
- **Auto-refresh dashboard** — Streamlit + Plotly 3-D floor layout, live metrics
- **Fully reproducible** — global `RANDOM_SEED = 42` in `config.py`

---

## Data & Model Artefacts

Generated at runtime (excluded from Git via `.gitignore`):

| Path | Description |
|---|---|
| `data/realtime.csv` | 30-day hourly simulation records (≈ 17 k rows) |
| `data/optimizations_latest.csv` | Optimiser output for last 200 rows |
| `models/energy_model.pkl` | Serialised energy RandomForest |
| `models/temp_model.pkl` | Serialised temperature RandomForest |
| `models/anomaly_model.pkl` | Serialised IsolationForest |

---

## Configuration

Edit `config.py` to adjust:

- `SIM_DAYS` — simulation duration
- `COMFORT_LOW` / `COMFORT_HIGH` — HVAC trigger band
- `FAULT_PROBABILITY` — fault injection rate
- `ROOMS_PER_BUILDING` — add or remove rooms / buildings

---

## License

MIT
