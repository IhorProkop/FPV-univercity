"""Крок 5. Таблиця Excel: дані CSV, показники формулами, три графіки.

Аркуші: «Показники» (формули MAX, MINIFS, MAXIFS, AVERAGEIF),
«Графіки» (діаграми висоти й швидкостей),
«CSV_QGC» (вихідні дані + перерахунок у м, м/с).
"""
import json
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import Reference, ScatterChart, Series
from openpyxl.styles import Alignment, Font, PatternFill

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "flight" / "2026-10-20 21-23-33 vehicle1.csv"
TLOG_STATS = json.load(open(HERE / "stats.json"))      # час зльоту і польоту з .tlog
CSV_STATS = json.load(open(HERE / "csvstats.json"))
HEAD = Font(bold=True)
GREY = PatternFill("solid", fgColor="E7E6E6")
COLS = ["Timestamp", "flightTime", "missionItemIndex", "altitudeRelative", "airSpeed",
        "groundSpeed", "climbRate", "roll", "pitch", "heading", "gps.lat", "gps.lon",
        "distanceToHome"]

# --- аркуш CSV_QGC: вихідні дані + 4 стовпці з формулами (N..Q) ---
d = pd.read_csv(CSV)[COLS].iloc[:CSV_STATS["disarm_row"] + 11]
d["Timestamp"] = pd.to_datetime(d["Timestamp"])
last = len(d) + 1                                       # номер останнього рядка
dis = CSV_STATS["disarm_row"] + 2                       # рядок disarm у Excel

wb = Workbook()
data = wb.active
data.title = "CSV_QGC"
data.append(COLS + ["t, с", "Висота, м", "Повітряна шв., м/с", "Наземна шв., м/с"])
for r, row in enumerate(d.itertuples(index=False), start=2):
    data.append(list(row) + [
        f"=(A{r}-$A$2)*86400",                          # секунди від першого рядка
        f"=D{r}*0.3048",                                # фути -> метри
        f"=E{r}*0.44704",                               # миль/год -> м/с
        f"=F{r}*0.44704",
    ])
    data[f"A{r}"].number_format = "hh:mm:ss.000"
for cell in data[1]:
    cell.font, cell.fill = HEAD, GREY
    cell.alignment = Alignment(wrap_text=True)
data.freeze_panes = "A2"

# --- аркуш «Показники» ---
rng = lambda col: f"CSV_QGC!{col}2:{col}{last}"         # діапазон стовпця
rows = [
    ("Показник", "Значення", "Пояснення"),
    ("Час армування (початок запису CSV)", "=CSV_QGC!A2", "перший рядок CSV"),
    ("Момент відриву від землі (висота > 0,3 м)",
     f'=_xlfn.MINIFS({rng("A")},{rng("O")},">0.3")', "MINIFS"),
    ("Час торкання землі", f'=_xlfn.MAXIFS({rng("A")},{rng("O")},">0.3")', "MAXIFS"),
    ("Найбільша висота, м", f"=MAX({rng('O')})", "altitudeRelative × 0,3048"),
    ("Найбільша повітряна швидкість, м/с", f"=MAX({rng('P')})", "airSpeed × 0,44704"),
    ("Найбільша наземна швидкість, м/с", f"=MAX({rng('Q')})",
     "groundSpeed × 0,44704"),
    ("Від arm до disarm за годинником ПК, с", f"=(CSV_QGC!A{dis}-CSV_QGC!A2)*86400",
     "рядок, де flightTime перестає зростати"),
    ("Від зльоту до посадки за годинником ПК, с", "=(B4-B3)*86400",
     "реальний час, RTF ≈ 0,2"),
    ("Початкова координата lat", "=CSV_QGC!K2", ""),
    ("Початкова координата lon", "=CSV_QGC!L2", ""),
    ("Кінцева координата lat", f"=CSV_QGC!K{dis}", ""),
    ("Кінцева координата lon", f"=CSV_QGC!L{dis}", ""),
    ("Максимальний |roll|, град.", f"=MAX(MAX({rng('H')}),-MIN({rng('H')}))", ""),
    ("Середня висота на ділянці WP, м", f"=AVERAGEIF({rng('C')},2,{rng('O')})",
     "missionItemIndex = 2"),
    ("Відстань від H після посадки, м", f"=CSV_QGC!M{dis}*0.3048",
     "distanceToHome × 0,3048"),
    ("Час зльоту (час автопілота), с", round(TLOG_STATS["takeoff_time_s"], 1),
     "з .tlog: набір 0,2 → 44,9 м без зависання на 3 м"),
    ("Час польоту (час автопілота), с", round(TLOG_STATS["flight_time_s"], 1),
     "з .tlog: від відриву до торкання"),
    ("Режими польоту", "GUIDED → AUTO", "HEARTBEAT.custom_mode: 4 → 3 (.tlog)"),
    ("Стан arm до / після місії", "DISARMED / DISARMED",
     "HEARTBEAT.base_mode: 81 / 89"),
]
ind = wb.create_sheet("Показники", 0)
for row in rows:
    ind.append(row)
for cell in ind[1]:
    cell.font, cell.fill = HEAD, GREY
for a in ("B2", "B3", "B4"):
    ind[a].number_format = "hh:mm:ss"
for a in ("B5", "B6", "B7", "B8", "B9", "B14", "B15", "B16"):
    ind[a].number_format = "0.00"
for a in ("B10", "B11", "B12", "B13"):
    ind[a].number_format = "0.0000000"
for a in ("B17", "B18"):                                # значення з .tlog - сині
    ind[a].font = Font(color="0000FF")
ind.column_dimensions["A"].width = 42
ind.column_dimensions["B"].width = 26
ind.column_dimensions["C"].width = 44

# --- аркуш «Графіки»: три точкові діаграми з лініями ---
charts = wb.create_sheet("Графіки", 1)
x = Reference(data, min_col=14, min_row=2, max_row=last)          # стовпець N: t
for k, (col, title, unit) in enumerate([(15, "Висота від часу", "Висота, м"),
                                         (16, "Повітряна швидкість від часу", "м/с"),
                                         (17, "Наземна швидкість від часу", "м/с")]):
    ch = ScatterChart()
    ch.title, ch.style, ch.legend = title, 13, None
    ch.x_axis.title, ch.y_axis.title = "Час від армування, с", unit
    ch.x_axis.delete = ch.y_axis.delete = False
    s = Series(Reference(data, min_col=col, min_row=2, max_row=last), x, title=title)
    s.marker.symbol = "none"
    ch.series.append(s)
    ch.width, ch.height = 24, 8.5
    charts.add_chart(ch, f"A{1 + k * 18}")

wb.save(HERE / "Аналіз_телеметрії_ЛР7.xlsx")
print("saved", HERE / "Аналіз_телеметрії_ЛР7.xlsx")
