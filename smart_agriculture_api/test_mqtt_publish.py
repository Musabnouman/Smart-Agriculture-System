import json
import paho.mqtt.client as mqtt

payload = {
    "temperature": 32,
    "humidity": 70,
    "soil_percent": 18,
    "water_low": False,
    "pump_water": False,
    "solenoid": False
}

client = mqtt.Client()
client.connect("127.0.0.1", 1883, 60)
client.publish("agri/sensors", json.dumps(payload))
client.disconnect()

print("Published:", json.dumps(payload))