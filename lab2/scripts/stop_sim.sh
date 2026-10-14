#!/usr/bin/env bash
# Зупинка всіх процесів симуляції (звільняє порти перед повторним запуском)
PATTERNS=("ros2 launch ardupilot_gz_bringup" "gz sim" "arducopter" "micro_ros_agent"
          "mavproxy" "parameter_bridge" "robot_state_publisher" "rviz2" "fpv_lab2")
for p in "${PATTERNS[@]}"; do pkill -INT -f "$p" 2>/dev/null; done
sleep 2
for p in "${PATTERNS[@]}"; do pkill -KILL -f "$p" 2>/dev/null; done
[ "$1" = "--quiet" ] || echo "Симуляцію зупинено"
exit 0
