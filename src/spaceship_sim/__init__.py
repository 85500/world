"""Spaceship construction and simulation prototype."""

from .components import Component, Engine, FuelTank, Wing, HullSection, Cockpit
from .spaceship import Spaceship
from .world import SalvageField

__all__ = [
    "Component",
    "Engine",
    "FuelTank",
    "Wing",
    "HullSection",
    "Cockpit",
    "Spaceship",
    "SalvageField",
]
