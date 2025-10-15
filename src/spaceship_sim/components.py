"""Component definitions for assembling a spaceship prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

Vector2 = Tuple[float, float]


def add_vectors(a: Vector2, b: Vector2) -> Vector2:
    return a[0] + b[0], a[1] + b[1]


@dataclass
class Component:
    """Base class for physical components that can be assembled."""

    name: str
    mass: float
    position: Vector2
    size: Vector2
    drag_area: float
    inertia_override: float | None = None

    def translate(self, offset: Vector2) -> "Component":
        """Return a copy of the component translated by ``offset``."""

        new_pos = add_vectors(self.position, offset)
        return type(self)(
            name=self.name,
            mass=self.mass,
            position=new_pos,
            size=self.size,
            drag_area=self.drag_area,
            **self._extra_init_kwargs(),
        )

    def _extra_init_kwargs(self) -> dict:
        return {}

    @property
    def inertia(self) -> float:
        if self.inertia_override is not None:
            return self.inertia_override
        width, height = self.size
        return (self.mass * (width ** 2 + height ** 2)) / 12.0


@dataclass
class Engine(Component):
    thrust: float = 0.0
    fuel_consumption: float = 0.0
    gimbal_limit: float = 0.0
    direction: Vector2 = (1.0, 0.0)

    def _extra_init_kwargs(self) -> dict:
        return {
            "thrust": self.thrust,
            "fuel_consumption": self.fuel_consumption,
            "gimbal_limit": self.gimbal_limit,
            "direction": self.direction,
        }


@dataclass
class FuelTank(Component):
    fuel_capacity: float = 0.0
    fuel_level: float = field(default=0.0)

    def _extra_init_kwargs(self) -> dict:
        return {
            "fuel_capacity": self.fuel_capacity,
            "fuel_level": self.fuel_level,
        }


@dataclass
class Wing(Component):
    area: float = 0.0
    lift_curve: float = 5.0
    stall_angle: float = 15.0

    def _extra_init_kwargs(self) -> dict:
        return {
            "area": self.area,
            "lift_curve": self.lift_curve,
            "stall_angle": self.stall_angle,
        }


@dataclass
class HullSection(Component):
    structural_integrity: float = 1.0

    def _extra_init_kwargs(self) -> dict:
        return {"structural_integrity": self.structural_integrity}


@dataclass
class Cockpit(Component):
    crew_capacity: int = 1

    def _extra_init_kwargs(self) -> dict:
        return {"crew_capacity": self.crew_capacity}
