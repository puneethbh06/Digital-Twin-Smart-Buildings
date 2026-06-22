# =============================================================================
# building.py — Room State & Physics Simulation
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   DATACLASS RoomState:
#       Fields: building, room, room_type, floor, x, y,
#               temperature, humidity, occupancy, hvac_on, lights_on,
#               water_liters, energy_kwh, fault_flag, anomaly_score
#       METHOD to_dict() → convert dataclass to plain dict
#
#   CLASS Room:
#
#       INIT(building, name, floor, x, y, room_type):
#           SET room identity fields
#           SET base_temp ← 22.5 if ServerRoom else 24.0
#           RANDOMISE initial temperature, humidity, occupancy
#           INITIALISE hvac_on=1, lights_on=1, water=0, energy=0
#
#       METHOD update_occupancy():
#           # ServerRooms have low, steady occupancy; others fluctuate more
#           delta ← random integer in [-1,+2] (ServerRoom) or [-5,+6] (others)
#           self.occupancy ← clamp(occupancy + delta, min=0, max=35)
#
#       METHOD simulate_step(outdoor_temp, outdoor_humidity):
#           CALL update_occupancy()
#
#           # Determine comfort band (tighter for ServerRooms)
#           IF ServerRoom: comfort_low=20, comfort_high=23
#           ELSE:          comfort_low=COMFORT_LOW, comfort_high=COMFORT_HIGH
#
#           # HVAC control logic (bang-bang controller)
#           IF temperature > comfort_high + 0.5:
#               hvac_on = 1, hvac_effect = −0.9   (cooling)
#           ELIF temperature < comfort_low − 0.5:
#               hvac_on = 1, hvac_effect = +0.6   (heating)
#           ELSE:
#               hvac_on = 0, hvac_effect = 0.0    (idle)
#
#           lights_on ← 1 if occupancy > 0 else 0
#
#           # Temperature dynamics: outdoor influence + HVAC + noise
#           temperature += 0.10 × (outdoor_temp − temperature)
#                        + hvac_effect
#                        + uniform(−0.15, +0.15)
#
#           # Humidity dynamics: outdoor influence + noise
#           humidity += 0.06 × (outdoor_humidity − humidity)
#                     + uniform(−0.7, +0.7)
#
#           # Water consumption model
#           base_water ← 1.5 (ServerRoom) or 2.0 (other)
#           water_liters ← base_water + 0.22 × occupancy + noise
#
#           # Energy consumption model
#           room_type_factor ← {Office:0.5, Lab:0.8, Conference:0.7,
#                               Classroom:0.6, ServerRoom:1.5}
#           energy_kwh ← 1.7×hvac_on + 0.65×lights_on
#                       + 0.06×occupancy + room_type_factor + noise
#
#           RETURN RoomState snapshot with all computed values
#
# =============================================================================

from dataclasses import dataclass, asdict
import random
from config import COMFORT_LOW, COMFORT_HIGH


@dataclass
class RoomState:
    """Immutable snapshot of a room's sensor readings at one time-step."""
    building: str
    room: str
    room_type: str
    floor: int
    x: float
    y: float
    temperature: float
    humidity: float
    occupancy: int
    hvac_on: int
    lights_on: int
    water_liters: float
    energy_kwh: float
    fault_flag: int = 0
    anomaly_score: float = 0.0

    def to_dict(self):
        # --- PSEUDO: serialise to plain dict for CSV / JSON export ---
        return asdict(self)


