import math
import time
from typing import TYPE_CHECKING

from ...flight_test.flight_state import FlightState
from ...flight_test.handlers.handler import FlightStateHandler

if TYPE_CHECKING:
    from ..target_flight_node import TargetFlightNode


class HoldingAtTargetHandler(FlightStateHandler):
    """Нульова швидкість кілька секунд, вимір похибки, перехід до посадки."""

    def handle(self, node: "TargetFlightNode") -> None:
        if node.disarmed_confirmed():
            node.fail("Drone disarmed unexpectedly while holding")
            return

        _, _, z = node.position()
        node.send_velocity(0.0, 0.0, node.altitude_correction(z))

        if time.monotonic() - node.phase_started_at < node.hold_time:
            return

        x, y, _ = node.position()
        tx, ty = node.target_xy
        node.actual_xy = (x, y)
        node.position_error = math.hypot(x - tx, y - ty)

        node.get_logger().info(f"Actual position before landing: ({x:.3f}, {y:.3f}) m")
        node.get_logger().info(
            f"Positioning error e = sqrt(({x:.3f}-{tx:.3f})^2 + ({y:.3f}-{ty:.3f})^2) "
            f"= {node.position_error:.3f} m"
        )
        if node.position_error <= node.tolerance:
            node.get_logger().info("TARGET REACHED within tolerance, starting landing")
        else:
            node.get_logger().warn("Error exceeds tolerance, landing anyway")
        node.state = FlightState.LANDING
