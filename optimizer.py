# =============================================================================
# optimizer.py — Rule-Based Energy & Comfort Optimiser
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   FUNCTION optimize_row(row):
#       READ temp, occupancy, energy, room_type from row
#
#       INITIALISE recommendation:
#           setpoint      ← 24.0 °C
#           hvac_on       ← 1 if temp > 25.2 else 0
#           lights_on     ← 1 if occupancy > 0 else 0
#           priority      ← "Normal"
#           action        ← "Maintain current operation"
#
#       SET comfort band:
#           IF ServerRoom: low=20, high=23
#           ELSE:          low=22, high=25
#
#       APPLY rule hierarchy (highest priority first):
#           IF temp > high + 0.8:
#               → setpoint = high − 1, hvac_on=1, priority="High", action="Increase cooling"
#           ELIF temp < low − 0.8:
#               → setpoint = low + 1, hvac_on=1, priority="High", action="Increase heating"
#           ELIF occupancy == 0:
#               → lights_on=0, priority="Low", action="Turn off lights and reduce HVAC load"
#           ELIF energy > 6.0:
#               → setpoint=24.5, priority="Medium", action="Reduce energy usage"
#
#       COMPUTE estimated_energy_saving_kwh ← energy × 0.85  (15% saving estimate)
#
#       RETURN recommendation dict
#
#   FUNCTION optimize_dataframe(df):
#       FOR each row in df:
#           rec ← optimize_row(row)
#           MERGE original row fields with recommendation
#           APPEND to results
#       RETURN DataFrame of results
#
# =============================================================================

import pandas as pd


def optimize_row(row: dict) -> dict:
    """
    Apply a rule-based optimiser to a single room's current sensor reading
    and produce an actionable control recommendation.

    Priority levels:  High > Medium > Normal > Low

    Args:
        row (dict): Must contain 'room_temp', 'occupancy', 'energy_kwh',
                    and optionally 'room_type'.

    Returns:
        dict: Recommendation with keys:
              setpoint, hvac_on, lights_on, priority, action,
              estimated_energy_saving_kwh
    """
    # --- PSEUDO: extract key metrics from the row ---
    temp      = float(row["room_temp"])
    occ       = int(row["occupancy"])
    energy    = float(row["energy_kwh"])
    room_type = row.get("room_type", "Office")

    # --- PSEUDO: default (do-nothing) recommendation ---
    recommendation = {
        "setpoint":  24.0,
        "hvac_on":   1 if temp > 25.2 else 0,
        "lights_on": 1 if occ > 0 else 0,
        "priority":  "Normal",
        "action":    "Maintain current operation",
    }

    # --- PSEUDO: room-type-specific comfort thresholds ---
    low, high = (20.0, 23.0) if room_type == "ServerRoom" else (22.0, 25.0)

    # --- PSEUDO: rule hierarchy (first match wins) ---
    if temp > high + 0.8:
        # Overheating — ramp up cooling
        recommendation["setpoint"] = max(20.0, high - 1.0)
        recommendation["hvac_on"]  = 1
        recommendation["priority"] = "High"
        recommendation["action"]   = "Increase cooling"

    elif temp < low - 0.8:
        # Too cold — ramp up heating
        recommendation["setpoint"] = min(26.0, low + 1.0)
        recommendation["hvac_on"]  = 1
        recommendation["priority"] = "High"
        recommendation["action"]   = "Increase heating"

    elif occ == 0:
        # Empty room — standby mode
        recommendation["lights_on"] = 0
        recommendation["priority"]  = "Low"
        recommendation["action"]    = "Turn off lights and reduce HVAC load"

    elif energy > 6.0:
        # High energy draw — mild setpoint nudge
        recommendation["setpoint"] = 24.5
        recommendation["priority"] = "Medium"
        recommendation["action"]   = "Reduce energy usage"

    # --- PSEUDO: estimate 15% energy saving from following recommendation ---
    recommendation["estimated_energy_saving_kwh"] = round(
        max(0.0, energy - (energy * 0.15)), 2
    )

    return recommendation


def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply optimize_row to every row in a DataFrame and merge results.

    Args:
        df (pd.DataFrame): Sensor data (must include all required columns).

    Returns:
        pd.DataFrame: Original columns + recommendation columns.
    """
    # --- PSEUDO: iterate rows, merge original data with recommendation ---
    rows = []
    for _, row in df.iterrows():
        rec = optimize_row(row.to_dict())
        out = row.to_dict()
        out.update(rec)       # recommendation fields overwrite same-named cols
        rows.append(out)

    return pd.DataFrame(rows)
