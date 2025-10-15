# Modular Spaceship Prototype

This proof of concept shows how players can assemble spacecraft from salvaged parts and fly them with a lightweight, physics-aware model.

## Features

- Salvage field inventory with pre-authored cockpits, hulls, tanks, engines, and wings.
- `Spaceship` class that computes total mass, center of mass, and inertia directly from attached parts.
- Newtonian forces for thrust, gravity, aerodynamic drag, and simplified wing lift in an Earth-like atmosphere.
- Simple command line demonstration that assembles a default craft and simulates a take-off throttle profile.

## Running the demo

```bash
PYTHONPATH=src python -m spaceship_sim.demo --duration 20 --dt 0.1 --takeoff 5
```

The simulation prints the craft's altitude, airspeed, and pitch angle at each integration step.
