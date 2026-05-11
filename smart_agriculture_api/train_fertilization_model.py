import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

np.random.seed(42)

rows = []

for _ in range(2000):
    temperature = np.random.uniform(15, 40)
    humidity = np.random.uniform(30, 95)
    soil_percent = np.random.uniform(10, 90)
    water_low = np.random.choice([0, 1], p=[0.9, 0.1])
    days_since_last_fertilization = np.random.randint(0, 21)
    days_since_last_watering = np.random.randint(0, 7)
    watering_count_24h = np.random.randint(0, 6)
    plant_age_days = np.random.randint(10, 120)

    fertilization_required = 0

    # Training label logic for prototype:
    # fertilize only if enough time passed and conditions are safe
    if (
        days_since_last_fertilization >= 7
        and water_low == 0
        and 30 <= soil_percent <= 75
        and temperature < 35
        and watering_count_24h <= 3
        and plant_age_days >= 15
    ):
        fertilization_required = 1

    # Safety blocks
    if soil_percent < 20 or temperature > 37 or water_low == 1:
        fertilization_required = 0

    rows.append([
        temperature,
        humidity,
        soil_percent,
        water_low,
        days_since_last_fertilization,
        days_since_last_watering,
        watering_count_24h,
        plant_age_days,
        fertilization_required
    ])

columns = [
    "temperature",
    "humidity",
    "soil_percent",
    "water_low",
    "days_since_last_fertilization",
    "days_since_last_watering",
    "watering_count_24h",
    "plant_age_days",
    "fertilization_required"
]

df = pd.DataFrame(rows, columns=columns)

X = df.drop("fertilization_required", axis=1)
y = df["fertilization_required"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=6,
    random_state=42
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(y_test, pred))

joblib.dump(model, "models/fertilization_model.pkl")
joblib.dump(scaler, "models/fertilization_scaler.pkl")

print("Saved models/fertilization_model.pkl")
print("Saved models/fertilization_scaler.pkl")