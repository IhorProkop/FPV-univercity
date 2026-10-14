#!/usr/bin/env bash
# Запуск симуляції: Gazebo (світ maze) + ArduPilot SITL + DDS-агент + міст ROS–Gazebo.
# Повертає керування, коли автопілот пройшов pre-arm і готовий до польоту.
source "$(dirname "$0")/env.sh"
"$(dirname "$0")/stop_sim.sh" --quiet

nohup ros2 launch ardupilot_gz_bringup iris_maze.launch.py rviz:=false \
  > "$LOG_DIR/sim.log" 2>&1 &
echo "Симуляцію запущено (журнал: $LOG_DIR/sim.log)"

echo -n "Чекаю сервіси ArduPilot "
SRV=""
for _ in $(seq 1 90); do
  SRV=$(ros2 service list 2>/dev/null | grep -m1 'prearm_check' || true)
  [ -n "$SRV" ] && break
  echo -n "."; sleep 2
done
echo
[ -n "$SRV" ] || { echo "ПОМИЛКА: сервіси /ap не з'явились за 3 хв — див. $LOG_DIR/sim.log"; exit 1; }
echo "Сервіси є ($SRV). Чекаю готовність автопілота (pre-arm) "
for _ in $(seq 1 60); do
  if ros2 service call "$SRV" std_srvs/srv/Trigger 2>/dev/null | grep -q 'success=True'; then
    echo "ГОТОВО: можна запускати політ (run_flight.sh)"; exit 0
  fi
  echo -n "."; sleep 2
done
echo; echo "Pre-arm поки не проходить — вузол fly_to_target сам повторюватиме перевірку"
