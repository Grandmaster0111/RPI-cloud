# RPI-cloud

A Raspberry Pi IoT sensor data pipeline that reads multiple sensors and streams real-time data to **Firebase Firestore**.

## What it does

- Reads **temperature & humidity** from a DHT22 sensor
- Reads **moisture / water level** via an MCP3008 ADC over SPI
- Detects **motion** via a PIR sensor (GPIO)
- Pushes all readings to **Firebase Firestore** in real time
- Accessible from any device via the Firebase console or a companion app

## Hardware Required

| Component | Purpose |
|-----------|---------|
| Raspberry Pi (any model with GPIO) | Main controller |
| DHT22 sensor | Temperature & humidity |
| MCP3008 ADC | Analogue sensor readings (moisture/water) |
| PIR sensor | Motion detection |
| Firebase project | Cloud database |

## Software Prerequisites

```bash
pip install RPi.GPIO Adafruit_DHT Adafruit-GPIO Adafruit-MCP3008 firebase-admin
```

## Setup

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Download your service account key and save as `firebase/sec.json`
3. Connect sensors to the GPIO pins defined in `main.py`
4. Run:

```bash
python3 main.py
```

## Pin Configuration

| Sensor | GPIO Pin |
|--------|---------|
| DHT22  | GPIO 4  |
| PIR    | GPIO 17 |
| MCP3008 | SPI0   |

## Data Structure in Firestore

```json
{
  "temperature": 24.5,
  "humidity": 60.2,
  "moisture": 412,
  "motion": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```
