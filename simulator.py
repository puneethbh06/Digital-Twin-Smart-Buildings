# =============================================================================
# simulator.py — Main Simulation Engine
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   SET global random seeds (numpy + Python) for reproducibility
#
#   CLASS DigitalTwinSimulator:
#
#       INIT:
#           CREATE WeatherModel instance
#           FOR each building in ROOMS_PER_BUILDING:
#               FOR each room spec in building:
#                   INSTANTIATE Room(building, name, floor, x, y, room_type)
#                   APPEND to self.rooms list
#
#       METHOD inject_fault(room):
#           # ServerRooms have a higher fault probability
#           fault_prob ← FAULT_PROBABILITY + (0.015 if ServerRoom else 0)
#           IF random() < fault_prob:
#               room.fault_flag ← 1
#               room.energy_kwh += uniform(2.0, 5.0)   # surge
#               room.temperature += uniform(1.5, 3.5)  # overheating
#           ELSE:
#               room.fault_flag ← 0
#
#       METHOD run() → list[dict]:
#           records ← []
#           total_hours ← SIM_DAYS × HOURS_PER_DAY
#
#           FOR t in range(total_hours):
#               (outdoor_temp, outdoor_humidity) ← weather.step(t)
#
#               FOR each room in self.rooms:
#                   state ← room.simulate_step(outdoor_temp, outdoor_humidity)
#                   inject_fault(room)
#
#                   # Propagate post-fault values back to state snapshot
#                   state.temperature ← room.temperature
#                   state.energy_kwh  ← room.energy_kwh
#                   state.fault_flag  ← room.fault_flag
#
#                   APPEND flat record dict to records
#                       (time, day, hour, building, room, room_type, floor,
#                        x, y, outdoor_temp, outdoor_humidity, room_temp,
#                        room_humidity, occupancy, hvac_on, lights_on,
#                        water_liters, energy_kwh, fault_flag)
#
#           RETURN records
#
# =============================================================================

import random
import numpy as np
from config import (
    ROOMS_PER_BUILDING, SIM_DAYS, HOURS_PER_DAY,
    FAULT_PROBABILITY, RANDOM_SEED,
)
from weather import WeatherModel
from building import Room

# --- PSEUDO: fix all random sources for reproducible runs ---
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)


class DigitalTwinSimulator:
    """Orchestrates the full multi-building, multi-room simulation loop."""

    def __init__(self):
        # --- PSEUDO: create shared weather model ---
        self.weather = WeatherModel()

        # --- PSEUDO: instantiate every room defined in config ---
        self.rooms = []
        for building, room_specs in ROOMS_PER_BUILDING.items():
            for spec in room_specs:
                self.rooms.append(
                    Room(
                        building,
                        spec["name"],
                        spec["floor"],
                        spec["x"],
                        spec["y"],
                        spec["room_type"],
                    )
                )

    def inject_fault(self, room: Room):
        """
        Randomly inject a hardware/sensor fault into a room.
        Faults raise energy consumption and temperature to simulate
        HVAC failures, sensor errors, or equipment malfunctions.
        """
        # --- PSEUDO: server rooms fault slightly more often ---
        p = FAULT_PROBABILITY + (0.015 if room.room_type == "ServerRoom" else 0.0)

        if random.random() < p:
            # --- PSEUDO: mark room as faulted and spike readings ---
            room.fault_flag = 1
            room.energy_kwh = round(room.energy_kwh + random.uniform(2.0, 5.0), 2)
            room.temperature += random.uniform(1.5, 3.5)
        else:
            room.fault_flag = 0

    def run(self) -> list:
        """
        Run the full simulation for SIM_DAYS × HOURS_PER_DAY time-steps.

        Returns:
            list[dict]: One flat record per (hour, room) pair, ready for
                        conversion to a pandas DataFrame or CSV export.
        """
        records = []
        total_hours = SIM_DAYS * HOURS_PER_DAY

        for t in range(total_hours):
            # --- PSEUDO: advance weather one hour ---
            outdoor_temp, outdoor_humidity = self.weather.step(t)

            for room in self.rooms:
                # --- PSEUDO: advance room physics ---
                state = room.simulate_step(outdoor_temp, outdoor_humidity)

                # --- PSEUDO: optionally inject a fault this step ---
                self.inject_fault(room)

                # --- PSEUDO: push post-fault values into the snapshot ---
                state.temperature = round(room.temperature, 2)
                state.energy_kwh  = round(room.energy_kwh, 2)
                state.fault_flag  = room.fault_flag

                # --- PSEUDO: flatten state to a dict row for the CSV ---
                records.append({
                    "time":             t,
                    "day":              t // 24,
                    "hour":             t % 24,
                    "building":         state.building,
                    "room":             state.room,
                    "room_type":        state.room_type,
                    "floor":            state.floor,
                    "x":                state.x,
                    "y":                state.y,
                    "outdoor_temp":     outdoor_temp,
                    "outdoor_humidity": round(outdoor_humidity, 2),
                    "room_temp":        state.temperature,
                    "room_humidity":    round(state.humidity, 2),
                    "occupancy":        state.occupancy,
                    "hvac_on":          state.hvac_on,
                    "lights_on":        state.lights_on,
                    "water_liters":     state.water_liters,
                    "energy_kwh":       state.energy_kwh,
                    "fault_flag":       state.fault_flag,
                })

        return records
