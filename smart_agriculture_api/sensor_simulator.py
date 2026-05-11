import json
import time
import random
import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883

TOPIC_SENSORS = "agri/sensors"
TOPIC_COMMANDS = "agri/commands"

soil_percent = 55.0

pump_water = False
solenoid = False
pump_fert = False

water_end_time = 0
fert_end_time = 0


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Simulator connected to MQTT broker")
        client.subscribe(TOPIC_COMMANDS)
        print(f"Simulator subscribed to {TOPIC_COMMANDS}")
    else:
        print("MQTT connection failed:", rc)


def on_message(client, userdata, msg):
    global pump_water, solenoid, pump_fert
    global water_end_time, fert_end_time

    try:
        payload = msg.payload.decode("utf-8")
        command = json.loads(payload)

        print("Command received from AI backend:", command)

        duration_sec = int(command.get("duration_sec", 0))
        fert_duration_sec = int(command.get("fert_duration_sec", 0))

        water_cmd = bool(command.get("water_pump", False))
        solenoid_cmd = bool(command.get("solenoid", False))
        fert_cmd = bool(command.get("fert_pump", False))

        if water_cmd and solenoid_cmd and duration_sec > 0:
            pump_water = True
            solenoid = True
            water_end_time = time.time() + duration_sec
            print(f"SIMULATOR: Water pump ON for {duration_sec} seconds")
        else:
            pump_water = False
            solenoid = False

        if fert_cmd and fert_duration_sec > 0:
            pump_fert = True
            fert_end_time = time.time() + fert_duration_sec
            print(f"SIMULATOR: Fertilizer pump ON for {fert_duration_sec} seconds")
        else:
            pump_fert = False

    except Exception as e:
        print("Error reading command:", e)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

print("Sensor simulator started. Publishing fake sensor data...")

while True:
    now = time.time()

    # Auto-stop simulated water pump
    if pump_water and now >= water_end_time:
        pump_water = False
        solenoid = False
        print("SIMULATOR: Water pump OFF")

    # Auto-stop simulated fertilizer pump
    if pump_fert and now >= fert_end_time:
        pump_fert = False
        print("SIMULATOR: Fertilizer pump OFF")

    # Simulate soil behavior
    if pump_water:
        soil_percent += random.uniform(3, 6)   # watering increases moisture
    else:
        soil_percent -= random.uniform(1, 3)   # soil slowly dries

    soil_percent = max(5, min(90, soil_percent))

    payload = {
        "temperature": round(random.uniform(26, 34), 1),
        "humidity": round(random.uniform(55, 80), 1),
        "soil_percent": round(soil_percent, 1),
        "water_low": False,

        "pump_water": pump_water,
        "solenoid": solenoid,
        "pump_fert": pump_fert,

        "days_since_last_fertilization": random.randint(5, 12),
        "days_since_last_watering": random.randint(0, 3),
        "watering_count_24h": random.randint(0, 3),
        "plant_age_days": 30
    }

    client.publish(TOPIC_SENSORS, json.dumps(payload))
    print("Published:", payload)

    time.sleep(5)