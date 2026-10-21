# ЛР7. Інтеграція телеметрії та протоколу MAVLink (варіант 17)

Прокоп Ігор, ІР-33. Gazebo Sim Harmonic + ArduPilot SITL (ArduCopter 4.8.0-dev) + QGroundControl 5.0.8, Ubuntu 22.04 (WSL2).

Варіант 17: H = 45 м, V = 4 м/с, ціль -35.3630965, 149.1637991 (131,7 м, азимут 278°).
Місія QGC: Takeoff 45 м → Waypoint (ціль) → Land (ціль). Швидкість: `WP_SPD = 4` м/с
(у цій версії ArduPilot параметр `WPNAV_SPEED`, см/с, перейменовано на `WP_SPD`, м/с).

## Структура
| Тека | Вміст |
|---|---|
| `scripts/` | `install_qgc.sh` - встановлення QGC 5.0.8; `start_lab7.sh` - запуск Gazebo + SITL + MAVProxy + QGC; `stop_lab7.sh` - зупинка |
| `flight/` | журнали польоту: CSV-телеметрія QGC і `.tlog` (MAVLink-потік, записаний MAVProxy) |
| `analysis/` | Python-скрипти аналізу, графіки (`figures/`), таблиця `Аналіз_телеметрії_ЛР7.xlsx` |
| `screenshots/` | знімки екрана QGC і Gazebo |

## Запуск (Ubuntu, WSL)
```bash
bash scripts/install_qgc.sh          # один раз
scripts/start_lab7.sh                # Gazebo + ArduPilot SITL + MAVProxy + QGC
scripts/stop_lab7.sh                 # зупинка
```
Скрипти використовують `~/fpv_labs/scripts/env.sh` і `stop_sim.sh` з ЛР2 (`../lab2`).

## Аналіз телеметрії
```bash
pip install pymavlink pandas matplotlib openpyxl
cd analysis
python3 1_parse_tlog.py    # .tlog -> часовий ряд (висота, швидкості, крен, режим, arm)
python3 2_flight_stats.py  # показники за .tlog (час симуляції)
python3 3_plots_tlog.py    # графіки за .tlog
python3 4_plots_csv.py     # показники і 3 графіки за CSV QGC
python3 5_make_xlsx.py     # таблиця Excel з формулами та графіками
```

## Результати
Висота 45,0 м (відхилення до 0,05 м), швидкість 4,0 м/с, посадка в цільовій точці (похибка < 1 см).
Час польоту: 681 с реального часу / 138,8 с часу симуляції (Gazebo у WSL2, RTF ≈ 0,2).
