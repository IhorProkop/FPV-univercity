"""Крок 1. Розбір журналу .tlog (MAVLink) у таблицю часових рядів.

Беремо повідомлення від автопілота (system 1, component 1):
  HEARTBEAT           -> режим польоту (custom_mode) і стан arm (біт 128 у base_mode)
  ATTITUDE            -> крен і тангаж
  VFR_HUD             -> повітряна і наземна швидкість, вертикальна швидкість
  GLOBAL_POSITION_INT -> координати, висота над точкою старту, час автопілота
Результат: all.pkl (один рядок на кожне GLOBAL_POSITION_INT).
"""
import math
from pathlib import Path

import pandas as pd
from pymavlink import mavutil

HERE = Path(__file__).resolve().parent            # lab7/analysis
TLOG = HERE.parent / "flight" / "mavproxy_mav.tlog"
ARMED_BIT = 128                                   # MAV_MODE_FLAG_SAFETY_ARMED

log = mavutil.mavlink_connection(str(TLOG))
rows = []
mode = armed = roll = pitch = hud = None

while True:
    msg = log.recv_match()
    if msg is None:                               # кінець файлу
        break
    if msg.get_srcSystem() != 1 or msg.get_srcComponent() != 1:
        continue                                  # пропускаємо пакети від QGC
    kind = msg.get_type()

    if kind == "HEARTBEAT":
        mode = msg.custom_mode                    # 0 STABILIZE, 3 AUTO, 4 GUIDED
        armed = bool(msg.base_mode & ARMED_BIT)
    elif kind == "ATTITUDE":
        roll = math.degrees(msg.roll)
        pitch = math.degrees(msg.pitch)
    elif kind == "VFR_HUD":
        hud = msg
    elif kind == "GLOBAL_POSITION_INT" and hud is not None:
        rows.append({
            "wall": msg._timestamp,               # час запису, годинник ПК
            "boot": msg.time_boot_ms / 1000,      # час автопілота, с
            "lat": msg.lat / 1e7,                 # градуси * 10^7 -> градуси
            "lon": msg.lon / 1e7,
            "alt_rel": msg.relative_alt / 1000,   # мм -> м, над точкою старту
            "alt_amsl": msg.alt / 1000,           # мм -> м, над рівнем моря
            "airspeed": hud.airspeed,             # м/с
            "groundspeed": hud.groundspeed,       # м/с
            "climb": hud.climb,                   # м/с
            "roll": roll,
            "pitch": pitch,
            "mode": mode,
            "armed": armed,
        })

df = pd.DataFrame(rows)
df.to_pickle(HERE / "all.pkl")

flight = df[df["armed"]]
start, end = flight.index[0], flight.index[-1]
sim = df["boot"][end] - df["boot"][start]
real = df["wall"][end] - df["wall"][start]
print(f"arm -> disarm: {sim:.1f} с часу автопілота, {real:.1f} с за годинником ПК")
print(f"RTF = {sim / real:.2f}")
