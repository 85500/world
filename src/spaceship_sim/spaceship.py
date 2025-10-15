"""Spaceship assembly and simulation routines."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

from .components import Component, Engine, FuelTank, Wing
from .physics import (
    EARTH_GRAVITY,
    ForceResult,
    PropulsionResult,
    add,
    compute_aero_forces,
    compute_propulsion,
    cross_z,
    integrate,
    length,
    mul,
    rotate,
    sub,
)

Vector2 = Tuple[float, float]


@dataclass
class Spaceship:
    """A spacecraft assembled from arbitrary components."""

    components: List[Component] = field(default_factory=list)
    engines: List[Engine] = field(default_factory=list)
    fuel_tanks: List[FuelTank] = field(default_factory=list)
    wings: List[Wing] = field(default_factory=list)

    position: Vector2 = (0.0, 0.0)
    velocity: Vector2 = (0.0, 0.0)
    orientation: float = math.radians(90)
    angular_velocity: float = 0.0

    def all_components(self) -> Iterable[Component]:
        yield from self.components
        yield from self.engines
        yield from self.fuel_tanks
        yield from self.wings

    @property
    def mass(self) -> float:
        return sum(comp.mass for comp in self.all_components())

    @property
    def center_of_mass(self) -> Vector2:
        total_mass = self.mass
        if total_mass == 0:
            return 0.0, 0.0
        cx = sum(comp.position[0] * comp.mass for comp in self.all_components()) / total_mass
        cy = sum(comp.position[1] * comp.mass for comp in self.all_components()) / total_mass
        return cx, cy

    @property
    def moment_of_inertia(self) -> float:
        com = self.center_of_mass
        inertia = 0.0
        for comp in self.all_components():
            r = sub(comp.position, com)
            inertia += comp.inertia + comp.mass * (r[0] ** 2 + r[1] ** 2)
        return inertia

    def attach(self, component: Component) -> None:
        if isinstance(component, Engine):
            self.engines.append(component)
        elif isinstance(component, FuelTank):
            self.fuel_tanks.append(component)
        elif isinstance(component, Wing):
            self.wings.append(component)
        else:
            self.components.append(component)

    def total_drag_area(self) -> float:
        return sum(comp.drag_area for comp in self.all_components())

    def apply_controls(self, throttle: float, control_surfaces: Dict[str, float]) -> Tuple[PropulsionResult, ForceResult]:
        com = self.center_of_mass
        propulsion = compute_propulsion(self.engines, self.fuel_tanks, throttle, self.orientation, com)
        aero = compute_aero_forces(list(self.all_components()), self.wings, self.velocity, self.angular_velocity, self.orientation, com)
        return propulsion, aero

    def simulate_step(self, throttle: float, dt: float, control_surfaces: Dict[str, float] | None = None) -> None:
        if control_surfaces is None:
            control_surfaces = {}
        propulsion, aero = self.apply_controls(throttle, control_surfaces)
        weight = (0.0, -self.mass * EARTH_GRAVITY)
        total_force = add(add(propulsion.force, aero.linear), weight)
        com = self.center_of_mass
        gravity_torque = 0.0
        total_torque = propulsion.torque + aero.torque + gravity_torque
        self.position, self.velocity, self.orientation, self.angular_velocity = integrate(
            self.position,
            self.velocity,
            self.orientation,
            self.angular_velocity,
            total_force,
            total_torque,
            self.mass,
            max(self.moment_of_inertia, 1e-3),
            dt,
        )

    def summary(self) -> str:
        lines = ["Spaceship summary:"]
        lines.append(f"  Mass: {self.mass:.1f} kg")
        lines.append(f"  Center of mass: {self.center_of_mass}")
        lines.append(f"  Moment of inertia: {self.moment_of_inertia:.1f} kg*m^2")
        lines.append(f"  Drag area: {self.total_drag_area():.2f} m^2")
        lines.append("  Engines:")
        for engine in self.engines:
            lines.append(f"    {engine.name}: thrust={engine.thrust} N, gimbal={engine.gimbal_limit}")
        lines.append("  Fuel tanks:")
        for tank in self.fuel_tanks:
            lines.append(f"    {tank.name}: {tank.fuel_level:.1f}/{tank.fuel_capacity} kg")
        lines.append("  Wings:")
        for wing in self.wings:
            lines.append(f"    {wing.name}: area={wing.area} m^2")
        return "\n".join(lines)
