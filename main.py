# =============================================================================
# main.py — Entry Point: Run Simulation, Train Models, Export Results
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   FUNCTION main():
#       ENSURE directories "data/" and "models/" exist
#
#       # 1. Simulate
#       sim     ← DigitalTwinSimulator()
#       records ← sim.run()                       # list of dicts
#       df      ← DataFrame(records)
#       SAVE df → DATA_CSV ("data/realtime.csv")
#
#       # 2. Train ML models
#       metrics      ← train_models(DATA_CSV)     # energy + temp models
#       anomaly_info ← train_anomaly_model(DATA_CSV)  # anomaly model
#
#       # 3. Generate optimisation recommendations on recent data
#       opt_df ← optimize_dataframe(df.tail(200))
#       SAVE opt_df → "data/optimizations_latest.csv"
#
#       PRINT summary to console
#
#   IF __name__ == "__main__":
#       CALL main()
#
# =============================================================================

import os
import pandas as pd

from simulator import DigitalTwinSimulator
from ml_models import train_models
from anomaly import train_anomaly_model
from optimizer import optimize_dataframe


def main():
    """
    Full pipeline:
      1. Run physics simulation → write realtime.csv
      2. Train energy, temperature, and anomaly ML models
      3. Compute optimisation recommendations on the latest 200 rows
      4. Print diagnostics to stdout
    """
    # --- PSEUDO: create output directories if they don't exist ---
    os.makedirs("data",   exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # -------------------------------------------------------------------------
    # Step 1 — Run Simulation
    # -------------------------------------------------------------------------
    # --- PSEUDO: initialise simulator (creates rooms + weather model) ---
    sim = DigitalTwinSimulator()

    # --- PSEUDO: execute time-loop, collect one record per (hour × room) ---
    records = sim.run()
    df = pd.DataFrame(records)

    csv_path = "data/realtime.csv"
    # --- PSEUDO: persist dataset for dashboard and ML training ---
    df.to_csv(csv_path, index=False)

    # -------------------------------------------------------------------------
    # Step 2 — Train ML Models
    # -------------------------------------------------------------------------
    # --- PSEUDO: train RandomForest energy + temperature predictors ---
    metrics = train_models(csv_path)

    # --- PSEUDO: train IsolationForest anomaly detector (annotates CSV) ---
    anomaly_info = train_anomaly_model(csv_path)

    # -------------------------------------------------------------------------
    # Step 3 — Optimisation Recommendations
    # -------------------------------------------------------------------------
    # --- PSEUDO: run rule engine over the most recent 200 records ---
    opt_df = optimize_dataframe(df.tail(200).copy())
    opt_df.to_csv("data/optimizations_latest.csv", index=False)

    # -------------------------------------------------------------------------
    # Step 4 — Diagnostics
    # -------------------------------------------------------------------------
    print("Simulation completed successfully.")
    print(f"Dataset saved to: {csv_path}")
    print("Model Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")
    print("Anomaly Metrics:")
    for k, v in anomaly_info.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
