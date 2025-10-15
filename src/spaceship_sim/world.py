"""Lightweight world representation offering physical salvage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .components import Cockpit, Engine, FuelTank, HullSection, Wing


@dataclass
class SalvageField:
    """Represents a field of reusable components the player can collect."""

    inventory: Dict[str, List] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.inventory:
            self.inventory = {
                "cockpit": [
                    Cockpit("Survey Cockpit", 900.0, (-1.5, 0.0), (2.0, 1.8), drag_area=1.6, crew_capacity=2),
                ],
                "hull": [
                    HullSection("Forward Hull", 500.0, (-1.0, 0.0), (2.5, 1.5), drag_area=1.0, structural_integrity=1.2),
                    HullSection("Aft Hull", 400.0, (1.0, 0.0), (2.5, 1.5), drag_area=1.0, structural_integrity=1.2),
                ],
                "tank": [
                    FuelTank("Primary Tank", 350.0, (0.0, -0.5), (1.8, 1.2), drag_area=0.6, fuel_capacity=400.0, fuel_level=300.0),
                    FuelTank("Aux Tank", 200.0, (0.5, -0.5), (1.5, 1.0), drag_area=0.4, fuel_capacity=150.0, fuel_level=120.0),
                ],
                "engine": [
                    Engine("Twin Thruster", 220.0, (1.8, 0.0), (1.0, 0.8), drag_area=0.5, thrust=32000.0, fuel_consumption=8.0),
                    Engine("Vernier Thruster", 80.0, (0.0, -1.5), (0.5, 0.5), drag_area=0.2, thrust=2000.0, fuel_consumption=1.5, direction=(0.0, 1.0)),
                ],
                "wing": [
                    Wing("Port Wing", 180.0, (-0.5, -2.5), (2.5, 0.3), drag_area=0.4, area=8.5, lift_curve=4.6, stall_angle=14.0),
                    Wing("Starboard Wing", 180.0, (-0.5, 2.5), (2.5, 0.3), drag_area=0.4, area=8.5, lift_curve=4.6, stall_angle=14.0),
                    Wing("Tail Plane", 90.0, (2.2, 0.0), (1.5, 0.2), drag_area=0.2, area=3.0, lift_curve=3.5, stall_angle=12.0),
                ],
            }

    def list_components(self) -> Dict[str, List[str]]:
        return {category: [comp.name for comp in comps] for category, comps in self.inventory.items()}

    def take(self, category: str, name: str):
        options = self.inventory.get(category, [])
        for idx, comp in enumerate(options):
            if comp.name == name:
                return options.pop(idx)
        raise KeyError(f"Component {name!r} not found in category {category!r}")

    def spawn_default_ship(self):
        from .spaceship import Spaceship

        ship = Spaceship()
        ship.attach(self.take("cockpit", "Survey Cockpit"))
        ship.attach(self.take("hull", "Forward Hull"))
        ship.attach(self.take("hull", "Aft Hull"))
        ship.attach(self.take("tank", "Primary Tank"))
        ship.attach(self.take("tank", "Aux Tank"))
        ship.attach(self.take("engine", "Twin Thruster"))
        ship.attach(self.take("engine", "Vernier Thruster"))
        ship.attach(self.take("wing", "Port Wing"))
        ship.attach(self.take("wing", "Starboard Wing"))
        ship.attach(self.take("wing", "Tail Plane"))
        return ship
