#!/usr/bin/env python3
import rclpy

from ..flight_test.flight_state import FlightState
from .target_flight_node import TargetFlightNode


def main(args=None):
    rclpy.init(args=args)
    node = TargetFlightNode()

    try:
        while (
            rclpy.ok()
            and node.state != FlightState.FINISHED
            and node.state != FlightState.ERROR
        ):
            rclpy.spin_once(node, timeout_sec=0.2)
    except KeyboardInterrupt:
        node.get_logger().warn("Interrupted by user")
    finally:
        node.print_summary()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
