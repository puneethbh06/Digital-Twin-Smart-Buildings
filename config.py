# =============================================================================
# config.py — Central Configuration File
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   DEFINE building_room_map:
#       FOR each building (North_Block, South_Block):
#           LIST rooms with name, floor, (x,y) grid position, and room_type
#
#   DEFINE simulation parameters:
#       SIM_DAYS           → total days to simulate
#       HOURS_PER_DAY      → time-steps per day (hourly resolution)
#
#   DEFINE environment defaults:
#       INITIAL_OUTDOOR_TEMP     → starting ambient temperature (°C)
#       INITIAL_OUTDOOR_HUMIDITY → starting relative humidity (%)
#
#   DEFINE comfort thresholds:
#       COMFORT_LOW   → minimum acceptable indoor temp (°C)
#       COMFORT_HIGH  → maximum acceptable indoor temp (°C)
#
#   DEFINE fault & seed:
#       FAULT_PROBABILITY → probability a room faults per time-step
#       RANDOM_SEED       → reproducibility seed for all RNG
#
#   DEFINE output paths:
#       DATA_CSV      → where simulated records are saved
#       ENERGY_MODEL  → serialized energy prediction model
#       TEMP_MODEL    → serialized temperature prediction model
#       ANOMALY_MODEL → serialized anomaly detection model
#
# =============================================================================

# --- Building & Room Layout -------------------------------------------

ROOMS_PER_BUILDING = {
    "North_Block": [
        {"name": "Office_A1",     "floor": 1, "x": 0, "y": 0, "room_type": "Office"},
        {"name": "Lab_A1",        "floor": 1, "x": 2, "y": 0, "room_type": "Lab"},
        {"name": "Conference_A1", "floor": 1, "x": 4, "y": 0, "room_type": "Conference"},
        {"name": "Classroom_A2",  "floor": 2, "x": 0, "y": 2, "room_type": "Classroom"},
        {"name": "Office_A2",     "floor": 2, "x": 2, "y": 2, "room_type": "Office"},
        {"name": "ServerRoom_A3", "floor": 3, "x": 4, "y": 2, "room_type": "ServerRoom"},
    ],
    "South_Block": [
        {"name": "Office_B1",     "floor": 1, "x": 0, "y": 0, "room_type": "Office"},
        {"name": "Lab_B1",        "floor": 1, "x": 2, "y": 0, "room_type": "Lab"},
        {"name": "Conference_B1", "floor": 1, "x": 4, "y": 0, "room_type": "Conference"},
        {"name": "Classroom_B2",  "floor": 2, "x": 0, "y": 2, "room_type": "Classroom"},
        {"name": "Office_B2",     "floor": 2, "x": 2, "y": 2, "room_type": "Office"},
        {"name": "ServerRoom_B3", "floor": 3, "x": 4, "y": 2, "room_type": "ServerRoom"},
    ],
}

# --- Simulation Time Parameters ---------------------------------------

SIM_DAYS = 30           # Number of days to simulate
HOURS_PER_DAY = 24      # Hourly time-steps per day

# --- Initial Weather Conditions ---------------------------------------

INITIAL_OUTDOOR_TEMP = 26.0       # °C
INITIAL_OUTDOOR_HUMIDITY = 55.0   # % relative humidity

# --- Comfort Band (HVAC triggers) -------------------------------------

COMFORT_LOW = 22.0    # Below this → HVAC heats
COMFORT_HIGH = 25.0   # Above this → HVAC cools

# --- Fault Injection --------------------------------------------------

FAULT_PROBABILITY = 0.03   # 3% chance per room per step; +1.5% for ServerRooms
RANDOM_SEED = 42           # Global seed for reproducibility

# --- File / Model Paths -----------------------------------------------

DATA_CSV      = "data/realtime.csv"
ENERGY_MODEL  = "models/energy_model.pkl"
TEMP_MODEL    = "models/temp_model.pkl"
ANOMALY_MODEL = "models/anomaly_model.pkl"
