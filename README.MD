# Smart Dustbin IoT Application on Google Cloud Platform

## Project Overview
This project is a Proof of Concept (PoC) for a smart dustbin that uses Generative AI (Gemini 2.5) to recognize waste and automatically sort it into "Recyclable" or "General Waste" bins. The system uses a hybrid edge-cloud architecture where a laptop camera captures images, sends them to an ESP32 microcontroller, which then uploads them to the Google Cloud Platform (GCP) for analysis.

## System Architecture
1.  **Image Capture:** Laptop Webcam (via Python script).
2.  **Edge Gateway & Control:** ESP32 Microcontroller (receives image via Serial, uploads to Cloud, controls Servo).
3.  **Cloud Controller:** Google Cloud Functions (HTTP Trigger).
4.  **Intelligence:** Vertex AI (Gemini 2.5 Flash) for Zero-Shot image classification.
5.  **Data Layer:** Google Firestore for logging sorting history.
6.  **Dashboard:** Streamlit App (Cloud Run) for real-time analytics.

## Deployment Status
*   **Backend:** **Google Cloud Functions**. Handles image processing and AI inference.
*   **Frontend:** **Google Cloud Run**. Hosts the Streamlit dashboard.
*   **Database:** **Google Firestore**. Stores waste classification logs.

## Hardware Requirements
*   ESP32 Development Board
*   Servo Motor (Pin 5)
*   LED (Pin 4) - Status Indicator
*   Laptop with Webcam

## Setup & Installation

### 1. Firmware (ESP32)
The firmware is located in `firmware_device/firmware.ino`.

1.  Open the project in Arduino IDE.
2.  Install the required libraries: `WiFi`, `WiFiClientSecure`, `ESP32Servo`, `ArduinoJson`.
3.  Create a `secrets.h` file in the `firmware_device` folder with your credentials:
    ```cpp
    const char* ssid = "YOUR_WIFI_SSID";
    const char* password = "YOUR_WIFI_PASSWORD";
    const char* serverName = "YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net"; 
    const char* serverPath = "/process_waste"; 
    ```
4.  Upload the code to your ESP32.

### 2. Laptop Camera Client
The python script `firmware_device/laptop_cam.py` captures images and sends them to the ESP32.

1.  Install dependencies:
    ```bash
    pip install opencv-python pyserial
    ```
2.  Update the `SERIAL_PORT` variable in `laptop_cam.py` to match your ESP32's COM port (e.g., `COM5` on Windows or `/dev/ttyUSB0` on Linux/Mac).
3.  Run the script:
    ```bash
    python firmware_device/laptop_cam.py
    ```

## Usage
1.  Ensure the ESP32 is powered and connected to the laptop.
2.  Run the `laptop_cam.py` script. You should see a live video feed.
3.  Aim the camera at a waste item.
4.  Press **[SPACE]** to capture and process the image.
    *   The image is sent to the ESP32.
    *   ESP32 uploads it to Google Cloud.
    *   Gemini AI classifies the item.
    *   ESP32 receives the result and moves the servo (Recycle = 0°, General = 180°).
5.  Press **[Q]** to quit the camera script.

## Accessing the Dashboard
Navigate to [Frontend Dashboard](https://dustbin-dashboard-633176041818.asia-southeast1.run.app/) to view real-time statistics and waste logs.

## Tech Stack
*   **Hardware:** ESP32, Servo, Webcam
*   **Firmware:** C++ (Arduino)
*   **Client:** Python (OpenCV, PySerial)
*   **Cloud:** GCP (Cloud Functions, Cloud Run, Firestore, Vertex AI)
