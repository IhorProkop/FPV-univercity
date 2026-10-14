import time
from typing import TYPE_CHECKING

from ...flight_test.handlers.handler import FlightStateHandler
from ..target_state import TargetState

if TYPE_CHECKING:
    from ..target_flight_node import TargetFlightNode


class ClimbingHandler(FlightStateHandler):
    """Замість фіксованого зависання — чекаємо фактичного набору висоти."""

    def handle(self, node: "TargetFlightNode") -> None:
        if node.disarmed_confirmed():
            node.fail("Drone disarmed unexpectedly during climb")
            return

        node.ensure_interfaces()  # шукаємо топіки заздалегідь, поки дрон набирає висоту

        pos = node.position()
        if pos is None:
            return
        if node.ground_z is None:
            node.ground_z = pos[2]

        height = pos[2] - node.ground_z
        node.log_throttled(f"Climbing: height {height:.2f} / {node.TAKEOFF_ALTITUDE:.1f} m")

        if height >= 0.9 * node.TAKEOFF_ALTITUDE:
            node.get_logger().info(f"Takeoff altitude reached: {height:.2f} m, stabilizing")
            node.phase_started_at = time.monotonic()
            node.state = TargetState.STABILIZING
            return

        if time.monotonic() - node.hover_started_at > node.climb_timeout:
            node.abort_to_landing("takeoff altitude not reached in time")
