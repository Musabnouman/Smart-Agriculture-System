"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, Leaf, Droplets, Thermometer, Waves, AlertTriangle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../config.ts";

type SensorData = {
  temperature: number | null;
  humidity: number | null;
  soil_percent: number | null;
  water_low: boolean | null;
  pump_water: boolean;
  solenoid: boolean;
  pump_fert: boolean;
  last_update: string | null;
};

type AiDecision = {
  irrigation_required: boolean;
  watering_duration: number;
  reason: string;
  raw_model_output?: number | null;
  last_prediction_time: string | null;
};

type FertilizationDecision = {
  fertilization_required: boolean;
  fertilizer_duration: number;
  fertilizer_reason: string;
  raw_fertilizer_model_output?: number | null;
  last_fertilization_prediction_time: string | null;
  last_fertilization_time?: string | null;
};



type DashboardResponse = {
  sensor_data: SensorData;
  ai_decision: AiDecision;
  fertilization_decision: FertilizationDecision;
};

const IrrigationPage: React.FC = () => {
  const navigate = useNavigate();

const [sensorData, setSensorData] = useState<SensorData | null>(null);
const [aiDecision, setAiDecision] = useState<AiDecision | null>(null);
const [fertilizationDecision, setFertilizationDecision] =
  useState<FertilizationDecision | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>("");

  // Test values for mock/simulation before ESP32 MQTT is connected
  const [testTemperature, setTestTemperature] = useState<number>(32);
  const [testHumidity, setTestHumidity] = useState<number>(70);
  const [testSoil, setTestSoil] = useState<number>(25);
  const [testWaterLow, setTestWaterLow] = useState<boolean>(false);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/dashboard`);
      if (!response.ok) {
        throw new Error(`Dashboard API error: ${response.status}`);
      }

      const data: DashboardResponse = await response.json();
      setSensorData(data.sensor_data);
      setAiDecision(data.ai_decision);
      setFertilizationDecision(data.fertilization_decision);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setStatusMessage("Failed to fetch dashboard data. Make sure Flask backend is running.");
    }
  };

  const runAiPrediction = async () => {
    setLoading(true);
    setStatusMessage("Running AI irrigation prediction...");

    try {
      const response = await fetch(`${API_BASE}/predict/irrigation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          temperature: testTemperature,
          humidity: testHumidity,
          soil_percent: testSoil,
          water_low: testWaterLow,
        }),
      });

      if (!response.ok) {
        throw new Error(`Prediction API error: ${response.status}`);
      }

      await response.json();
      await fetchDashboardData();

      setStatusMessage("AI prediction updated successfully.");
    } catch (error) {
      console.error("Error running AI prediction:", error);
      setStatusMessage("Failed to run AI prediction. Check backend terminal.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();

    // Auto-refresh dashboard every 3 seconds
    const interval = setInterval(fetchDashboardData, 3000);

    return () => clearInterval(interval);
  }, []);

  const formatValue = (value: number | null | undefined, unit: string = "") => {
    if (value === null || value === undefined) return "No data";
    return `${value}${unit}`;
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="px-4 py-2 border-b flex items-center justify-between bg-white shadow-sm">
        <div className="flex items-center gap-1 font-medium">
          <Leaf className="h-5 w-5 text-green-600" />
          <span className="text-md">SmartFarm</span>
        </div>

        <button
          onClick={() => navigate("/")}
          className="flex items-center text-green-600 text-sm hover:text-green-700 transition"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Home
        </button>
      </header>

      <main className="flex-1 p-6 bg-[url('/latest.png')] bg-cover bg-center bg-no-repeat relative before:absolute before:inset-0 before:bg-black/40">
        <div className="relative z-10 max-w-6xl mx-auto space-y-6">
          <Card className="shadow-xl bg-white/95">
            <CardHeader>
              <CardTitle className="text-2xl font-semibold text-center text-green-700">
                Smart Irrigation and Fertilization Dashboard
              </CardTitle>
              <p className="text-center text-sm text-gray-600">
                Live sensor monitoring, AI irrigation and fertilization prediction, and decision support
              </p>
            </CardHeader>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-white/95 shadow-md">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Waves className="h-4 w-4 text-blue-600" />
                  Soil Moisture
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatValue(sensorData?.soil_percent, "%")}
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/95 shadow-md">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Thermometer className="h-4 w-4 text-red-600" />
                  Temperature
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatValue(sensorData?.temperature, "°C")}
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/95 shadow-md">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Droplets className="h-4 w-4 text-cyan-600" />
                  Humidity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {formatValue(sensorData?.humidity, "%")}
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/95 shadow-md">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  Water Tank
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className={`text-2xl font-bold ${sensorData?.water_low ? "text-red-600" : "text-green-600"}`}>
                  {sensorData?.water_low === null || sensorData?.water_low === undefined
                    ? "No data"
                    : sensorData.water_low
                    ? "LOW"
                    : "OK"}
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="bg-white/95 shadow-xl">
              <CardHeader>
                <CardTitle className="text-lg text-green-700">
                  AI Irrigation Decision
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="font-medium">Irrigation Required:</span>
                  <span
                    className={`font-bold ${
                      aiDecision?.irrigation_required ? "text-green-700" : "text-gray-700"
                    }`}
                  >
                    {aiDecision?.irrigation_required ? "YES" : "NO"}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="font-medium">Predicted Duration:</span>
                  <span className="font-bold">
                    {aiDecision ? `${aiDecision.watering_duration} seconds` : "No data"}
                  </span>
                </div>

                <div>
                  <p className="font-medium mb-1">Reason:</p>
                  <p className="text-sm text-gray-700 bg-gray-100 p-3 rounded-md">
                    {aiDecision?.reason || "No prediction yet"}
                  </p>
                </div>

                <Separator />

                <div className="text-sm text-gray-600 space-y-1">
                  <p>Last Sensor Update: {sensorData?.last_update || "No data"}</p>
                  <p>Last AI Prediction: {aiDecision?.last_prediction_time || "No data"}</p>
                  <p>Raw Model Output: {aiDecision?.raw_model_output ?? "No data"}</p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/95 shadow-xl">
  <CardHeader>
    <CardTitle className="text-lg text-green-700">
      AI Fertilization Decision
    </CardTitle>
  </CardHeader>

  <CardContent className="space-y-3">
    <div className="flex justify-between">
      <span className="font-medium">Fertilization Required:</span>
      <span
        className={`font-bold ${
          fertilizationDecision?.fertilization_required
            ? "text-green-700"
            : "text-gray-700"
        }`}
      >
        {fertilizationDecision?.fertilization_required ? "YES" : "NO"}
      </span>
    </div>

    <div className="flex justify-between">
      <span className="font-medium">Fertilizer Duration:</span>
      <span className="font-bold">
        {fertilizationDecision
          ? `${fertilizationDecision.fertilizer_duration} seconds`
          : "No data"}
      </span>
    </div>

    <div>
      <p className="font-medium mb-1">Reason:</p>
      <p className="text-sm text-gray-700 bg-gray-100 p-3 rounded-md">
        {fertilizationDecision?.fertilizer_reason ||
          "No fertilization prediction yet"}
      </p>
    </div>

    <Separator />

    <div className="text-sm text-gray-600 space-y-1">
      <p>
        Last Fertilization Prediction:{" "}
        {fertilizationDecision?.last_fertilization_prediction_time || "No data"}
      </p>
      <p>
        Last Fertilization Time:{" "}
        {fertilizationDecision?.last_fertilization_time || "No data"}
        </p>
        <p>
        Raw Fertilizer Model Output:{" "}
        {fertilizationDecision?.raw_fertilizer_model_output ?? "No data"}
         </p>
        </div>
        </CardContent>
        </Card>
            <Card className="bg-white/95 shadow-xl">
              <CardHeader>
                <CardTitle className="text-lg text-green-700">
                  Pump and Valve Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="font-medium">Water Pump:</span>
                  <span className={`font-bold ${sensorData?.pump_water ? "text-green-700" : "text-gray-700"}`}>
                    {sensorData?.pump_water ? "ON" : "OFF"}
                  </span>
                </div>
                <div className="flex justify-between">
                <span className="font-medium">Fertilizer Pump:</span>
                <span className={`font-bold ${sensorData?.pump_fert ? "text-green-700" : "text-gray-700"}`}>
                  {sensorData?.pump_fert ? "ON" : "OFF"}
                </span>
                </div>

                <div className="flex justify-between">
                  <span className="font-medium">Solenoid Valve:</span>
                  <span className={`font-bold ${sensorData?.solenoid ? "text-green-700" : "text-gray-700"}`}>
                    {sensorData?.solenoid ? "ON" : "OFF"}
                  </span>
                </div>

                <Separator />

                <p className="text-sm text-gray-700">
                  In the final system, the backend will send MQTT commands to the ESP32 based on this AI decision.
                </p>

                {statusMessage && (
                  <p className="text-sm font-medium text-blue-700 bg-blue-50 p-3 rounded-md">
                    {statusMessage}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <Card className="bg-white/95 shadow-xl">
            <CardHeader>
              <CardTitle className="text-lg text-green-700">
                Manual Test Mode
              </CardTitle>
              <p className="text-sm text-gray-600">
               This section is only for manual testing. In the final system, MQTT sensor data automatically updates the AI decisions.
              </p>
            </CardHeader>

            <CardContent className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
              <div>
                <Label>Temperature (°C)</Label>
                <Input
                  type="number"
                  value={testTemperature}
                  onChange={(e) => setTestTemperature(Number(e.target.value))}
                />
              </div>

              <div>
                <Label>Humidity (%)</Label>
                <Input
                  type="number"
                  value={testHumidity}
                  onChange={(e) => setTestHumidity(Number(e.target.value))}
                />
              </div>

              <div>
                <Label>Soil Moisture (%)</Label>
                <Input
                  type="number"
                  value={testSoil}
                  onChange={(e) => setTestSoil(Number(e.target.value))}
                />
              </div>

              <div>
                <Label>Water Tank</Label>
                <Button
                  type="button"
                  variant={testWaterLow ? "destructive" : "outline"}
                  className="w-full mt-1"
                  onClick={() => setTestWaterLow(!testWaterLow)}
                >
                  {testWaterLow ? "LOW" : "OK"}
                </Button>
              </div>

              <Button
                onClick={runAiPrediction}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {loading ? "Running..." : "Run AI Prediction"}
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default IrrigationPage;