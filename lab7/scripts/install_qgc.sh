#!/usr/bin/env bash
set -e
cd ~/fpv_labs/lab7
sudo apt-get remove -y modemmanager || true
sudo apt-get install -y gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl libfuse2 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-cursor-dev
for NAME in QGroundControl-x86_64.AppImage QGroundControl.AppImage; do
  wget -q --show-progress -O QGroundControl.AppImage \
    "https://github.com/mavlink/qgroundcontrol/releases/download/v5.0.8/$NAME" && break
done
chmod +x QGroundControl.AppImage && ls -lh QGroundControl.AppImage
