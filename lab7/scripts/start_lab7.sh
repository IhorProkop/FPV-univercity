#!/usr/bin/env bash
# ЛР7: Gazebo (iris_runway) + ArduPilot SITL + MAVProxy + QGroundControl
source ~/fpv_labs/scripts/env.sh
LAB7=~/fpv_labs/lab7
~/fpv_labs/scripts/stop_sim.sh --quiet; pkill -f QGroundControl 2>/dev/null
nohup ros2 launch ardupilot_gz_bringup iris_runway.launch.py rviz:=false > "$LAB7/logs/sim.log" 2>&1 &
echo -n "Чекаю ArduPilot SITL "
for i in $(seq 1 90); do ros2 service list 2>/dev/null | grep -q prearm_check && break; echo -n .; sleep 2; done; echo
pgrep -f mavproxy.py >/dev/null && echo "MAVProxy працює: QGC під'єднається сам (UDP 14550)" \
  || echo "MAVProxy не запущено: у QGC додай Comm Link TCP 127.0.0.1:5762"
nohup "$LAB7/QGroundControl.AppImage" > "$LAB7/logs/qgc.log" 2>&1 &
echo "QGroundControl запущено"
