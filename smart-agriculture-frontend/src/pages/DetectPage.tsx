"use client";

import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Leaf, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE } from "../config.ts";

const DetectPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<{ disease: string; confidence: number; cause: string; symptoms: string;  treatment: string, healthy: string; } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setSelectedImage(reader.result as string);
        setResult(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) return;
    setIsAnalyzing(true);

    try {
      const base64Data = selectedImage.split(",")[1];
      const response = await fetch(`${API_BASE}/predict/plant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: `data:image/jpeg;base64,${base64Data}` }),
      });

      const data = await response.json();
      if (response.ok) {
        setResult(data);
      } else {
        console.error("API Error:", data.error);
        setResult(null);
      }
    } catch (error) {
      console.error("Request failed:", error);
      setResult(null);
    }
    setIsAnalyzing(false);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <header className="px-4 py-2 border-b flex items-center justify-between bg-white shadow-sm">
        <div className="flex items-center gap-1 font-medium">
          <Leaf className="h-5 w-5 text-green-600" />
          <span className="text-md">FarmFriend</span>
        </div>
        <button
          onClick={() => navigate("/")}
          className="flex items-center text-green-600 text-sm hover:text-green-700 transition"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Home
        </button>
      </header>


      <main className="flex-1 py-12 bg-[#fef8e6]">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col gap-8 md:gap-12">

            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Upload Plant Image</CardTitle>
                  <CardDescription>Upload an image to detect plant diseases</CardDescription>
                </CardHeader>
                <CardContent>
                  <input type="file" accept="image/*" ref={fileInputRef} className="hidden" onChange={handleImageChange} />

                  <div
                    onClick={() => fileInputRef.current?.click()}
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDragging(true);
                    }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setIsDragging(false);
                      const file = e.dataTransfer.files[0];
                      if (file) {
                        handleImageChange({ target: { files: [file] } } as unknown as React.ChangeEvent<HTMLInputElement>);
                      }
                    }}
                    className={`cursor-pointer border-2 ${isDragging ? "border-green-600" : "border-gray-300"} border-dashed p-6 text-center rounded-lg`}
                  >
                    <Upload className="mx-auto h-8 w-8 text-gray-500" />
                    <p className="mt-2 text-sm text-gray-500">Click or drag an image to upload</p>
                  </div>

                  {selectedImage && (
                    <div className="mt-4 h-[200px] w-full md:w-[200px] overflow-hidden border rounded-lg">
                        <img src={selectedImage} alt="Selected Plant" className="h-full w-full object-contain" />
                     </div>
                  )}
                </CardContent>
                <CardFooter>
                  <Button onClick={analyzeImage} disabled={isAnalyzing} className="bg-green-600 hover:bg-green-700">
                    {isAnalyzing ? "Analyzing..." : "Detect Disease"}
                  </Button>
                </CardFooter>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Detection Results</CardTitle>
                </CardHeader>
                <CardContent>
                  {isAnalyzing ? (
                    <p className="text-xl font-semibold">Analyzing...</p>
                  ) : result ? (
                    <div className="space-y-2">
                      <p className="text-xl font-semibold text-green-700">{result.disease}</p>
                      <p className="text-gray-700">Confidence: <span className="font-medium">{result.confidence.toFixed(1)}%</span></p>
                      
                      {result.healthy && (
                        <p className="text-green-600 font-medium">✔ {result.healthy}</p>
                      )}
                      
                      {result.cause && (
                        <p className="text-gray-800">
                          <span className="font-semibold">Cause:</span> {result.cause}
                        </p>
                      )}
                      
                      {result.symptoms && (
                        <p className="text-gray-800">
                          <span className="font-semibold">Symptoms:</span> {result.symptoms}
                        </p>
                      )}
                      
                      {result.treatment && (
                        <p className="text-gray-800">
                          <span className="font-semibold">Treatment:</span> {result.treatment}
                        </p>
                      )}
                    </div>

                  ) : (
                    <p className="text-xl font-semibold">Upload an image to see results.</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DetectPage;