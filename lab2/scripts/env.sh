#!/usr/bin/env bash
export LAB_WS="${LAB_WS:-$HOME/fpv_labs}"
export ARDU_WS="${ARDU_WS:-$HOME/ardu_ws}"
export LOG_DIR="$LAB_WS/logs"
export GZ_VERSION=harmonic
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
export RCUTILS_COLORIZED_OUTPUT=0
export PATH="$PATH:$HOME/.local/bin:$HOME/venv-ardupilot/bin:$ARDU_WS/src/ardupilot/Tools/autotest"
mkdir -p "$LOG_DIR"
source /opt/ros/humble/setup.bash
source "$ARDU_WS/install/setup.bash"
if [ -f "$LAB_WS/install/setup.bash" ]; then source "$LAB_WS/install/setup.bash"; fi
export SDF_PATH="$ARDU_WS/install/ardupilot_gazebo/share:$ARDU_WS/install/ardupilot_gz_description/share:$ARDU_WS/install/ardupilot_gz_gazebo/share:${GZ_SIM_RESOURCE_PATH}"
true
export GZ_SIM_RESOURCE_PATH="$ARDU_WS/install/ardupilot_gazebo/share:$ARDU_WS/install/ardupilot_gazebo/share/ardupilot_gazebo/models:$ARDU_WS/install/ardupilot_gz_description/share:$ARDU_WS/install/ardupilot_gz_description/share/ardupilot_gz_description/models:${GZ_SIM_RESOURCE_PATH}"
