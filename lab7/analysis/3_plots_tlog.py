"""Крок 3. Графіки за .tlog у часі автопілота і траєкторія у плані.

Результат: figures/g_alt.png, g_as.png, g_gs.png, g_traj.png.
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                     # малюємо у файл, без вікна
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)
TARGET = (-35.3630965, 149.1637991)

f = pd.read_pickle(HERE / "flight.pkl")
ph = json.load(open(HERE / "stats.json"))["phases_s"]
PHASES = [(0, ph["auto"], "GUIDED:\nзліт до 3 м"),
          (ph["auto"], ph["top"], "AUTO:\nнабір 45 м"),
          (ph["top"], ph["descent"], "AUTO:\nпереліт"),
          (ph["descent"], f["t"].max(), "AUTO:\nпосадка")]


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
    ax.set_ylim(0, ymax)
    ax.set_xlabel("Час автопілота від arm, с")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / filename)
    plt.close(fig)


plot("alt_rel", "Висота, м", "Висота (relative_alt)", "g_alt.png", 45, "план 45 м")
plot("airspeed", "м/с", "Повітряна швидкість", "g_as.png", 4, "WP_SPD = 4 м/с")
plot("groundspeed", "м/с", "Наземна швидкість", "g_gs.png", 4, "WP_SPD = 4 м/с")

# траєкторія у плані: переводимо градуси в метри відносно точки старту
lat0, lon0 = f["lat"].iloc[0], f["lon"].iloc[0]
m_per_deg_lon = 111320 * math.cos(math.radians(lat0))
m_per_deg_lat = 110574
x = (f["lon"] - lon0) * m_per_deg_lon
y = (f["lat"] - lat0) * m_per_deg_lat
tx = (TARGET[1] - lon0) * m_per_deg_lon
ty = (TARGET[0] - lat0) * m_per_deg_lat

fig, ax = plt.subplots(figsize=(8.6, 3.0), dpi=200)
ax.plot(x, y, color="#1f5fa8", lw=2, label="фактична траєкторія")
ax.plot([0, tx], [0, ty], "--", color="#999", lw=1, label="план")
ax.scatter([0], [0], color="#222", zorder=3)
ax.scatter([tx], [ty], marker="x", color="#c0392b", s=80, zorder=3)
ax.set_aspect("equal")
ax.set_xlabel("Схід, м")
ax.set_ylabel("Північ, м")
ax.set_title("Траєкторія у плані (вид згори)", loc="left", fontweight="bold")
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.set_ylim(-10, 40)
fig.tight_layout()
fig.savefig(OUT / "g_traj.png")
