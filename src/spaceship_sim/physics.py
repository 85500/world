"""Physics helpers and flight model for the spaceship prototype."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Tuple

from .components import Component, Engine, FuelTank, Wing

Vector2 = Tuple[float, float]


EARTH_GRAVITY = 9.80665  # m/s^2
ATMOSPHERIC_DENSITY = 1.225  # kg/m^3 at sea level
DRAG_COEFFICIENT = 0.7  # generic spacecraft-ish value


def add(a: Vector2, b: Vector2) -> Vector2:
    return a[0] + b[0], a[1] + b[1]


def sub(a: Vector2, b: Vector2) -> Vector2:
    return a[0] - b[0], a[1] - b[1]


def mul(a: Vector2, scalar: float) -> Vector2:
    return a[0] * scalar, a[1] * scalar


def length(v: Vector2) -> float:
    return math.hypot(v[0], v[1])


def normalize(v: Vector2) -> Vector2:
    mag = length(v)
    if mag == 0:
        return 0.0, 0.0
    return v[0] / mag, v[1] / mag


def rotate(v: Vector2, angle: float) -> Vector2:
    c, s = math.cos(angle), math.sin(angle)
    return v[0] * c - v[1] * s, v[0] * s + v[1] * c


def dot(a: Vector2, b: Vector2) -> float:
    return a[0] * b[0] + a[1] * b[1]


def cross_z(a: Vector2, b: Vector2) -> float:
    return a[0] * b[1] - a[1] * b[0]


def aerodynamic_drag(velocity: Vector2, reference_area: float, cd: float = DRAG_COEFFICIENT) -> Vector2:
    speed = length(velocity)
    if speed == 0:
        return 0.0, 0.0
    drag_magnitude = 0.5 * ATMOSPHERIC_DENSITY * cd * reference_area * speed ** 2
    return mul(normalize(mul(velocity, -1.0)), drag_magnitude)


def aerodynamic_lift(wing: Wing, velocity_body: Vector2) -> Vector2:
    forward = (1.0, 0.0)
    speed = length(velocity_body)
    if speed == 0:
        return 0.0, 0.0
    angle = math.degrees(math.atan2(velocity_body[1], velocity_body[0]))
    alpha = max(min(-angle, wing.stall_angle), -wing.stall_angle)
    cl = (wing.lift_curve * math.radians(alpha))
    q = 0.5 * ATMOSPHERIC_DENSITY * speed ** 2
    lift_magnitude = cl * q * wing.area
    lift_direction = (0.0, 1.0)
    return mul(lift_direction, lift_magnitude)


@dataclass
class PropulsionResult:
    force: Vector2
    torque: float
    fuel_used: float


@dataclass
class ForceResult:
    linear: Vector2
    torque: float


def compute_propulsion(
    engines: Iterable[Engine],
    fuel_tanks: Iterable[FuelTank],
    throttle: float,
    orientation: float,
    com: Vector2,
) -> PropulsionResult:
    throttle = max(0.0, min(1.0, throttle))
    total_force = (0.0, 0.0)
    total_torque = 0.0
    fuel_needed = 0.0
    for engine in engines:
        thrust_vector = rotate(engine.direction, orientation)
        thrust_force = mul(thrust_vector, engine.thrust * throttle)
        lever = sub(engine.position, com)
        total_force = add(total_force, thrust_force)
        total_torque += cross_z(lever, thrust_force)
        fuel_needed += engine.fuel_consumption * throttle

    fuel_available = sum(tank.fuel_level for tank in fuel_tanks)
    fuel_used = min(fuel_available, fuel_needed)
    if fuel_needed > 0:
        scale = fuel_used / fuel_needed
        total_force = mul(total_force, scale)
        total_torque *= scale
    if fuel_used > 0:
        drain = fuel_used
        for tank in fuel_tanks:
            if drain <= 0:
                break
            taken = min(tank.fuel_level, drain)
            tank.fuel_level -= taken
            drain -= taken
    return PropulsionResult(total_force, total_torque, fuel_used)


def compute_aero_forces(
    components: Iterable[Component],
    wings: Iterable[Wing],
    velocity: Vector2,
    angular_velocity: float,
    orientation: float,
    com: Vector2,
) -> ForceResult:
    total_force = (0.0, 0.0)
    total_torque = 0.0
    for comp in components:
        world_velocity = add(velocity, (-angular_velocity * (comp.position[1] - com[1]), angular_velocity * (comp.position[0] - com[0])))
        drag_force_body = aerodynamic_drag(rotate(world_velocity, -orientation), comp.drag_area)
        drag_force_world = rotate(drag_force_body, orientation)
        lever = sub(comp.position, com)
        total_force = add(total_force, drag_force_world)
        total_torque += cross_z(lever, drag_force_world)
    for wing in wings:
        world_velocity = add(velocity, (-angular_velocity * (wing.position[1] - com[1]), angular_velocity * (wing.position[0] - com[0])))
        velocity_body = rotate(world_velocity, -orientation)
        lift_body = aerodynamic_lift(wing, velocity_body)
        lift_world = rotate(lift_body, orientation)
        lever = sub(wing.position, com)
        total_force = add(total_force, lift_world)
        total_torque += cross_z(lever, lift_world)
    return ForceResult(total_force, total_torque)


def integrate(
    position: Vector2,
    velocity: Vector2,
    orientation: float,
    angular_velocity: float,
    force: Vector2,
    torque: float,
    mass: float,
    inertia: float,
    dt: float,
) -> Tuple[Vector2, Vector2, float, float]:
    acceleration = mul(force, 1.0 / mass) if mass > 0 else (0.0, 0.0)
    velocity = add(velocity, mul(acceleration, dt))
    position = add(position, mul(velocity, dt))
    angular_acc = torque / inertia if inertia > 0 else 0.0
    angular_velocity += angular_acc * dt
    orientation += angular_velocity * dt
    return position, velocity, orientation, angular_velocity
