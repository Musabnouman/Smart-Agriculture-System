import base64
import os
import io
import joblib
import numpy as np
import requests
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, BatchNormalization, Dropout
from tensorflow.keras.models import Model
from dotenv import load_dotenv
from datetime import datetime
import json
import time
import paho.mqtt.client as mqtt

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Force CPU to avoid GPU errors
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# Load Models
irrigation_model, scaler = joblib.load("models/irrigation_model.pkl")
fertilization_model = joblib.load("models/fertilization_model.pkl")
fertilization_scaler = joblib.load("models/fertilization_scaler.pkl")

base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
x = Dense(512, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.2)(x)
prediction = Dense(15, activation='softmax')(x)
plant_model = Model(inputs=base_model.input, outputs=prediction)
plant_model.load_weights("models/plant_disease_model.h5")

# Weather API Key 
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Image Preprocessing
def preprocess_image(img):
    img = img.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalize
    return img_array

latest_sensor_data = {
    "temperature": None,
    "humidity": None,
    "soil_percent": None,
    "water_low": None,
    "pump_water": False,
    "solenoid": False,
    "pump_fert": False,
    "last_update": None
}

latest_ai_decision = {
    "irrigation_required": False,
    "watering_duration": 0,
    "reason": "No prediction yet",
    "last_prediction_time": None
}
latest_fertilization_decision = {
    "fertilization_required": False,
    "fertilizer_duration": 0,
    "fertilizer_reason": "No fertilization prediction yet",
    "raw_fertilizer_model_output": None,
    "last_fertilization_prediction_time": None,
    "last_fertilization_time": None
}


MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883

TOPIC_SENSORS = "agri/sensors"
TOPIC_COMMANDS = "agri/commands"

AUTO_CONTROL_ENABLED = True
last_watering_timestamp = 0
MIN_SECONDS_BETWEEN_WATERING = 60

last_fertilization_timestamp = 0
MIN_SECONDS_BETWEEN_FERTILIZATION = 60

mqtt_client = mqtt.Client()





class_names = [
    "Pepper Bell - Bacterial Spot",
    "Pepper Bell - Healthy",
    "Potato - Early Blight",
    "Potato - Late Blight",
    "Potato - Healthy",
    "Tomato - Bacterial Spot",
    "Tomato - Early Blight",
    "Tomato - Late Blight",
    "Tomato - Leaf Mold",
    "Tomato - Septoria Leaf Spot",
    "Tomato - Spider Mites (Two-Spotted Spider Mite)",
    "Tomato - Target Spot",
    "Tomato - Yellow Leaf Curl Virus",
    "Tomato - Mosaic Virus",
    "Tomato - Healthy"
]

causes = {
    "Pepper Bell - Bacterial Spot": "Xanthomonas campestris bacteria",
    "Potato - Early Blight": "Alternaria solani fungus",
    "Potato - Late Blight": "Phytophthora infestans pathogen",
    "Tomato - Bacterial Spot": "Xanthomonas campestris bacteria",
    "Tomato - Early Blight": "Alternaria solani fungus",
    "Tomato - Late Blight": "Phytophthora infestans pathogen",
    "Tomato - Leaf Mold": "Passalora fulva fungus",
    "Tomato - Septoria Leaf Spot": "Septoria lycopersici fungus",
    "Tomato - Spider Mites (Two-Spotted Spider Mite)": "Tetranychus urticae mites",
    "Tomato - Target Spot": "Corynespora cassiicola fungus",
    "Tomato - Yellow Leaf Curl Virus": "Tomato yellow leaf curl virus (spread by whiteflies)",
    "Tomato - Mosaic Virus": "Tobacco mosaic virus (TMV)",
}

symptoms = {
    "Pepper Bell - Bacterial Spot": "Small, dark, water-soaked spots on leaves and fruit; can lead to defoliation and reduced yield.",
    "Potato - Early Blight": "Brown lesions with concentric rings on lower leaves, leading to defoliation.",
    "Potato - Late Blight": "Dark, water-soaked lesions on leaves and stems; rapid plant death in humid conditions.",
    "Tomato - Bacterial Spot": "Dark, water-soaked leaf spots that merge and cause yellowing; fruit may have scabby spots.",
    "Tomato - Early Blight": "Dark spots with concentric rings on lower leaves; can cause plant defoliation.",
    "Tomato - Late Blight": "Large, water-soaked lesions on leaves and stems, leading to rapid plant collapse.",
    "Tomato - Leaf Mold": "Yellow patches on upper leaves, fuzzy olive-green mold underneath.",
    "Tomato - Septoria Leaf Spot": "Numerous small, circular spots with dark margins on leaves; causes defoliation.",
    "Tomato - Spider Mites (Two-Spotted Spider Mite)": "Yellow speckling on leaves, fine webbing, leaf curling, and drying.",
    "Tomato - Target Spot": "Circular brown spots with concentric rings, leading to premature leaf drop.",
    "Tomato - Yellow Leaf Curl Virus": "Upward curling, yellowing of leaves, and stunted growth.",
    "Tomato - Mosaic Virus": "Mottled yellow and green leaf pattern, distorted leaf growth, and reduced fruit production.",
}


