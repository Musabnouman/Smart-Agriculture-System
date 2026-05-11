# FarmFriend: A Smart Agriculture System

FarmFriend is an intelligent agricultural solution designed to empower farmers by leveraging modern technology. This project integrates **deep learning** for accurate plant disease detection and **machine learning** for efficient irrigation scheduling, providing actionable insights through a user-friendly interface.

-----

## Link : [FarmFriend](https://smart-agriculture-system-delta.vercel.app/)

----

## Key Features

  * **Real-time Disease Detection:** Instantly identify plant diseases by uploading an image. Our system uses a high-accuracy deep learning model to provide a quick diagnosis.
  * **Intelligent Irrigation Scheduling:** Get smart recommendations on whether to irrigate your crops. The system analyzes key environmental and soil data to help conserve water and ensure optimal plant health.
  * **User-Friendly Interface:** A clean and intuitive web application built with React and Vite for seamless user interaction.
  * **Scalable Backend:** Powered by a robust Flask API, ensuring secure and efficient communication between the frontend and the machine learning models.

-----

## System Architecture & Technology Stack

The system operates on a simple and effective architecture: a **React frontend** interacts with a **Flask backend API**, which hosts and serves predictions from the two core machine learning models.

  * **Frontend:** React, Vite, TypeScript
  * **Backend:** Python, Flask
  * **Machine Learning:** TensorFlow, Keras, Scikit-learn
  * **Primary Dataset Source:** Kaggle

-----

## Core Models

### 1\. Plant Disease Detection (MobileNetV2)

This module uses a deep convolutional neural network to classify plant diseases from images.

  * **Model:** **MobileNetV2** with Transfer Learning.
  * **Why MobileNetV2?** It was chosen for its excellent balance of **high accuracy** and **low computational cost**, making it ideal for deployment on edge devices or mobile platforms.
  * **Architecture:** The pre-trained MobileNetV2 base is augmented with `GlobalAveragePooling2D`, `Dense`, `BatchNormalization`, and `Dropout` layers, culminating in a `Softmax` output layer for multi-class classification.
  * **Performance:** Achieved approximately **90% accuracy** on the **PlantVillage dataset**.
  * **Training:** Optimized using the **Adam** optimizer with a **Categorical Crossentropy** loss function.

### 2\. Intelligent Irrigation Scheduling (Logistic Regression)

This module predicts the need for irrigation using a binary classification model.

  * **Model:** **Logistic Regression**.
  * **Why Logistic Regression?** It's highly **interpretable, fast, and efficient**, making it perfect for real-time decision-making based on sensor-like data.
  * **Features:** The model is trained on a tabular dataset including features like **temperature, humidity, rainfall, and soil moisture**.
  * **Output:** A binary prediction: `Irrigation Required` or `Irrigation Not Required`.
  * **Performance:** Achieved approximately **85% accuracy**.

### Model Alternatives Explored

To ensure the best model selection, several alternatives were evaluated:

  * **ResNet50:** Achieved the highest accuracy (**95%**) for disease detection but was deemed too heavyweight for a lightweight application.
  * **VGG16:** Resulted in lower accuracy compared to other CNN architectures.
  * **Random Forest:** Considered for irrigation scheduling and useful for feature importance, but was computationally heavier than Logistic Regression.
  * **SVM & Naive Bayes:** While fast, they were less accurate for the given datasets.

-----

## Project Demo

Here's a glimpse of the FarmFriend user interface.
![WhatsApp Image 2025-03-20 at 22 18 02_3f12eb2e](https://github.com/user-attachments/assets/2922b39f-d46c-469d-8063-daf6a3c5ac9c)
![WhatsApp Image 2025-03-20 at 22 19 19_55a12dbe](https://github.com/user-attachments/assets/763c4a56-5f9a-47ac-a0ca-a59ba8cc43e6)
![WhatsApp Image 2025-03-20 at 22 20 04_6f847494](https://github.com/user-attachments/assets/08b64672-4551-4c1b-8171-909cfb9bcc9d)
-----

## Future Scope

We plan to enhance FarmFriend with the following features:

  * **IoT Sensor Integration:** Incorporate real-time data from soil moisture, temperature, and humidity sensors for hyper-accurate irrigation predictions.
  * **Mobile Application:** Develop a dedicated mobile app for on-the-go access and convenience.
  * **Advanced Analytics Dashboard:** Implement a dashboard to visualize historical data, track disease trends, and monitor crop health over time.
  * **Cloud Deployment:** Migrate the application to a cloud platform (like AWS or GCP) for improved scalability and accessibility.

-----

## Contributors

  * **Dev Patel** - [@devpatel0005](https://github.com/devpatel0005)
  * **Hari Patel** - [@haripatel07](https://github.com/haripatel07)
  * **Het Patel** - [@ihetpatel](https://github.com/ihetpatel)
