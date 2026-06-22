# =============================================================================
# ml_models.py — ML Training & Inference (Energy + Temperature Prediction)
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   CONSTANTS:
#       MODEL_DIR        → "models/"
#       ENERGY_MODEL_PATH → models/energy_model.pkl
#       TEMP_MODEL_PATH   → models/temp_model.pkl
#
#   FUNCTION train_models(csv_path):
#       LOAD DataFrame from csv_path
#
#       DEFINE feature columns:
#           ["outdoor_temp", "outdoor_humidity", "occupancy", "hvac_on",
#            "lights_on", "room_temp", "room_humidity", "floor"]
#
#       X       ← df[feature_columns]
#       y_energy ← df["energy_kwh"]                        # current energy
#       y_temp   ← df["room_temp"].shift(-1).fillna(mean)  # NEXT hour temp
#
#       TRAIN energy_model = RandomForestRegressor(n_estimators=150) on (X, y_energy)
#       TRAIN temp_model   = RandomForestRegressor(n_estimators=150) on (X, y_temp)
#
#       SAVE both models via joblib.dump()
#
#       COMPUTE & RETURN metrics dict:
#           {energy_mae, energy_r2, temp_mae, temp_r2}
#
#   FUNCTION load_models():
#       LOAD energy_model from disk
#       LOAD temp_model   from disk
#       RETURN (energy_model, temp_model)
#
#   FUNCTION predict_next(row_dict):
#       LOAD models
#       BUILD single-row DataFrame from row_dict using feature columns
#       next_energy ← energy_model.predict(X)[0]
#       next_temp   ← temp_model.predict(X)[0]
#       RETURN (round(next_energy, 2), round(next_temp, 2))
#
# =============================================================================

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# --- PSEUDO: paths for serialised models ---
MODEL_DIR         = "models"
ENERGY_MODEL_PATH = os.path.join(MODEL_DIR, "energy_model.pkl")
TEMP_MODEL_PATH   = os.path.join(MODEL_DIR, "temp_model.pkl")

# Features shared by both models
FEATURE_COLS = [
    "outdoor_temp", "outdoor_humidity", "occupancy",
    "hvac_on", "lights_on", "room_temp", "room_humidity", "floor",
]


def train_models(csv_path: str = "data/realtime.csv") -> dict:
    """
    Train energy and temperature prediction models on the simulation dataset.

    The temperature model predicts the *next* hour's temperature (shift −1),
    making it a one-step-ahead forecaster.

    Args:
        csv_path (str): Path to the simulation CSV produced by simulator.py.

    Returns:
        dict: MAE and R² for both models on the training set.
    """
    # --- PSEUDO: ensure model directory exists ---
    os.makedirs(MODEL_DIR, exist_ok=True)

    # --- PSEUDO: load simulation data ---
    df = pd.read_csv(csv_path)

    X        = df[FEATURE_COLS]
    y_energy = df["energy_kwh"]

    # --- PSEUDO: shift temperature by 1 to create next-hour target ---
    y_temp = df["room_temp"].shift(-1).fillna(df["room_temp"].mean())

    # --- PSEUDO: train Random Forest regressors ---
    energy_model = RandomForestRegressor(n_estimators=150, random_state=42)
    temp_model   = RandomForestRegressor(n_estimators=150, random_state=42)

    energy_model.fit(X, y_energy)
    temp_model.fit(X, y_temp)

    # --- PSEUDO: persist trained models ---
    joblib.dump(energy_model, ENERGY_MODEL_PATH)
    joblib.dump(temp_model, TEMP_MODEL_PATH)

    # --- PSEUDO: compute in-sample metrics for diagnostics ---
    metrics = {
        "energy_mae": float(mean_absolute_error(y_energy, energy_model.predict(X))),
        "energy_r2":  float(r2_score(y_energy, energy_model.predict(X))),
        "temp_mae":   float(mean_absolute_error(y_temp, temp_model.predict(X))),
        "temp_r2":    float(r2_score(y_temp, temp_model.predict(X))),
    }
    return metrics


def load_models():
    """
    Load serialised models from disk.

    Returns:
        tuple: (energy_model, temp_model)

    Raises:
        FileNotFoundError: If models have not been trained yet.
    """
    # --- PSEUDO: deserialise models from .pkl files ---
    energy_model = joblib.load(ENERGY_MODEL_PATH)
    temp_model   = joblib.load(TEMP_MODEL_PATH)
    return energy_model, temp_model


def predict_next(row_dict: dict) -> tuple:
    """
    Predict next-hour energy consumption and room temperature for a single row.

    Args:
        row_dict (dict): Sensor reading dict containing the feature columns.

    Returns:
        tuple: (predicted_energy_kwh, predicted_temp_celsius)
    """
    # --- PSEUDO: load models and build one-row feature matrix ---
    energy_model, temp_model = load_models()
    X = pd.DataFrame([row_dict])[FEATURE_COLS]

    # --- PSEUDO: generate predictions ---
    next_energy = float(energy_model.predict(X)[0])
    next_temp   = float(temp_model.predict(X)[0])

    return round(next_energy, 2), round(next_temp, 2)
