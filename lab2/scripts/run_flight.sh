#!/usr/bin/env bash
# Запуск вузла польоту з записом журналу у logs/
#   ./run_flight.sh                 політ до цілі (варіант 17)
#   ./run_flight.sh flight_test     початковий приклад викладача
source "$(dirname "$0")/env.sh"
EXE="${1:-fly_to_target}"; shift || true
LOG="$LOG_DIR/${EXE}_$(date +%Y%m%d_%H%M%S).log"
export PYTHONUNBUFFERED=1
ros2 run fpv_lab2 "$EXE" "$@" 2>&1 | tee "$LOG"
echo "Журнал польоту: $LOG"
