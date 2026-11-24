# 🏎️ F1 Speed & Aerodynamics Graphical Monitoring System

A complete, ready-to-run **Formula 1 cars speed and aerodynamics graphical monitoring system**.

It provides a live dashboard that simulates realistic F1 car telemetry and calculates aerodynamic forces (downforce, drag, efficiency) in real time.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Live Telemetry Dashboard**
  - Speed, RPM, Gear, Throttle, Brake, DRS status
  - Real-time gauges and scrolling history charts

- **Aerodynamics Monitoring**
  - Live **Downforce** (kg)
  - Live **Drag Force** (N)
  - **Aero Efficiency** (Lift/Drag ratio)
  - Physics-based calculation using simplified aero equations
  - DRS effect (drag reduction when open)
  - Track-type dependent aero package (High Downforce / Balanced / Low Drag)

- **Multi-car Support**
  - 6 cars with different team characteristics
  - Quick car selector + live speed leaderboard

- **Vehicle Status**
  - Tire temperatures (all four corners)
  - Engine temperature
  - Lateral G-force estimate
  - Fuel remaining

- **Beautiful Dark F1 Theme**
  - Clean, modern, race-inspired UI

---

## Quick Start (Works Completely Offline)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/f1-aero-monitor.git
cd f1-aero-monitor
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The dashboard will automatically open in your browser at:

```
http://localhost:8501
```

That's it — the system is fully working.

---

## Project Structure

```
f1-aero-monitor/
├── app.py              # Main Streamlit dashboard
├── simulator.py        # Telemetry + Aerodynamics simulation engine
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .gitignore
└── LICENSE
```

---

## How the Aerodynamics Work

The simulator uses the classic aerodynamic force equations:

```
Downforce (N) = ½ × ρ × v² × A × CL
Drag (N)      = ½ × ρ × v² × A × CD
```

Where:
- `ρ` = air density (1.225 kg/m³)
- `v` = car speed in m/s
- `A` = frontal area (~1.5 m²)
- `CL` / `CD` = lift & drag coefficients (adjusted by wing level + track type)

**DRS** reduces drag by ~28% when active (high speed + full throttle).

Different track types change the aero multipliers:
- **High Downforce** (Monaco-style): higher CL and CD, lower top speed
- **Low Drag** (Monza-style): lower CL and CD, higher top speed
- **Balanced** (Silverstone-style): middle ground

---

## Requirements

- Python 3.9 or higher
- Internet only needed for the first `pip install` (after that it runs fully offline)

---

## Customization Ideas

- Add more cars in `simulator.py`
- Change history length (`max_history`)
- Adjust aero coefficients
- Add more track types
- Export data to CSV

---

## License

MIT License — free to use, modify, and share.

---

**Not affiliated with Formula 1, FIA, or any team.**  
This is an educational / demonstration project using simulated data.
