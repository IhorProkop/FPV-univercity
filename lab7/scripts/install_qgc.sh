#!/usr/bin/env bash
# Встановлення QGroundControl 5.0.8 (остання версія для Ubuntu 22.04)
set -e                                    # зупинитися на першій помилці
cd ~/fpv_labs/lab7

# modemmanager займає послідовні порти, QGC рекомендує його видалити
sudo apt-get remove -y modemmanager || true

# відео (GStreamer), запуск AppImage (libfuse2) і залежності Qt
sudo apt-get install -y \
  gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl \
  libfuse2 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-cursor-dev

# назва файлу в релізі залежить від версії, пробуємо обидві
URL=https://github.com/mavlink/qgroundcontrol/releases/download/v5.0.8
for NAME in QGroundControl-x86_64.AppImage QGroundControl.AppImage; do
  wget -q --show-progress -O QGroundControl.AppImage "$URL/$NAME" && break
done

chmod +x QGroundControl.AppImage          # дозвіл на запуск
ls -lh QGroundControl.AppImage
