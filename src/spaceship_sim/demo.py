"""Command line proof of concept for assembling and flying a spaceship."""

from __future__ import annotations

import argparse
import math
from typing import Iterable

from .physics import length
from .spaceship import Spaceship
from .world import SalvageField


def run_simulation(ship: Spaceship, duration: float, dt: float, throttle_profile: Iterable[float]):
    timeline = []
    time = 0.0
    for throttle in throttle_profile:
        ship.simulate_step(throttle, dt)
        time += dt
        timeline.append(
            {
                "time": time,
                "position": ship.position,
                "velocity": ship.velocity,
                "speed": length(ship.velocity),
                "altitude": ship.position[1],
                "orientation": math.degrees(ship.orientation),
            }
        )
        if time >= duration:
            break
    return timeline


def make_profile(duration: float, dt: float, takeoff_time: float) -> Iterable[float]:
    steps = int(duration / dt)
    for step in range(steps):
        t = step * dt
        if t < takeoff_time:
            yield 0.4
        elif t < takeoff_time + 2.0:
            yield 0.7
        else:
            yield 1.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", type=float, default=20.0, help="Seconds to simulate")
    parser.add_argument("--dt", type=float, default=0.1, help="Integration step size")
    parser.add_argument("--takeoff", type=float, default=5.0, help="Seconds before full throttle")
    args = parser.parse_args()

    salvage = SalvageField()
    ship = salvage.spawn_default_ship()
    print(ship.summary())
    print("\nSimulating...")
    profile = make_profile(args.duration, args.dt, args.takeoff)
    timeline = run_simulation(ship, args.duration, args.dt, profile)
    for entry in timeline:
        print(
            f"t={entry['time']:4.1f}s | alt={entry['altitude']:6.1f} m | speed={entry['speed']:6.1f} m/s | "
            f"pitch={entry['orientation']:6.1f}°",
        )


if __name__ == "__main__":  # pragma: no cover - manual testing utility
    main()
