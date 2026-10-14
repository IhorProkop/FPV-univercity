import time
from typing import TYPE_CHECKING

from ...flight_test.flight_state import FlightState
from ...flight_test.handlers.prearm_check import PrearmCheckHandler

if TYPE_CHECKING:
    from ..target_flight_node import TargetFlightNode


class PrearmRetryHandler(PrearmCheckHandler):
    """Як базовий pre-arm check, але з повтором: одразу після старту SITL
    автопілот ще ініціалізує EKF/GPS і перевірка може не пройти."""

    RETRY_PERIOD = 2.0
    TIMEOUT = 90.0

    def __init__(self):
        self.first_attempt_at = None
        self.next_attempt_at = 0.0

    def handle(self, node: "TargetFlightNode") -> None:
        now = time.monotonic()
        if self.first_attempt_at is None:
            self.first_attempt_at = now
        if node.request_in_progress or now < self.next_attempt_at:
            return
        self.call_prearm_check(node)

    def prearm_callback(self, node: "TargetFlightNode", future) -> None:
        node.request_in_progress = False
        try:
            response = future.result()
        except Exception as error:
            node.fail(f"Pre-arm service failed: {error}")
            return

        if not response.success:
            if time.monotonic() - self.first_attempt_at > self.TIMEOUT:
                node.fail(f"Vehicle is not armable: {response.message}")
                return
            node.get_logger().warn(f"Pre-arm not ready yet: {response.message}; retrying")
            self.next_attempt_at = time.monotonic() + self.RETRY_PERIOD
            return

        pos = node.position()
        if pos is not None:
            node.ground_z = pos[2]
            node.get_logger().info(
                f"Initial position (Gazebo): x={pos[0]:.3f}, y={pos[1]:.3f}, z={pos[2]:.3f}"
            )
        node.get_logger().info(f"Pre-arm check passed: {response.message}")
        node.state = FlightState.SETTING_GUIDED
