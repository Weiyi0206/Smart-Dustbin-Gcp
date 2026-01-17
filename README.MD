# ♻️ Smart Dustbin IoT Application on Google Cloud Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![PlatformIO](https://img.shields.io/badge/Firmware-Arduino%2FC%2B%2B-green?logo=arduino&logoColor=white)
![GCP](https://img.shields.io/badge/Cloud-Google%20Cloud%20Platform-red?logo=googlecloud&logoColor=white)
![Status](https://img.shields.io/badge/Status-Proof%20of%20Concept-orange)

## 📖 Project Overview
This project is a Proof of Concept (PoC) for an intelligent waste management system. It leverages **Generative AI (Gemini 2.5)** to visually recognize waste items and automatically sort them into "Recyclable" or "General Waste" bins.

To overcome hardware constraints while maintaining a robust IoT architecture, the system employs a **Serial-to-Cloud Bridge** design:
1.  **High-Fidelity Capture:** A laptop acts as the visual sensor gateway.
2.  **IoT Hub:** An ESP32 microcontroller receives raw image data via Serial, handles the secure HTTPS connection to Google Cloud, and actuates the sorting mechanism.

## 📂 Repository Structure
```text
Smart-Dustbin-Gcp/
├── cloud_backend/        # Google Cloud Function (Python) - The AI Controller
│   └── main.py           # Handles image receipt and Gemini API calls
├── firmware_device/      # ESP32 Firmware & Gateway Script
│   ├── firmware.ino      # C++ code for ESP32 (HTTPS & Servo Logic)
│   └── laptop_cam.py     # Python script to capture & stream images to ESP32
├── frontend/             # Streamlit Dashboard (Cloud Run)
│   ├── app.py            # Visualization logic
│   └── Dockerfile        # Container configuration
└── README.md             # Project documentation
```

## 🏗 System Architecture
1.  **Image Source:** Laptop Webcam captures the image.
2.  **Data Transmission:** Python script compresses the image and streams it via UART (`921600` baud) to the ESP32.
3.  **Network Node:** ESP32 reconstructs the payload and uploads it via **HTTPS** to Google Cloud Functions.
4.  **Intelligence:** **Vertex AI (Gemini 2.5 Flash)** analyzes the image context (Zero-Shot Learning).
5.  **Persistence:** Results are logged in **Firestore**.
6.  **Actuation:** Cloud response triggers the ESP32 to drive a Servo Motor (Pin 5).
7.  **Visualization:** **Cloud Run** hosts a Streamlit dashboard for real-time analytics.

---

## ⚙️ Setup & Installation

### 1. Cloud Backend (Google Cloud Functions)
Navigate to the `cloud_backend` folder and deploy the function:
```bash
gcloud functions deploy process_waste \
--gen2 --runtime=python310 \
--region=asia-southeast1 \
--source=. \
--entry-point=process_waste \
--trigger-http --allow-unauthenticated
```
*Note: Ensure Vertex AI and Firestore APIs are enabled in your GCP project.*

### 2. Frontend Dashboard (Google Cloud Run)
Navigate to the `frontend` folder and deploy:
```bash
gcloud run deploy dustbin-dashboard --source . --region=asia-southeast1 --allow-unauthenticated
```

### 3. Firmware (ESP32)
1.  Open `firmware_device/firmware.ino` in Arduino IDE.
2.  Install required libraries: `WiFi`, `WiFiClientSecure`, `ESP32Servo`, `ArduinoJson`.
3.  **Configuration:** Create a file named `secrets.h` inside the `firmware_device` folder with your credentials:
    ```cpp
    const char* ssid = "YOUR_WIFI_SSID";
    const char* password = "YOUR_WIFI_PASSWORD";
    // NOTE: Do not include 'https://' prefix here
    const char* serverName = "classify-waste-xyz.run.app"; 
    const char* serverPath = "/process_waste"; 
    ```
4.  Upload to ESP32. **Ensure Serial Monitor baud rate is set to 921600.**

### 4. Laptop Gateway Client
1.  Install Python dependencies:
    ```bash
    pip install opencv-python pyserial
    ```
2.  Open `firmware_device/laptop_cam.py`.
3.  Update the **COM Port** to match your ESP32 connection:
    ```python
    SERIAL_PORT = "COM5" # Check Device Manager (Windows) or /dev/ttyUSB0 (Linux/Mac)
    BAUD_RATE = 921600   # Must match firmware
    ```

---

## 🚀 Usage Guide

1.  **Hardware Prep:** Ensure ESP32 is powered via USB and Servo is connected to **Pin 5**.
2.  **Start Gateway:** Run the camera script:
    ```bash
    python firmware_device/laptop_cam.py
    ```
3.  **Operation:**
    *   Aim camera at trash.
    *   Press **[SPACE]** to capture.
    *   *Watch the terminal:* You will see the image streaming to ESP32, then the Cloud response.
    *   *Watch the servo:* It will move to 90° (Recycle) or 180° (General).
4.  **Stop:** Press **[Q]** to quit.

## 📊 Analytics Dashboard
Access the live dashboard to view historical logs, efficiency metrics, and material breakdown:
[**🔗 Open Live Dashboard**](https://dustbin-dashboard-633176041818.asia-southeast1.run.app/)

## 🛠 Hardware Wiring
| Component | ESP32 Pin |
| :--- | :--- |
| Servo Signal | GPIO 5 |
| Status LED | GPIO 4 |
| VCC | 5V / USB |
| GND | GND |

---

## 🛡️ Security Note
This repository uses a `.gitignore` file to exclude sensitive credentials (`secrets.h` and `service-account.json`). For local development, you must recreate these files based on the instructions above.
