#!/usr/bin/env bash
# Зупинка QGroundControl і всіх процесів симуляції
pkill -f QGroundControl 2>/dev/null
~/fpv_labs/scripts/stop_sim.sh
