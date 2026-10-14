#!/usr/bin/env bash
# Створення ROS 2-пакета fpv_lab2 (як у методичці), копіювання коду та збірка
set -e
source "$(dirname "$0")/env.sh"
mkdir -p "$LAB_WS/src"
cd "$LAB_WS/src"
if [ ! -d fpv_lab2 ]; then
  ros2 pkg create fpv_lab2 \
    --build-type ament_python \
    --license Apache-2.0 \
    --dependencies rclpy std_srvs geometry_msgs nav_msgs ardupilot_msgs
fi
rsync -a "$LAB_WS/pkg_src/fpv_lab2/" "$LAB_WS/src/fpv_lab2/"
cd "$LAB_WS"
colcon build --symlink-install --packages-select fpv_lab2
source "$LAB_WS/install/setup.bash"
echo "--- Виконувані вузли пакета ---"
ros2 pkg executables fpv_lab2
