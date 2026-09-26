# Smart Water Tank & Rain Monitoring System

A real-time, desktop-integrated IoT monitoring system designed to track water storage levels and ambient precipitation conditions. The project combines an **Arduino** hardware unit with a modern **Python CustomTkinter GUI** for real-time visualization, threshold alarms, and automated local data logging.

---

## Key Features

- **Live Data Streaming & Visualization:** Real-time water level plot using `matplotlib` embedded directly into a modern dark-mode `customtkinter` desktop interface.
- **Multithreaded Architecture:** Background serial reading thread prevents UI freezing during continuous JSON stream processing.
- **Physical Edge Feedback:**
  - 16x2 I2C LCD displaying live system status (Rain status, water level tier, overflow risk).
  - Multi-stage LED indicators (Low, Medium, High).
  - Visual strobe alarm when critical water level coincides with active rainfall.
- **Data Persistence & Logging:**
  - Dynamic directory selection via native file dialog.
  - Snapshot logging in JSON format (`live_data.json` / `anlik_veri.json`).
  - Historical timestamped text logs (`historical_logs.txt` / `gecmis_veriler.txt`).

> **Note:** The source code contains detailed Turkish inline comments for educational and step-by-step learning purposes.

---

## Hardware Architecture

| Component | Interface / Pin | Purpose |
| :--- | :--- | :--- |
| **Arduino Uno / Nano** | USB Serial (9600 Baud) | Microcontroller & data acquisition |
| **Water Level Sensor** | Analog Pin `A1` | Continuous depth sensing |
| **Rain Detection Sensor** | Analog Pin `A0` | Surface precipitation measurement |
| **16x2 LCD (I2C: 0x27)** | SDA / SCL (`A4` / `A5`) | Local edge status display |
| **Rain Indicator LED** | Digital Pin `D2` | Active precipitation indicator |
| **Level Indicator LEDs** | Digital Pins `D3`, `D4`, `D5` | Tiered level indicators (Low, Mid, High) |

---

## Software Stack

- **Python 3.x**
  - `customtkinter`: Modern UI dashboard
  - `matplotlib`: Dynamic live plot rendering
  - `pyserial`: Serial communication over USB
- **Arduino C/C++**
  - `Wire.h` & `LiquidCrystal_I2C.h`: I2C display control

---

## Installation & Setup

### 1. Arduino Setup
1. Open the Arduino sketch (`arduino_code.ino`) in the Arduino IDE.
2. Install the **LiquidCrystal_I2C** library via the Library Manager if not already installed.
3. Select your board model and COM port, then click **Upload**.

### 2. Python Setup
1. Clone the repository:
git clone https://github.com/yunusemretemel/smart-water-tank-monitor.git
cd smart-water-tank-monitor

2. Install required Python packages:
pip install pyserial customtkinter matplotlib

3. Update `ARDUINO_PORT` in the Python script to match your connected serial port (e.g., `'COM5'` on Windows or `'/dev/ttyUSB0'` on Linux/macOS).

4. Run the application:
python main.py

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