treatments = {
    "Pepper Bell - Bacterial Spot": "Apply copper-based fungicides. Avoid overhead watering. Use disease-resistant varieties.",
    "Pepper Bell - Healthy": "No treatment needed. Maintain proper watering and nutrient balance.",
    "Potato - Early Blight": "Use fungicides containing chlorothalonil or mancozeb. Rotate crops and remove infected plants.",
    "Potato - Late Blight": "Apply fungicides like metalaxyl or chlorothalonil. Improve air circulation and avoid wet conditions.",
    "Potato - Healthy": "No treatment needed. Maintain soil health and proper irrigation.",
    "Tomato - Bacterial Spot": "Use copper sprays and bactericides. Avoid handling plants when wet.",
    "Tomato - Early Blight": "Apply fungicides such as chlorothalonil or mancozeb. Prune lower leaves and use mulch to prevent soil splash.",
    "Tomato - Late Blight": "Use fungicides like copper-based sprays or chlorothalonil. Remove and destroy infected plants.",
    "Tomato - Leaf Mold": "Increase air circulation, reduce humidity, and apply fungicides containing chlorothalonil or mancozeb.",
    "Tomato - Septoria Leaf Spot": "Use fungicides like copper-based sprays. Remove infected leaves and ensure good airflow.",
    "Tomato - Spider Mites (Two-Spotted Spider Mite)": "Use insecticidal soap, neem oil, or predatory mites to control infestations.",
    "Tomato - Target Spot": "Apply fungicides such as azoxystrobin or chlorothalonil. Remove infected leaves and avoid overhead watering.",
    "Tomato - Yellow Leaf Curl Virus": "Control whiteflies with neem oil or insecticidal soap. Use virus-resistant tomato varieties.",
    "Tomato - Mosaic Virus": "Remove infected plants immediately. Control aphids that spread the virus using neem oil or insecticidal soap.",
    "Tomato - Healthy": "No treatment needed. Maintain good growing conditions."
}

