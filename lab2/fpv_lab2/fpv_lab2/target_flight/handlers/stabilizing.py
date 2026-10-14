import math
import time
from typing import TYPE_CHECKING

from ...flight_test.handlers.handler import FlightStateHandler
from ..target_state import TargetState

if TYPE_CHECKING:
    from ..target_flight_node import TargetFlightNode


class StabilizingHandler(FlightStateHandler):
    """Зависання кілька секунд, фіксація стартової точки, обчислення цілі."""

    INTERFACE_TIMEOUT = 15.0

    def handle(self, node: "TargetFlightNode") -> None:
        if node.disarmed_confirmed():
            node.fail("Drone disarmed unexpectedly while stabilizing")
            return

        ready = node.ensure_interfaces()
        elapsed = time.monotonic() - node.phase_started_at

        if not ready:
            if elapsed > node.stabilize_time + self.INTERFACE_TIMEOUT:
                topics = sorted(n for n, _ in node.get_topic_names_and_types() if n.startswith("/ap"))
                node.abort_to_landing(f"cmd_vel topic not found; /ap topics: {topics}")
            return

        if elapsed < node.stabilize_time:
            return

        # чекаємо першу позицію від ArduPilot, щоб узгодити системи координат
        if node.ap_pose_subscription is not None and node.ap_pose is None \
                and elapsed < node.stabilize_time + 5.0:
            return

        x0, y0, _ = node.position()
        node.start_xy = (x0, y0)
        node.target_xy = (x0 - node.delta_x, y0 - node.delta_y)
        node.initial_distance = math.hypot(node.delta_x, node.delta_y)
        node.calibrate_frames()

        node.get_logger().info(f"Start position (x0, y0): ({x0:.3f}, {y0:.3f}) m")
        node.get_logger().info(
            f"Target (x0-{node.delta_x}, y0-{node.delta_y}): "
            f"({node.target_xy[0]:.3f}, {node.target_xy[1]:.3f}) m, "
            f"distance {node.initial_distance:.2f} m"
        )
        node.get_logger().info("Flying to target")
        node.reached_cycles = 0
        node.phase_started_at = time.monotonic()
        node.state = TargetState.FLYING_TO_TARGET
