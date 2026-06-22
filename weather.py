# =============================================================================
# weather.py — Outdoor Weather Model
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   CLASS WeatherModel:
#
#       INIT:
#           SET base_temp     ← INITIAL_OUTDOOR_TEMP from config
#           SET base_humidity ← INITIAL_OUTDOOR_HUMIDITY from config
#
#       METHOD step(hour_index):
#           # Compute sinusoidal daily temperature cycle
#           daily_temp     ← 5.5 × sin(2π × (hour_index mod 24) / 24)
#
#           # Humidity peaks ~6 hours after temperature trough (phase offset)
#           daily_humidity ← 12.0 × sin(2π × ((hour_index + 6) mod 24) / 24)
#
#           # Add Gaussian noise to simulate natural variation
#           outdoor_temp     ← base_temp + daily_temp + gauss(μ=0, σ=0.6)
#           outdoor_humidity ← base_humidity + daily_humidity + gauss(μ=0, σ=1.2)
#
#           RETURN (round(outdoor_temp, 2), round(outdoor_humidity, 2))
#
# =============================================================================

import math
import random
from config import INITIAL_OUTDOOR_TEMP, INITIAL_OUTDOOR_HUMIDITY, RANDOM_SEED

random.seed(RANDOM_SEED)


class WeatherModel:
    """Simulates outdoor temperature and humidity using a sinusoidal daily cycle
    plus Gaussian noise. No external data source required — fully synthetic."""

    def __init__(self):
        # --- PSEUDO: initialise base climate from config ---
        self.base_temp = INITIAL_OUTDOOR_TEMP
        self.base_humidity = INITIAL_OUTDOOR_HUMIDITY

    def step(self, hour_index: int):
        """
        Advance weather by one hour.

        Args:
            hour_index (int): Absolute hour counter since simulation start.

        Returns:
            tuple: (outdoor_temp °C, outdoor_humidity %)
        """
        # --- PSEUDO: sinusoidal daily temperature swing (±5.5°C) ---
        daily_temp = 5.5 * math.sin(2 * math.pi * (hour_index % 24) / 24)

        # --- PSEUDO: humidity inversely correlated, phase-shifted by 6 h ---
        daily_humidity = 12.0 * math.sin(2 * math.pi * ((hour_index + 6) % 24) / 24)

        # --- PSEUDO: add small Gaussian noise for realism ---
        outdoor_temp = self.base_temp + daily_temp + random.gauss(0, 0.6)
        outdoor_humidity = self.base_humidity + daily_humidity + random.gauss(0, 1.2)

        return round(outdoor_temp, 2), round(outdoor_humidity, 2)
