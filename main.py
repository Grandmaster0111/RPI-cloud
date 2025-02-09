import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase/sec.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Sensor Setup
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
PIR_PIN = 17

# MCP3008 ADC Setup (for moisture/water level)
SPI_PORT = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

def read_sensors():
    # Read DHT22 (Temperature/Humidity)
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    # Read PIR Sensor (Motion: 1 = motion detected, 0 = no motion)
    motion = GPIO.input(PIR_PIN)
    
    # Read Moisture Sensor (0-1023, higher = drier)
    moisture = mcp.read_adc(0)
    
    # Read Water Level (0-1023, higher = more water)
    water_level = mcp.read_adc(1)
    
    return {
        "temperature": round(temperature, 2) if temperature else None,
        "humidity": round(humidity, 2) if humidity else None,
        "motion": bool(motion),
        "moisture": moisture,
        "water_level": water_level,
        "timestamp": firestore.SERVER_TIMESTAMP
    }

try:
    while True:
        sensor_data = read_sensors()
        
        # Send data to Firebase Firestore
        db.collection("sensor_readings").add(sensor_data)
        print("Data sent:", sensor_data)
        
        time.sleep(10)  # Send data every 10 seconds

except KeyboardInterrupt:
    GPIO.cleanup()
