import network
import urequests
import dht
from time import sleep
from machine import Pin
import json

SSID = "Cihuy"
PASSWORD = "bawadebwak"

UBIDOTS_TOKEN = "BBUS-GhlChYF9mrfQ9jkPxg38jfY2W0HGCw"
DEVICE_LABEL = "esp32_sensor"
TEMP_LABEL = "temperature"
HUMID_LABEL = "humidity"
MOTION_LABEL = "motion"

SERVER_IP = "192.168.188.120"
SERVER_PORT = "5000"
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}/sensor"

DHT_PIN = Pin(15)
PIR_PIN = Pin(18, Pin.IN)
dht_sensor = dht.DHT11(DHT_PIN)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())

def send_to_ubidots(temp, humid, motion):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}
    payload = {TEMP_LABEL: temp, HUMID_LABEL: humid, MOTION_LABEL: motion}
    try:
        response = urequests.post(url, json=payload, headers=headers)
        print("Ubidots Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data to Ubidots:", e)

def send_to_server(temp, humid, motion):
    headers = {"Content-Type": "application/json"}
    payload = {"temperature": temp, "humidity": humid, "motion": motion}
    try:
        response = urequests.post(SERVER_URL, json=payload, headers=headers)
        print("Server Response:", response.status_code, response.text)
        response.close()
    except Exception as e:
        print("Failed to send data to server:", e)

def read_dht():
    for _ in range(3):
        try:
            dht_sensor.measure()
            return dht_sensor.temperature(), dht_sensor.humidity()
        except OSError as e:
            print("Retrying sensor read...")
            sleep(2)
    return None, None

connect_wifi()
last_motion_state = 0

while True:
    temp, humid = read_dht()
    motion = PIR_PIN.value()
    if temp is not None and humid is not None:
        print(f"Temperature: {temp}°C, Humidity: {humid}%, Motion: {motion}")
        if motion != last_motion_state:
            send_to_ubidots(temp, humid, motion)
            send_to_server(temp, humid, motion)
            last_motion_state = motion
    else:
        print("Sensor gagal membaca data! Pastikan sensor tersambung dengan benar.")
    sleep(3)