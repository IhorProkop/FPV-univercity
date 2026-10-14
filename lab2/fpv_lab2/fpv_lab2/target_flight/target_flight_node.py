import math
import time

from geometry_msgs.msg import PoseStamped, TwistStamped
from rclpy.qos import qos_profile_sensor_data

from ..flight_test.flight_state import FlightState
from ..flight_test.flight_test_node import FlightTestNode
from ..flight_test.handlers import HANDLERS
from .handlers import TARGET_HANDLERS


def yaw_from_quaternion(q) -> float:
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


class TargetFlightNode(FlightTestNode):
    """Політ до заданої точки: розширення базового вузла без зміни його коду."""

    def __init__(self):
        super().__init__()

        # Варіант 17: x_target = x0 - 7.0, y_target = y0 - 0.8
        self.delta_x = self.declare_parameter("delta_x", 7.0).value
        self.delta_y = self.declare_parameter("delta_y", 0.8).value
        self.tolerance = self.declare_parameter("tolerance", 0.2).value
        self.max_speed = self.declare_parameter("max_speed", 1.0).value
        self.min_speed = self.declare_parameter("min_speed", 0.1).value
        self.kp = self.declare_parameter("kp", 0.6).value
        self.kp_z = self.declare_parameter("kp_z", 0.5).value
        self.stabilize_time = self.declare_parameter("stabilize_time", 3.0).value
        self.hold_time = self.declare_parameter("hold_time", 2.0).value
        self.climb_timeout = self.declare_parameter("climb_timeout", 30.0).value
        self.flight_timeout = self.declare_parameter("flight_timeout", 60.0).value

        # Базові обробники + свої: HOVERING замінено на очікування висоти
        self._handlers = {**HANDLERS, **TARGET_HANDLERS}

        self.ground_z = None
        self.start_xy = None
        self.target_xy = None
        self.actual_xy = None
        self.position_error = None
        self.initial_distance = None
        self.phase_started_at = None
        self.reached_cycles = 0
        self.frame_yaw_offset = 0.0
        self._last_log = 0.0

        self.cmd_vel_topic = None
        self.cmd_vel_publisher = None
        self.ap_pose = None
        self.ap_pose_subscription = None

        self.get_logger().info(
            f"Target mode: dx={self.delta_x:.2f} m, dy={self.delta_y:.2f} m, "
            f"tolerance={self.tolerance:.2f} m"
        )

    # ---------- допоміжні методи ----------

    def position(self):
        if self.odometry is None:
            return None
        p = self.odometry.pose.pose.position
        return p.x, p.y, p.z

    def gazebo_yaw(self):
        return yaw_from_quaternion(self.odometry.pose.pose.orientation)

    def find_ap_topic(self, suffix):
        for name, _types in self.get_topic_names_and_types():
            if name.startswith("/ap") and name.endswith(suffix):
                return name
        return None

    def ensure_interfaces(self) -> bool:
        """Знаходить топік команд швидкості й топік позиції ArduPilot."""
        if self.cmd_vel_publisher is None:
            self.cmd_vel_topic = self.find_ap_topic("cmd_vel")
            if self.cmd_vel_topic is not None:
                self.cmd_vel_publisher = self.create_publisher(
                    TwistStamped, self.cmd_vel_topic, 10
                )
                self.get_logger().info(f"Velocity commands -> {self.cmd_vel_topic}")

        if self.ap_pose_subscription is None:
            pose_topic = self.find_ap_topic("/pose/filtered")
            if pose_topic is not None:
                self.ap_pose_subscription = self.create_subscription(
                    PoseStamped, pose_topic, self._ap_pose_callback, qos_profile_sensor_data
                )
                self.get_logger().info(f"ArduPilot pose <- {pose_topic}")

        return self.cmd_vel_publisher is not None

    def _ap_pose_callback(self, message):
        self.ap_pose = message

    def calibrate_frames(self):
        """Кут між системою Gazebo (/odometry) і системою ArduPilot (map, ENU).

        Обидві системи бачать один і той самий курс дрона, тому різниця
        курсів = поворот між системами координат. Якщо системи збігаються, кут ~0.
        """
        if self.ap_pose is None:
            self.get_logger().warn("No ArduPilot pose received, assuming frames are aligned")
            self.frame_yaw_offset = 0.0
            return
        ap_yaw = yaw_from_quaternion(self.ap_pose.pose.orientation)
        offset = self.gazebo_yaw() - ap_yaw
        self.frame_yaw_offset = math.atan2(math.sin(offset), math.cos(offset))
        self.get_logger().info(
            f"Frame alignment: Gazebo vs ArduPilot yaw offset = "
            f"{math.degrees(self.frame_yaw_offset):.1f} deg"
        )

    def send_velocity(self, vx_world, vy_world, vz=0.0):
        """Швидкість у системі Gazebo -> TwistStamped у системі map (ENU) ArduPilot."""
        if self.cmd_vel_publisher is None:
            return
        c = math.cos(-self.frame_yaw_offset)
        s = math.sin(-self.frame_yaw_offset)
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.twist.linear.x = c * vx_world - s * vy_world
        msg.twist.linear.y = s * vx_world + c * vy_world
        msg.twist.linear.z = vz
        self.cmd_vel_publisher.publish(msg)

    def stop_motion(self):
        self.send_velocity(0.0, 0.0, 0.0)

    def altitude_correction(self, z):
        if self.ground_z is None:
            return 0.0
        error = (self.ground_z + self.TAKEOFF_ALTITUDE) - z
        return max(-0.3, min(0.3, self.kp_z * error))

    def log_throttled(self, message, period=1.0):
        now = time.monotonic()
        if now - self._last_log >= period:
            self._last_log = now
            self.get_logger().info(message)

    def abort_to_landing(self, reason):
        """Аварійне завершення в повітрі: зупинитися й сісти, а не зависнути."""
        self.get_logger().error(f"ABORT: {reason}")
        self.stop_motion()
        if self.status is not None and self.status.armed:
            self.state = FlightState.LANDING
        else:
            self.state = FlightState.ERROR

    def print_summary(self):
        log = self.get_logger()
        log.info("========== FLIGHT SUMMARY ==========")
        log.info(f"Final state: {self.state.name}")
        if self.start_xy:
            log.info(f"Start position   (x0, y0): ({self.start_xy[0]:.3f}, {self.start_xy[1]:.3f}) m")
        if self.target_xy:
            log.info(f"Target position  (xt, yt): ({self.target_xy[0]:.3f}, {self.target_xy[1]:.3f}) m")
        if self.actual_xy:
            log.info(f"Actual before landing    : ({self.actual_xy[0]:.3f}, {self.actual_xy[1]:.3f}) m")
            log.info(f"Positioning error e      : {self.position_error:.3f} m")
        pos = self.position()
        if pos:
            log.info(f"Position after landing   : ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}) m")
        log.info("====================================")

    def disarmed_confirmed(self, grace=2.0):
        """Статус приходить із затримкою: відмова лише якщо disarmed триває довше grace с."""
        armed = self.status is not None and self.status.armed
        now = time.monotonic()
        if armed:
            self._disarmed_since = None
            return False
        if getattr(self, "_disarmed_since", None) is None:
            self._disarmed_since = now
        return now - self._disarmed_since > grace
