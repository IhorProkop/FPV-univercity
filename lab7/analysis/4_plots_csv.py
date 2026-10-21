"""Крок 4. Показники і три графіки за CSV-файлом QGroundControl.

QGC пише CSV у одиницях інтерфейсу: висота у футах, швидкість у милях за годину.
Час у CSV - годинник ПК (реальний час), один запис за секунду.
Результат: csvstats.json, figures/c_alt.png, c_as.png, c_gs.png.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "flight" / "2026-10-20 21-23-33 vehicle1.csv"
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)
FT = 0.3048                                # 1 фут = 0,3048 м
MPH = 0.44704                              # 1 миля/год = 0,44704 м/с

df = pd.read_csv(CSV)
f = pd.DataFrame({
    "time": pd.to_datetime(df["Timestamp"]),
    "alt": df["altitudeRelative"] * FT,
    "airspeed": df["airSpeed"] * MPH,
    "groundspeed": df["groundSpeed"] * MPH,
    "roll": df["roll"],
    "lat": df["gps.lat"],
    "lon": df["gps.lon"],
    "item": df["missionItemIndex"],        # номер поточного пункту місії
    "flight_time": df["flightTime"].astype(str),
})
f["t"] = (f["time"] - f["time"][0]).dt.total_seconds()

# disarm - перший рядок, де лічильник flightTime перестає зростати
i_disarm = f.index[f["flight_time"] == f["flight_time"].iloc[-1]][0]
f = f.loc[:i_disarm + 10]


def first_time(cond):
    return float(f.loc[cond, "t"].iloc[0])


# межі етапів за номером пункту місії: 1 Takeoff, 2 Waypoint, 3 Land
t_auto = first_time((f["item"] == 1) & (f["alt"] > 3.2))
t_wp = first_time(f["item"] == 2)
t_land = first_time(f["item"] == 3)
t_disarm = float(f["t"][i_disarm])

stats = {
    "max_alt_m": f["alt"].max(),
    "max_airspeed": f["airspeed"].max(),
    "max_groundspeed": f["groundspeed"].max(),
    "max_roll_deg": f["roll"].abs().max(),
    "start": [f["lat"].iloc[0], f["lon"].iloc[0]],
    "end": [f["lat"][i_disarm], f["lon"][i_disarm]],
    "cruise_alt_m": f.loc[f["item"] == 2, "alt"].mean(),
    "disarm_row": int(i_disarm),
}
print(json.dumps(stats, indent=1, default=float))
with open(HERE / "csvstats.json", "w") as fh:
    json.dump(stats, fh, indent=1, default=float)

PHASES = [(0, t_auto, "GUIDED:\nзліт до 3 м"), (t_auto, t_wp, "AUTO:\nнабір 45 м"),
          (t_wp, t_land, "AUTO:\nпереліт"), (t_land, t_disarm, "AUTO:\nпосадка")]


def plot(column, ylabel, title, filename, ref, ref_label):
    """Графік величини від часу з підсвіченими етапами місії."""
    fig, ax = plt.subplots(figsize=(8.6, 3.9), dpi=200)
    ymax = f[column].max() * 1.32
    for k, (a, b, label) in enumerate(PHASES):
        ax.axvspan(a, b, color="#f2f2f2" if k % 2 == 0 else "#e6e6e6", lw=0)
        ax.text((a + b) / 2, ymax * 0.97, label, ha="center", va="top", fontsize=8)
    ax.axhline(ref, color="#999", lw=1, ls="--")
    ax.text(f["t"].max(), ref, ref_label, ha="right", va="bottom", fontsize=8)
    ax.plot(f["t"], f[column], color="#1f5fa8", lw=2)
    ax.set_xlim(0, f["t"].max())
    ax.set_ylim(0, ymax)
    ax.set_xlabel("Час від армування за CSV (реальний час), с")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / filename)
    plt.close(fig)


plot("alt", "Висота над точкою старту, м", "Висота польоту (CSV: altitudeRelative)",
     "c_alt.png", 45, "план 45 м")
plot("airspeed", "Повітряна швидкість, м/с", "Повітряна швидкість (CSV: airSpeed)",
     "c_as.png", 4, "WP_SPD = 4 м/с")
plot("groundspeed", "Наземна швидкість, м/с", "Наземна швидкість (CSV: groundSpeed)",
     "c_gs.png", 4, "WP_SPD = 4 м/с")
