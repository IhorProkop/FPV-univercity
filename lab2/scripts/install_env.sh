#!/usr/bin/env bash
# ЛР2 — встановлення середовища: ROS 2 Humble + Gazebo Harmonic + ArduPilot SITL (ardupilot_gz)
# Цільова ОС: Ubuntu 22.04 (WSL2). Запуск БЕЗ sudo:  bash install_env.sh
# Повний журнал: ~/lab2_install.log
set -eo pipefail

LOG="$HOME/lab2_install.log"
exec > >(tee -a "$LOG") 2>&1
step() { echo; echo "===== [$(date +%H:%M:%S)] $* ====="; }
add_line() { grep -qxF "$1" "$HOME/.bashrc" || echo "$1" >> "$HOME/.bashrc"; }

[ "$(lsb_release -rs)" = "22.04" ] || { echo "ПОМИЛКА: потрібна Ubuntu 22.04, а стоїть $(lsb_release -ds)"; exit 1; }
[ "$EUID" -ne 0 ] || { echo "ПОМИЛКА: запускай без sudo"; exit 1; }

# Пароль sudo питаємо один раз і підтримуємо активним до кінця скрипта
sudo -v
( while true; do sudo -n true; sleep 50; kill -0 "$$" 2>/dev/null || exit; done ) 2>/dev/null &

ARDU_WS="$HOME/ardu_ws"
START=$(date +%s)

step "1/9 Базові пакети, локаль, universe"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y locales software-properties-common curl wget git lsb-release gnupg
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
sudo add-apt-repository -y universe

step "2/9 Репозиторій ROS 2"
if ! dpkg -s ros2-apt-source >/dev/null 2>&1; then
  V=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F '"tag_name"' | awk -F\" '{print $4}')
  curl -L -o /tmp/ros2-apt-source.deb \
    "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${V}/ros2-apt-source_${V}.jammy_all.deb"
  sudo dpkg -i /tmp/ros2-apt-source.deb
fi

step "3/9 Репозиторій Gazebo (OSRF)"
sudo wget -q https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable jammy main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

step "4/9 ROS 2 Humble + Gazebo Harmonic + інструменти (довге завантаження)"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ros-humble-desktop ros-dev-tools gz-harmonic default-jre python3-pip rsync

add_line 'source /opt/ros/humble/setup.bash'
add_line 'export GZ_VERSION=harmonic'
export GZ_VERSION=harmonic
source /opt/ros/humble/setup.bash

step "5/9 rosdep (з джерелами Gazebo для пари Humble + Harmonic)"
[ -f /etc/ros/rosdep/sources.list.d/20-default.list ] || sudo rosdep init
sudo wget -q https://raw.githubusercontent.com/osrf/osrf-rosdep/master/gz/00-gazebo.list \
  -O /etc/ros/rosdep/sources.list.d/00-gazebo.list
rosdep update

step "6/9 Вихідний код ArduPilot + ardupilot_gz у $ARDU_WS"
mkdir -p "$ARDU_WS/src"
cd "$ARDU_WS"
vcs import --recursive --skip-existing --input https://raw.githubusercontent.com/ArduPilot/ardupilot/master/Tools/ros2/ros2.repos src
vcs import --recursive --skip-existing --input https://raw.githubusercontent.com/ArduPilot/ardupilot_gz/main/ros2_gz.repos src
sudo apt-get update
rosdep install --from-paths src --ignore-src -r -y

step "7/9 Micro-XRCE-DDS-Gen (генератор коду для DDS)"
cd "$ARDU_WS"
[ -d Micro-XRCE-DDS-Gen ] || git clone --recurse-submodules --branch v4.7.0 https://github.com/ardupilot/Micro-XRCE-DDS-Gen.git
( cd Micro-XRCE-DDS-Gen && ./gradlew assemble )
add_line "export PATH=\$PATH:$ARDU_WS/Micro-XRCE-DDS-Gen/scripts"
export PATH="$PATH:$ARDU_WS/Micro-XRCE-DDS-Gen/scripts"
microxrceddsgen -help > /dev/null && echo "microxrceddsgen OK"

step "8/9 Залежності ArduPilot (install-prereqs)"
cd "$ARDU_WS/src/ardupilot"
Tools/environment_install/install-prereqs-ubuntu.sh -y
set +e; source "$HOME/.profile"; set -e
source /opt/ros/humble/setup.bash

step "9/9 Збірка (colcon) — найдовший етап"
cd "$ARDU_WS"
colcon build --packages-up-to ardupilot_gz_bringup
add_line "source $ARDU_WS/install/setup.bash"

step "ГОТОВО за $(( ($(date +%s) - START) / 60 )) хв"
echo "--- Дані для звіту ---"
lsb_release -ds; uname -m
echo "ROS_DISTRO=$ROS_DISTRO"
gz sim --versions 2>/dev/null | head -n 1 || true
python3 --version
( cd "$ARDU_WS/src/ardupilot" && echo "ArduPilot commit: $(git rev-parse --short HEAD)" )
echo "Журнал: $LOG"
