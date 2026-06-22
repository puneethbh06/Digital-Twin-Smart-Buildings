# =============================================================================
# dashboard.py — Streamlit Real-Time Dashboard
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   CONFIGURE page: wide layout, title "Digital Twin Dashboard"
#   SET auto-refresh every 5 seconds
#
#   IF "data/realtime.csv" not found:
#       SHOW info message
#       CALL main() to generate simulation data
#
#   LOAD df from CSV, normalise column names to lowercase
#
#   RENDER page title
#
#   SIDEBAR:
#       selected_building ← selectbox(unique buildings)
#       selected_room     ← selectbox(unique rooms in building)
#
#   FILTER df → building_df (selected building)
#   FILTER building_df → room_df (selected room)
#   latest ← room_df.iloc[-1].to_dict()
#
#   CALL predict_next(latest)   → (next_energy, next_temp)
#   CALL detect_anomaly(latest) → (anomaly_flag, anomaly_score)
#   CALL optimize_row(latest)   → recommendation dict
#
#   ROW 1 — Current Metrics (4 columns):
#       Current Temp | Energy kWh | Water L | Occupancy
#
#   ROW 2 — AI Predictions (4 columns):
#       Predicted Temp | Predicted Energy | Anomaly Score | Anomaly Flag
#
#   SECTION "Room Analysis":
#       Line chart: room_temp + energy_kwh over time
#
#   SPLIT COLUMNS:
#       Left:  line chart water_liters
#       Right: bar chart occupancy
#
#   SECTION "Weather & Control":
#       Line chart: outdoor_temp, outdoor_humidity, hvac_on, lights_on
#
#   SECTION "3D Floor Layout":
#       CALL build_3d_floor_layout(df, selected_building)
#       RENDER with plotly_chart
#
#   SECTION "Optimisation Recommendation":
#       DISPLAY action, hvac_on, lights_on, setpoint, priority, energy_saving
#
#   SECTION "Anomalies in Selected Room":
#       SHOW last 20 rows where anomaly_flag == 1
#
#   SECTION "Latest Records":
#       SHOW last 15 rows of room_df
#
#   SECTION "Building KPI Summary":
#       GROUP building_df by room
#       MEAN of temp, energy, water, occupancy → show as table
#
# =============================================================================

import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ml_models import predict_next
from optimizer import optimize_row
from visualization_3d import build_3d_floor_layout
from anomaly import detect_anomaly
from main import main as generate_data

# --- PSEUDO: configure Streamlit page ---
st.set_page_config(page_title="Digital Twin Dashboard", layout="wide")

# --- PSEUDO: auto-refresh every 5 s to simulate real-time feel ---
st_autorefresh(interval=5000, key="dt_refresh")

# --- PSEUDO: bootstrap data if running for the first time ---
if not os.path.exists("data/realtime.csv"):
    st.info("Data not found. Generating simulation dataset...")
    generate_data()

# --- PSEUDO: load and normalise dataset ---
df = pd.read_csv("data/realtime.csv")
df.columns = df.columns.str.strip().str.lower()

st.title("🏢 Intelligent Digital Twin for Smart Buildings")

# ─── Sidebar filters ──────────────────────────────────────────────────────────

# --- PSEUDO: building selector ---
building_options  = sorted(df["building"].unique())
selected_building = st.sidebar.selectbox("Select Building", building_options)

building_df = df[df["building"] == selected_building].copy()

# --- PSEUDO: room selector (filtered by building) ---
room_options  = sorted(building_df["room"].unique())
selected_room = st.sidebar.selectbox("Select Room", room_options)

room_df = building_df[building_df["room"] == selected_room].copy()
latest  = room_df.iloc[-1].to_dict()

# ─── AI inference on the latest row ──────────────────────────────────────────

# --- PSEUDO: ML predictions + anomaly detection + optimiser ---
next_energy, next_temp     = predict_next(latest)
anomaly_flag, anomaly_score = detect_anomaly(latest)
recommendation              = optimize_row(latest)

# ─── KPI metric cards ─────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Temp (°C)",  f"{latest['room_temp']:.2f}")
c2.metric("Energy (kWh)",       f"{latest['energy_kwh']:.2f}")
c3.metric("Water (L)",          f"{latest['water_liters']:.2f}")
c4.metric("Occupancy",          int(latest["occupancy"]))

c5, c6, c7, c8 = st.columns(4)
c5.metric("Predicted Next Temp",   f"{next_temp:.2f}")
c6.metric("Predicted Next Energy", f"{next_energy:.2f}")
c7.metric("Anomaly Score",         f"{anomaly_score:.4f}")
c8.metric("Anomaly Flag",          "Yes" if anomaly_flag else "No")

# ─── Time-series charts ───────────────────────────────────────────────────────

st.subheader(f"Room Analysis: {selected_room}")
# --- PSEUDO: temp + energy combined trend ---
st.line_chart(room_df[["room_temp", "energy_kwh"]].reset_index(drop=True))

cc1, cc2 = st.columns(2)
with cc1:
    st.line_chart(room_df[["water_liters"]].reset_index(drop=True))
    st.caption("Water Usage")
with cc2:
    st.bar_chart(room_df[["occupancy"]].reset_index(drop=True))
    st.caption("Occupancy")

st.subheader("Weather and Control Variables")
st.line_chart(
    room_df[["outdoor_temp", "outdoor_humidity", "hvac_on", "lights_on"]]
    .reset_index(drop=True)
)

# ─── 3-D floor visualisation ─────────────────────────────────────────────────

st.subheader("3D Floor Layout Visualization")
# --- PSEUDO: build Plotly 3-D figure and embed in dashboard ---
fig = build_3d_floor_layout(df, selected_building)
st.plotly_chart(fig, use_container_width=True)

# ─── Optimiser recommendation ────────────────────────────────────────────────

st.subheader("Optimization Recommendation")
st.write(f"**Action:** {recommendation['action']}")
st.write(f"**HVAC On:** {recommendation['hvac_on']},  **Lights On:** {recommendation['lights_on']}")
st.write(f"**Suggested Setpoint:** {recommendation['setpoint']} °C")
st.write(f"**Priority:** {recommendation['priority']}")
st.write(f"**Estimated Energy Saving:** {recommendation['estimated_energy_saving_kwh']} kWh")

# ─── Anomaly table ───────────────────────────────────────────────────────────

st.subheader("Anomalies in Selected Room")
if "anomaly_flag" in room_df.columns:
    anomalies = room_df[room_df["anomaly_flag"] == 1]
    st.dataframe(anomalies.tail(20), use_container_width=True)
else:
    st.info("Anomaly column not available in this dataframe snapshot.")

# ─── Raw data preview ────────────────────────────────────────────────────────

st.subheader("Latest Records")
st.dataframe(room_df.tail(15), use_container_width=True)

# ─── Building KPI summary ────────────────────────────────────────────────────

st.subheader("Building KPI Summary")
# --- PSEUDO: mean KPIs per room for the selected building ---
summary = (
    building_df
    .groupby("room")[["room_temp", "energy_kwh", "water_liters", "occupancy"]]
    .mean()
    .round(2)
)
st.dataframe(summary, use_container_width=True)
