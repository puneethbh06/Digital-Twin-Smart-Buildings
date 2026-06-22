# =============================================================================
# anomaly.py — Anomaly Detection via Isolation Forest
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   CONSTANT ANOMALY_MODEL_PATH → "models/anomaly_model.pkl"
#
#   FUNCTION train_anomaly_model(csv_path):
#       LOAD DataFrame from csv_path
#
#       DEFINE anomaly feature columns:
#           ["outdoor_temp", "outdoor_humidity", "room_temp", "room_humidity",
#            "occupancy", "hvac_on", "lights_on", "water_liters", "energy_kwh"]
#
#       X ← df[feature_columns]
#
#       TRAIN model = IsolationForest(
#                         n_estimators=200,
#                         contamination=0.05,   ← expect 5% anomalies
#                         random_state=42
#                     )
#
#       scores ← model.decision_function(X)   # lower = more anomalous
#       preds  ← model.predict(X)             # −1 = anomaly, +1 = normal
#
#       WRITE anomaly_score & anomaly_flag columns back to CSV
#
#       SAVE model to ANOMALY_MODEL_PATH
#
#       RETURN { anomaly_count, anomaly_rate }
#
#   FUNCTION load_anomaly_model():
#       RETURN joblib.load(ANOMALY_MODEL_PATH)
#
#   FUNCTION detect_anomaly(row_dict):
#       LOAD model
#       BUILD one-row DataFrame from row_dict
#       pred  ← model.predict(X)[0]              # −1 or +1
#       score ← model.decision_function(X)[0]    # float
#       RETURN (1 if pred == −1 else 0, round(score, 4))
#
# =============================================================================

import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

ANOMALY_MODEL_PATH = "models/anomaly_model.pkl"

# Features used for anomaly scoring (richer set than the energy model)
ANOMALY_FEATURE_COLS = [
    "outdoor_temp", "outdoor_humidity",
    "room_temp", "room_humidity",
    "occupancy", "hvac_on", "lights_on",
    "water_liters", "energy_kwh",
]


def train_anomaly_model(csv_path: str = "data/realtime.csv") -> dict:
    """
    Train an Isolation Forest model to detect unusual sensor patterns.

    Scores and flags are written back to the CSV so the dashboard can
    display historical anomalies without re-running inference.

    Args:
        csv_path (str): Path to the simulation / realtime CSV.

    Returns:
        dict: { 'anomaly_count': int, 'anomaly_rate': float }
    """
    # --- PSEUDO: load dataset ---
    df = pd.read_csv(csv_path)
    X  = df[ANOMALY_FEATURE_COLS]

    # --- PSEUDO: train unsupervised anomaly detector ---
    #   contamination=0.05 → model assumes ≤5% of points are anomalies
    model = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
    model.fit(X)

    # --- PSEUDO: score every row in the dataset ---
    scores = model.decision_function(X)   # negative = more anomalous
    preds  = model.predict(X)             # −1 = anomaly, +1 = inlier

    # --- PSEUDO: annotate dataset and overwrite CSV ---
    df["anomaly_score"] = scores
    df["anomaly_flag"]  = (preds == -1).astype(int)
    df.to_csv(csv_path, index=False)

    # --- PSEUDO: save trained model for runtime inference ---
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, ANOMALY_MODEL_PATH)

    return {
        "anomaly_count": int(df["anomaly_flag"].sum()),
        "anomaly_rate":  float(df["anomaly_flag"].mean()),
    }


def load_anomaly_model():
    """
    Load the serialised Isolation Forest from disk.

    Returns:
        IsolationForest: Trained anomaly detection model.
    """
    # --- PSEUDO: deserialise model ---
    return joblib.load(ANOMALY_MODEL_PATH)


def detect_anomaly(row_dict: dict) -> tuple:
    """
    Run real-time anomaly detection on a single sensor reading.

    Args:
        row_dict (dict): Must contain all ANOMALY_FEATURE_COLS keys.

    Returns:
        tuple: (anomaly_flag: int 0|1, anomaly_score: float)
               Lower score → higher anomalousness.
    """
    # --- PSEUDO: load model, build single-row matrix ---
    model = load_anomaly_model()
    X     = pd.DataFrame([row_dict])[ANOMALY_FEATURE_COLS]

    # --- PSEUDO: predict and score ---
    pred  = model.predict(X)[0]
    score = float(model.decision_function(X)[0])

    # --- PSEUDO: convert −1/+1 prediction to binary flag ---
    return int(pred == -1), round(score, 4)
