# ЛР2 — Gazebo + ArduPilot SITL + ROS 2: політ до точки (варіант 17)

Ціль: `x_t = x0 − 7.0`, `y_t = y0 − 0.8`, допуск 0.2 м.

## Структура
```
lab2/
├── scripts/
│   ├── install_env.sh    # одноразове встановлення ROS 2 Humble + Gazebo Harmonic + ArduPilot
│   ├── env.sh            # спільні шляхи + source середовищ
│   ├── build_package.sh  # ros2 pkg create + копіювання коду + colcon build
│   ├── start_sim.sh      # запуск Gazebo (maze) + SITL + DDS-агент, очікування готовності
│   ├── run_flight.sh     # запуск вузла з журналом у logs/
│   └── stop_sim.sh       # зупинка всіх процесів симуляції
├── fpv_lab2/             # ROS 2 пакет (ament_python)
│   ├── package.xml, setup.py, setup.cfg, resource/
│   └── fpv_lab2/
│       ├── flight_test/      # початковий приклад викладача (без змін)
│       └── target_flight/    # власний модуль: політ до точки
├── logs/                 # журнали запусків
├── screenshots/          # скріншоти Gazebo для звіту
└── README.md
```
Робота виконується у WSL (Ubuntu 22.04); у домашній теці WSL проєкт лежить як `~/fpv_labs`, тому в командах нижче шляхи `~/fpv_labs/...`.

## Порядок
```bash
bash ~/fpv_labs/scripts/build_package.sh       # один раз
~/fpv_labs/scripts/start_sim.sh                # термінал 1
~/fpv_labs/scripts/run_flight.sh flight_test   # приклад викладача
~/fpv_labs/scripts/stop_sim.sh && ~/fpv_labs/scripts/start_sim.sh
~/fpv_labs/scripts/run_flight.sh               # політ до цілі
~/fpv_labs/scripts/stop_sim.sh
```

Параметри можна змінити без правки коду:
`./run_flight.sh fly_to_target --ros-args -p max_speed:=0.8 -p tolerance:=0.25`

## Результат

Варіант 17: Δx = 7,0 м, Δy = 0,8 м, допуск 0,2 м.

| Параметр | Значення |
|---|---|
| Старт (x0, y0) | (0,001; 0,001) м |
| Ціль (xt, yt) | (7,001; 0,801) м |
| Фактична точка перед посадкою | (6,949; 0,790) м |
| Похибка позиціювання e | **0,053 м** (у межах допуску) |

За формулою методички `x_t = x0 − Δx` ціль (−6,999; −0,799) лежить за стіною Wall_9 (x = −1 м) у світі `maze.sdf` — політ у цю точку завершується зіткненням (журнал `logs/fly_to_target_20261014_171312.log`). Тому політ виконано у дзеркальну точку `(x0 + Δx; y0 + Δy)` через параметри запуску `delta_x:=-7.0 delta_y:=-0.8`. Фінальний журнал: `logs/fly_to_target_20261014_180536.log` (FLIGHT SUMMARY, Final state: FINISHED).