def make_irrigation_decision(data):
    temperature = float(data.get("temperature"))
    humidity = float(data.get("humidity", 0))
    soil_percent = float(data.get("soil_percent", data.get("soil_moisture")))
    water_low = parse_bool(data.get("water_low", False))

    latest_sensor_data["temperature"] = temperature
    latest_sensor_data["humidity"] = humidity
    latest_sensor_data["soil_percent"] = soil_percent
    latest_sensor_data["water_low"] = water_low
    latest_sensor_data["pump_water"] = parse_bool(data.get("pump_water", False))
    latest_sensor_data["solenoid"] = parse_bool(data.get("solenoid", False))
    latest_sensor_data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_sensor_data["pump_fert"] = parse_bool(data.get("pump_fert", False))

    if water_low:
        result = {
            "irrigation_required": False,
            "watering_duration": 0,
            "reason": "Water tank is low. Irrigation is blocked for pump safety.",
            "raw_model_output": None,
            "command_sent_to_esp32": False
        }
        latest_ai_decision.update(result)
        latest_ai_decision["last_prediction_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return result

    pressure = float(data.get("pressure", 1013.25))
    altitude = float(data.get("altitude", 0))

    X = np.array([[temperature, pressure, altitude, soil_percent]])
    X_scaled = scaler.transform(X)

    raw_prediction = int(irrigation_model.predict(X_scaled)[0])

    # Model suggestion from GitHub model
    model_suggests_irrigation = raw_prediction in [0, 1]

    # Safety correction for our prototype
    # Do not irrigate if soil moisture is already enough
    if soil_percent >= 45:
        irrigation_required = False
    elif soil_percent <= 35 and model_suggests_irrigation:
        irrigation_required = True
    elif soil_percent <= 25:
        irrigation_required = True
    else:
        irrigation_required = False

    if irrigation_required:
        if soil_percent < 20:
            watering_duration = 15
        elif soil_percent < 35:
            watering_duration = 10
        else:
            watering_duration = 5
    else:
        watering_duration = 0

    if irrigation_required:
        if soil_percent < 20:
            reason = "AI predicts irrigation is required because soil moisture is very low."
        elif temperature > 35:
            reason = "AI predicts irrigation is required because temperature is high and soil moisture is low."
        else:
            reason = "AI predicts irrigation is required based on current soil and environmental conditions."
    else:
        reason = "AI predicts irrigation is not required under current conditions."

    result = {
        "irrigation_required": irrigation_required,
        "watering_duration": watering_duration,
        "reason": reason,
        "raw_model_output": raw_prediction,
        "command_sent_to_esp32": False
    }

    latest_ai_decision.update(result)
    latest_ai_decision["last_prediction_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return result

def send_command_to_esp32(irrigation_decision, fertilization_decision):
    payload = {
        "water_pump": bool(irrigation_decision["irrigation_required"]),
        "solenoid": bool(irrigation_decision["irrigation_required"]),
        "duration_sec": int(irrigation_decision["watering_duration"]),

        "fert_pump": bool(fertilization_decision["fertilization_required"]),
        "fert_duration_sec": int(fertilization_decision["fertilizer_duration"]),

        "source": "ai_models",
        "irrigation_reason": irrigation_decision["reason"],
        "fertilizer_reason": fertilization_decision["fertilizer_reason"]
    }

    mqtt_client.publish(TOPIC_COMMANDS, json.dumps(payload))
    print("AI command sent to ESP32:", payload)
    return True


def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Flask backend connected to MQTT broker")
        client.subscribe(TOPIC_SENSORS)
        print(f"Subscribed to topic: {TOPIC_SENSORS}")
    else:
        print("MQTT connection failed with code:", rc)


def on_mqtt_message(client, userdata, msg):
    global last_watering_timestamp, last_fertilization_timestamp

    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        print("Sensor data received:", data)

        decision = make_irrigation_decision(data)
        fert_decision = make_fertilization_decision(data)

        now = time.time()

        can_water_now = (now - last_watering_timestamp) >= MIN_SECONDS_BETWEEN_WATERING
        can_fertilize_now = (now - last_fertilization_timestamp) >= MIN_SECONDS_BETWEEN_FERTILIZATION

        irrigation_allowed = (
            decision["irrigation_required"]
            and decision["watering_duration"] > 0
            and can_water_now
        )

        fertilization_allowed = (
            fert_decision["fertilization_required"]
            and fert_decision["fertilizer_duration"] > 0
            and can_fertilize_now
        )

        # Block irrigation during cooldown
        if decision["irrigation_required"] and not can_water_now:
            decision_for_command = decision.copy()
            decision_for_command["irrigation_required"] = False
            decision_for_command["watering_duration"] = 0
            latest_ai_decision["reason"] = (
                decision["reason"] + " Waiting because minimum watering interval has not passed."
            )
        else:
            decision_for_command = decision

        # Block fertilization during cooldown
        if fert_decision["fertilization_required"] and not can_fertilize_now:
            fert_decision_for_command = fert_decision.copy()
            fert_decision_for_command["fertilization_required"] = False
            fert_decision_for_command["fertilizer_duration"] = 0
            latest_fertilization_decision["fertilizer_reason"] = (
                fert_decision["fertilizer_reason"]
                + " Waiting because minimum fertilization interval has not passed."
            )
        else:
            fert_decision_for_command = fert_decision

        if AUTO_CONTROL_ENABLED and (irrigation_allowed or fertilization_allowed):
            command_sent = send_command_to_esp32(
                decision_for_command,
                fert_decision_for_command
            )

            latest_ai_decision["command_sent_to_esp32"] = command_sent

            if irrigation_allowed:
                last_watering_timestamp = now
                latest_ai_decision["last_watering_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if fertilization_allowed:
                last_fertilization_timestamp = now
                latest_fertilization_decision["last_fertilization_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            latest_ai_decision["command_sent_to_esp32"] = False

    except Exception as e:
        print("Error processing MQTT message:", e)


def start_mqtt_listener():
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    print("MQTT listener started")
    

def make_fertilization_decision(data):
    temperature = float(data.get("temperature", 0))
    humidity = float(data.get("humidity", 0))
    soil_percent = float(data.get("soil_percent", 0))
    water_low = 1 if parse_bool(data.get("water_low", False)) else 0

    # These are backend/simulator fields until real tracking is added
    days_since_last_fertilization = float(data.get("days_since_last_fertilization", 7))
    days_since_last_watering = float(data.get("days_since_last_watering", 1))
    watering_count_24h = float(data.get("watering_count_24h", 1))
    plant_age_days = float(data.get("plant_age_days", 30))

    X = np.array([[
        temperature,
        humidity,
        soil_percent,
        water_low,
        days_since_last_fertilization,
        days_since_last_watering,
        watering_count_24h,
        plant_age_days
    ]])

    X_scaled = fertilization_scaler.transform(X)
    prediction = int(fertilization_model.predict(X_scaled)[0])

    fertilization_required = prediction == 1

    if fertilization_required:
        fertilizer_duration = 5
        fertilizer_reason = (
            "AI predicts fertilization is required because fertilization is due "
            "and current environmental conditions are suitable."
        )
    else:
        fertilizer_duration = 0
        fertilizer_reason = "AI predicts fertilization is not required under current conditions."

    if water_low == 1:
        fertilization_required = False
        fertilizer_duration = 0
        fertilizer_reason = "Fertilization blocked because tank level is low."

    result = {
        "fertilization_required": fertilization_required,
        "fertilizer_duration": fertilizer_duration,
        "fertilizer_reason": fertilizer_reason,
        "raw_fertilizer_model_output": prediction,
        "last_fertilization_prediction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    latest_fertilization_decision.update(result)
    return result

# API Routes 
@app.route("/check_weather", methods=["GET"])
def check_weather():
    location = request.args.get("location", "default_location")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        rain_forecast = "rain" in weather_data["weather"][0]["description"].lower()
        altitude = weather_data["coord"]["lat"] * 0.1
        return jsonify({
            "rain_expected": rain_forecast,
            "temperature": weather_data["main"]["temp"],
            "pressure": weather_data["main"]["pressure"],
            "altitude": altitude
        })
    return jsonify({"error": "Could not fetch weather data"}), 400

def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ["true", "1", "yes", "on"]
    return bool(value)

@app.route("/predict/irrigation", methods=["POST"])
def predict_irrigation():
    try:
        data = request.json
        result = make_irrigation_decision(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/predict/plant", methods=["POST"])
def predict_plant_disease():
    try:
        if "image" in request.files:
            file = request.files["image"]
            img = Image.open(file).convert("RGB")
        elif "image" in request.json:
            image_data = request.json["image"].split(",")[1]  
            img = Image.open(io.BytesIO(base64.b64decode(image_data))).convert("RGB")
        else:
            return jsonify({"error": "No image provided"}), 400

        img_array = preprocess_image(img)
        prediction = plant_model.predict(img_array)
        predicted_class_idx = np.argmax(prediction, axis=1)[0]
        confidence = float(np.max(prediction)) * 100
        predicted_class = class_names[predicted_class_idx]
        if predicted_class == "Pepper Bell - Healthy" or predicted_class == "Tomato - Healthy" or predicted_class == "Potato - Healthy": 
            return jsonify({"healthy": "Plant is healthy", "confidence": confidence})
        cause = causes.get(predicted_class, "Cause details not available")
        symptom = symptoms.get(predicted_class, "Symptom details not available")
        treatment = treatments.get(predicted_class, "No treatment details available")


        return jsonify({
            "disease": predicted_class,
            "confidence": confidence,
            "cause": cause,
            "symptoms": symptom,
            "treatment": treatment
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/mock-sensor", methods=["POST"])
def mock_sensor_data():
    try:
        data = request.json

        latest_sensor_data["temperature"] = float(data.get("temperature", 28))
        latest_sensor_data["humidity"] = float(data.get("humidity", 70))
        latest_sensor_data["soil_percent"] = float(data.get("soil_percent", 30))
        latest_sensor_data["water_low"] = parse_bool(data.get("water_low", False))
        latest_sensor_data["pump_water"] = parse_bool(data.get("pump_water", False))
        latest_sensor_data["solenoid"] = parse_bool(data.get("solenoid", False))
        latest_sensor_data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latest_sensor_data["pump_fert"] = parse_bool(data.get("pump_fert", False))

        return jsonify({
            "message": "Mock sensor data updated",
            "sensor_data": latest_sensor_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dashboard", methods=["GET"])
def dashboard_data():
    return jsonify({
        "sensor_data": latest_sensor_data,
        "ai_decision": latest_ai_decision,
        "fertilization_decision": latest_fertilization_decision
    })
# Run the Flask app
if __name__ == "__main__":
    start_mqtt_listener()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
