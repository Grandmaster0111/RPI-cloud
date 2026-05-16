#!/usr/bin/env python3
"""
RPI-cloud sensor data pipeline.
On first run (or if firebase/sec.json is missing) you will be prompted
to provide the path to your Firebase service account key.
"""
import json
import os
import time

import RPi.GPIO as GPIO
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import firebase_admin
from firebase_admin import credentials, firestore


CRED_PATH = os.path.join(os.path.dirname(__file__), "firebase", "sec.json")


def _setup_credentials() -> str:
    """Prompt for the Firebase service account JSON path and save it locally."""
    print("\n" + "=" * 60)
    print("  Firebase credentials not found.")
    print("  Download your service account key from:")
    print("  Firebase Console → Project Settings → Service Accounts")
    print("  → Generate new private key → save the JSON file")
    print("=" * 60)

    while True:
        path = input("\nEnter the full path to your service account JSON file: ").strip()
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            print(f"  File not found: {path}. Please try again.")
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            if "type" not in data or data["type"] != "service_account":
                print("  That doesn\'t look like a service account JSON. Please try again.")
                continue
        except json.JSONDecodeError:
            print("  Could not parse JSON. Please check the file.")
            continue

        # Copy to firebase/sec.json so future runs work automatically
        os.makedirs(os.path.dirname(CRED_PATH), exist_ok=True)
        with open(path) as src, open(CRED_PATH, "w") as dst:
            dst.write(src.read())
        print(f"\n  Credentials saved to {CRED_PATH}")
        print("  (This file is excluded from git via .gitignore)\n")
        return CRED_PATH


def _init_firebase() -> firestore.client:
    """Initialize Firebase, prompting for credentials if needed."""
    cred_path = CRED_PATH if os.path.isfile(CRED_PATH) else _setup_credentials()
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()


# ── Sensor setup ──────────────────────────────────────────────────────
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN    = 4
PIR_PIN    = 17
SPI_PORT   = 0
SPI_DEVICE = 0

mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)


def read_sensors() -> dict:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return {
        "temperature": round(temperature, 2) if temperature else None,
        "humidity":    round(humidity, 2)    if humidity    else None,
        "motion":      bool(GPIO.input(PIR_PIN)),
        "moisture":    mcp.read_adc(0),
        "water_level": mcp.read_adc(1),
        "timestamp":   firestore.SERVER_TIMESTAMP,
    }


def main():
    db = _init_firebase()
    print("RPI-cloud started. Sending sensor data every 10 s. Press Ctrl+C to stop.\n")
    try:
        while True:
            data = read_sensors()
            db.collection("sensor_readings").add(data)
            print("Sent:", data)
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nStopped.")
        GPIO.cleanup()


if __name__ == "__main__":
    main()