class Room:
    """Stateful room object that evolves through physics-based simulation."""

    def __init__(self, building: str, name: str, floor: int,
                 x: float, y: float, room_type: str):
        # --- PSEUDO: store room identity ---
        self.building = building
        self.name = name
        self.floor = floor
        self.x = x
        self.y = y
        self.room_type = room_type

        # --- PSEUDO: set initial state (ServerRooms run cooler) ---
        base_temp = 24.0 if room_type != "ServerRoom" else 22.5
        self.temperature = base_temp + random.uniform(-0.8, 0.8)
        self.humidity = 50.0 + random.uniform(-2.0, 2.0)
        self.occupancy = random.randint(0, 20)
        self.hvac_on = 1
        self.lights_on = 1
        self.water_liters = 0.0
        self.energy_kwh = 0.0
        self.fault_flag = 0
        self.anomaly_score = 0.0

    def update_occupancy(self):
        """
        Stochastically change occupancy by a small delta each hour.
        ServerRooms stay near-constant; general rooms fluctuate widely.
        """
        # --- PSEUDO: server rooms rarely change headcount ---
        if self.room_type == "ServerRoom":
            delta = random.randint(-1, 2)
        else:
            delta = random.randint(-5, 6)

        # --- PSEUDO: clamp to valid range [0, 35] ---
        self.occupancy = max(0, min(35, self.occupancy + delta))

    def simulate_step(self, outdoor_temp: float, outdoor_humidity: float) -> RoomState:
        """
        Advance room physics by one hour.

        Args:
            outdoor_temp     (float): Current outdoor temperature (°C).
            outdoor_humidity (float): Current outdoor humidity (%).

        Returns:
            RoomState: Snapshot of sensor readings after this step.
        """
        # --- PSEUDO: update occupancy for this time-step ---
        self.update_occupancy()

        # --- PSEUDO: pick comfort thresholds by room type ---
        if self.room_type == "ServerRoom":
            comfort_low, comfort_high = 20.0, 23.0
        else:
            comfort_low, comfort_high = COMFORT_LOW, COMFORT_HIGH

        # --- PSEUDO: bang-bang HVAC controller ---
        if self.temperature > comfort_high + 0.5:
            self.hvac_on = 1
            hvac_effect = -0.9       # cooling
        elif self.temperature < comfort_low - 0.5:
            self.hvac_on = 1
            hvac_effect = 0.6        # heating
        else:
            self.hvac_on = 0
            hvac_effect = 0.0        # idle

        # --- PSEUDO: lights follow occupancy ---
        self.lights_on = 1 if self.occupancy > 0 else 0

        # --- PSEUDO: first-order temperature dynamics ---
        self.temperature += (
            0.10 * (outdoor_temp - self.temperature)
            + hvac_effect
            + random.uniform(-0.15, 0.15)
        )

        # --- PSEUDO: first-order humidity dynamics ---
        self.humidity += (
            0.06 * (outdoor_humidity - self.humidity)
            + random.uniform(-0.7, 0.7)
        )

        # --- PSEUDO: water consumption proportional to occupancy ---
        base_water = 1.5 if self.room_type == "ServerRoom" else 2.0
        self.water_liters = round(
            max(0.0, base_water + 0.22 * self.occupancy + random.uniform(-0.4, 0.5)), 2
        )

        # --- PSEUDO: energy model (HVAC + lighting + occupancy + room factor) ---
        room_type_factor = {
            "Office": 0.5,
            "Lab": 0.8,
            "Conference": 0.7,
            "Classroom": 0.6,
            "ServerRoom": 1.5,
        }.get(self.room_type, 0.6)

        self.energy_kwh = round(
            (1.7 * self.hvac_on)
            + (0.65 * self.lights_on)
            + (0.06 * self.occupancy)
            + room_type_factor
            + random.uniform(0.0, 0.45),
            2,
        )

        # --- PSEUDO: package state into immutable RoomState snapshot ---
        return RoomState(
            building=self.building,
            room=self.name,
            room_type=self.room_type,
            floor=self.floor,
            x=self.x,
            y=self.y,
            temperature=round(self.temperature, 2),
            humidity=round(self.humidity, 2),
            occupancy=self.occupancy,
            hvac_on=self.hvac_on,
            lights_on=self.lights_on,
            water_liters=self.water_liters,
            energy_kwh=self.energy_kwh,
            fault_flag=self.fault_flag,
            anomaly_score=self.anomaly_score,
        )
