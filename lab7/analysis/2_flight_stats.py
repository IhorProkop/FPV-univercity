"""Крок 2. Показники польоту за .tlog (час автопілота).

Означення (за вимогами викладача):
  час зльоту  - від початку фактичного набору висоти до заданої висоти H,
                без часу простою (зависання на 3 м перед AUTO);
  час польоту - від початку зльоту (відрив) до завершення посадки (торкання).
Результат: stats.json, flight.pkl.
"""
import json
import math
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
H = 45.0                                   # задана висота, м
TARGET = (-35.3630965, 149.1637991)        # цільова точка варіанта 17
MODES = {0: "STABILIZE", 3: "AUTO", 4: "GUIDED"}


def distance_m(lat1, lon1, lat2, lon2):
    """Відстань між двома точками WGS 84 (формула гаверсинуса), м."""
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def first_time(cond):
    """Перший момент часу t, у який виконується умова."""
    return float(f.loc[cond, "t"].iloc[0])


df = pd.read_pickle(HERE / "all.pkl")
armed = df[df["armed"]]
i_arm, i_disarm = armed.index[0], armed.index[-1]

f = df.loc[i_arm:i_disarm].copy()
f["t"] = f["boot"] - df["boot"][i_arm]     # час від arm, с (час автопілота)
f.to_pickle(HERE / "flight.pkl")

# межі етапів за висотою
t_lift = first_time(f["alt_rel"] > 0.2)                       # відрив від землі
t_3m = first_time(f["alt_rel"] > 2.9)                         # GUIDED-зліт на 3 м
t_auto = first_time((f["mode"] == 3) & (f["alt_rel"] > 3.2))  # почався набір в AUTO
t_top = first_time((f["t"] > t_auto) & (f["alt_rel"] > H - 0.1))
t_desc = first_time((f["t"] > t_top + 30) & (f["alt_rel"] < H - 0.1))
t_land = first_time((f["t"] > t_desc) & (f["alt_rel"] < 0.3))

start, end = f.iloc[0], f.iloc[-1]
before = df.loc[i_arm - 1]                 # останній рядок перед arm
after = df.iloc[-1]                        # кінець журналу, після disarm

stats = {
    "takeoff_time_s": (t_3m - t_lift) + (t_top - t_auto),   # без зависання
    "flight_time_s": t_land - t_lift,
    "max_alt_m": f["alt_rel"].max(),
    "max_groundspeed": f["groundspeed"].max(),
    "max_airspeed": f["airspeed"].max(),
    "max_roll_deg": f["roll"].abs().max(),
    "start": [start["lat"], start["lon"]],
    "end": [end["lat"], end["lon"]],
    "landing_error_m": distance_m(end["lat"], end["lon"], *TARGET),
    "modes_in_mission": [MODES.get(m, m) for m in f["mode"].drop_duplicates()],
    "armed_before": bool(before["armed"]),
    "armed_after": bool(after["armed"]),
    "phases_s": {"lift": t_lift, "3m": t_3m, "auto": t_auto, "top": t_top,
                 "descent": t_desc, "touchdown": t_land},
}
print(json.dumps(stats, indent=1, ensure_ascii=False, default=float))
with open(HERE / "stats.json", "w") as fh:
    json.dump(stats, fh, indent=1, ensure_ascii=False, default=float)
