"""
F1 Car Telemetry & Aerodynamics Simulator
Generates realistic real-time data for the monitoring dashboard.
"""

import numpy as np
import time
from dataclasses import dataclass, field
from typing import Dict, List
import math


@dataclass
class CarState:
    name: str
    team: str
    color: str
    number: int
    speed: float = 0.0          # km/h
    rpm: float = 0.0
    gear: int = 1
    throttle: float = 0.0       # 0-100
    brake: float = 0.0          # 0-100
    drs: bool = False
    tire_temp_fl: float = 85.0
    tire_temp_fr: float = 85.0
    tire_temp_rl: float = 90.0
    tire_temp_rr: float = 90.0
    engine_temp: float = 95.0
    downforce: float = 0.0      # kg
    drag: float = 0.0           # N
    aero_efficiency: float = 0.0
    lateral_g: float = 0.0
    fuel: float = 100.0
    # Internal simulation state
    _phase: float = 0.0
    _lap_progress: float = 0.0
    _base_speed: float = 280.0
    _wing_level: float = 1.0    # 0.6 (low drag) to 1.4 (high downforce)


# Realistic F1 cars (2024/2025 style)
CARS = [
    CarState("Max Verstappen", "Red Bull Racing", "#3671C6", 1),
    CarState("Lando Norris", "McLaren", "#FF8000", 4),
    CarState("Charles Leclerc", "Ferrari", "#E8002D", 16),
    CarState("Lewis Hamilton", "Mercedes", "#27F4D2", 44),
    CarState("Oscar Piastri", "McLaren", "#FF8000", 81),
    CarState("Carlos Sainz", "Ferrari", "#E8002D", 55),
]


