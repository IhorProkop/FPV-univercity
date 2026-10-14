import math
import time
from typing import TYPE_CHECKING

from ...flight_test.handlers.handler import FlightStateHandler
from ..target_state import TargetState

if TYPE_CHECKING:
    from ..target_flight_node import TargetFlightNode


class FlyingToTargetHandler(FlightStateHandler):
    """П-регулятор з насиченням: v = clamp(kp * d, v_min, v_max) у напрямку цілі."""

    REACHED_CYCLES_REQUIRED = 5   # 5 циклів * 0.2 с = 1 с стабільно в зоні допуску
    DIVERGENCE_MARGIN = 2.0       # м: якщо відстань росте — команди йдуть не туди

    def handle(self, node: "TargetFlightNode") -> None:
        if node.disarmed_confirmed():
            node.fail("Drone disarmed unexpectedly during flight to target")
            return

        x, y, z = node.position()
        tx, ty = node.target_xy
        ex, ey = tx - x, ty - y
        distance = math.hypot(ex, ey)
        vz = node.altitude_correction(z)

        if distance <= node.tolerance:
            node.reached_cycles += 1
            node.send_velocity(0.0, 0.0, vz)
            if node.reached_cycles >= self.REACHED_CYCLES_REQUIRED:
                node.get_logger().info(f"Target zone reached: distance {distance:.3f} m, holding")
                node.phase_started_at = time.monotonic()
                node.state = TargetState.HOLDING_AT_TARGET
            return

        node.reached_cycles = 0
        speed = max(node.min_speed, min(node.max_speed, node.kp * distance))
        vx = speed * ex / distance
        vy = speed * ey / distance
        node.send_velocity(vx, vy, vz)

        node.log_throttled(
            f"Position ({x:.2f}, {y:.2f}) | distance {distance:.2f} m | speed {speed:.2f} m/s"
        )

        if distance > node.initial_distance + self.DIVERGENCE_MARGIN:
            node.abort_to_landing("distance to target is growing (frame mismatch?)")
        elif time.monotonic() - node.phase_started_at > node.flight_timeout:
            node.abort_to_landing("flight to target timed out")