class F1Simulator:
    def __init__(self):
        self.cars: Dict[int, CarState] = {c.number: c for c in CARS}
        self.track_type = "balanced"  # balanced | high_downforce | low_drag
        self.running = True
        self.start_time = time.time()
        self.history: Dict[int, Dict[str, List[float]]] = {
            num: {
                "speed": [], "rpm": [], "downforce": [], "drag": [],
                "throttle": [], "time": []
            } for num in self.cars
        }
        self.max_history = 120  # points

        # Track characteristics affect aero multipliers
        self.track_aero = {
            "balanced": {"cl_mult": 1.0, "cd_mult": 1.0, "base_speed": 290},
            "high_downforce": {"cl_mult": 1.35, "cd_mult": 1.25, "base_speed": 265},
            "low_drag": {"cl_mult": 0.75, "cd_mult": 0.70, "base_speed": 330},
        }

    def set_track(self, track: str):
        if track in self.track_aero:
            self.track_type = track
            for car in self.cars.values():
                car._base_speed = self.track_aero[track]["base_speed"]

    def _aero_forces(self, speed_kmh: float, wing_level: float) -> tuple:
        """
        Calculate approximate downforce and drag using simplified aero equations.
        Downforce (L) = 0.5 * rho * v^2 * A * CL
        Drag (D) = 0.5 * rho * v^2 * A * CD
        """
        # Convert to m/s
        v = speed_kmh / 3.6
        rho = 1.225          # air density kg/m³
        area = 1.5           # frontal area m² (approx for modern F1)

        track = self.track_aero[self.track_type]
        # Base coefficients (typical modern F1 range)
        # CL around 3.5–5.5 depending on setup, CD around 0.9–1.4
        cl = 4.2 * wing_level * track["cl_mult"]
        cd = 1.05 * wing_level * track["cd_mult"]

        # DRS effect: reduces CD significantly when open
        # (handled outside when DRS active)

        downforce_n = 0.5 * rho * v * v * area * cl
        drag_n = 0.5 * rho * v * v * area * cd

        downforce_kg = downforce_n / 9.81
        efficiency = cl / cd if cd > 0 else 0

        return downforce_kg, drag_n, efficiency

    def update(self):
        """Advance simulation by one step for all cars."""
        t = time.time() - self.start_time

        for car in self.cars.values():
            # Each car has slightly different phase and base performance
            phase_offset = car.number * 0.7
            car._phase = t * 0.35 + phase_offset

            # Simulate a lap-like speed profile (high speed straights + slower corners)
            # Use a combination of sine waves to create realistic variation
            progress = (car._phase % (2 * math.pi)) / (2 * math.pi)
            car._lap_progress = progress

            # Speed profile: mostly high, dips in "corners"
            corner_factor = (
                0.55 + 0.45 * abs(math.sin(car._phase * 1.7))
                + 0.15 * math.sin(car._phase * 3.1)
            )
            noise = np.random.normal(0, 2.5)

            target_speed = car._base_speed * corner_factor + noise
            # Smooth the speed a bit
            car.speed = 0.82 * car.speed + 0.18 * max(80, min(360, target_speed))

            # Throttle / Brake logic
            if car.speed < target_speed - 8:
                car.throttle = min(100, car.throttle + 12 + np.random.uniform(-3, 3))
                car.brake = max(0, car.brake - 25)
            elif car.speed > target_speed + 12:
                car.throttle = max(0, car.throttle - 20)
                car.brake = min(100, car.brake + 30 + np.random.uniform(-5, 5))
            else:
                car.throttle = 0.7 * car.throttle + 0.3 * (70 + np.random.uniform(-10, 10))
                car.brake = max(0, car.brake * 0.6)

            car.throttle = float(np.clip(car.throttle, 0, 100))
            car.brake = float(np.clip(car.brake, 0, 100))

            # Gear & RPM (simplified mapping)
            if car.speed < 80:
                car.gear = 1
            elif car.speed < 120:
                car.gear = 2
            elif car.speed < 160:
                car.gear = 3
            elif car.speed < 200:
                car.gear = 4
            elif car.speed < 240:
                car.gear = 5
            elif car.speed < 280:
                car.gear = 6
            elif car.speed < 315:
                car.gear = 7
            else:
                car.gear = 8

            # RPM rises with throttle and gear, drops on braking
            base_rpm = 4500 + car.gear * 850
            car.rpm = base_rpm + car.throttle * 55 - car.brake * 25 + np.random.normal(0, 80)
            car.rpm = float(np.clip(car.rpm, 4000, 12800))

            # DRS: open on high-speed sections when throttle is high
            car.drs = car.speed > 280 and car.throttle > 85 and car.brake < 5

            # Wing level slightly different per team philosophy
            if "Red Bull" in car.team:
                car._wing_level = 1.05
            elif "McLaren" in car.team:
                car._wing_level = 1.00
            elif "Ferrari" in car.team:
                car._wing_level = 1.10
            else:
                car._wing_level = 0.95

            # Aerodynamics
            df, drag, eff = self._aero_forces(car.speed, car._wing_level)
            if car.drs:
                # DRS reduces drag significantly (~20-30%)
                drag *= 0.72
                df *= 0.92   # small downforce loss too
                eff = (df * 9.81) / drag if drag > 0 else 0

            car.downforce = df
            car.drag = drag
            car.aero_efficiency = eff

            # Tire temperatures (rise with speed + lateral load simulation)
            lateral = abs(math.sin(car._phase * 2.3)) * (car.speed / 100)
            car.lateral_g = lateral * 1.8

            heat = (car.speed / 15) + (car.throttle * 0.08) + lateral * 8
            car.tire_temp_fl = 0.92 * car.tire_temp_fl + 0.08 * (78 + heat + np.random.uniform(-2, 2))
            car.tire_temp_fr = 0.92 * car.tire_temp_fr + 0.08 * (79 + heat + np.random.uniform(-2, 2))
            car.tire_temp_rl = 0.92 * car.tire_temp_rl + 0.08 * (82 + heat * 1.1 + np.random.uniform(-2, 2))
            car.tire_temp_rr = 0.92 * car.tire_temp_rr + 0.08 * (83 + heat * 1.1 + np.random.uniform(-2, 2))

            # Engine temp
            car.engine_temp = 0.95 * car.engine_temp + 0.05 * (90 + car.throttle * 0.25 + np.random.uniform(-1, 1))

            # Fuel slowly decreases
            car.fuel = max(0, car.fuel - 0.008)

            # Store history
            hist = self.history[car.number]
            hist["speed"].append(car.speed)
            hist["rpm"].append(car.rpm)
            hist["downforce"].append(car.downforce)
            hist["drag"].append(car.drag)
            hist["throttle"].append(car.throttle)
            hist["time"].append(t)

            # Keep history size limited
            for key in hist:
                if len(hist[key]) > self.max_history:
                    hist[key] = hist[key][-self.max_history:]

    def get_car(self, number: int) -> CarState:
        return self.cars.get(number)

    def get_all_cars(self) -> List[CarState]:
        return list(self.cars.values())
