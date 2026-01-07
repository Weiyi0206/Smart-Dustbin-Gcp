# Smart Dustbin IoT Application on Google Cloud Platform

**Course:** CPC357: IoT Architecture & Smart Applications  
**Session:** 2025/2026  
**Project:** Intelligent Waste Classification System

## Project Overview
This project is a Proof of Concept (PoC) for a smart dustbin that uses Generative AI (Gemini 2.5) to recognize waste and automatically sort it into "Recyclable" or "General Waste" bins. The system is fully deployed and operational on the Google Cloud Platform (GCP).

## System Architecture
1.  **Edge Layer:** Maker Feather AIoT S3 (Simulated) captures images.
2.  **Cloud Layer:** Google Cloud Functions acts as the controller.
3.  **Intelligence:** Vertex AI (Gemini 2.5 Flash) performs Zero-Shot image classification.
4.  **Data Layer:** Google Firestore stores sorting logs.
5.  **Application Layer:** Streamlit Dashboard (Cloud Run) visualizes waste statistics.

## Deployment Status
The application components are deployed as follows:
*   **Backend:** Deployed on **Google Cloud Functions**. Handles image uploads, interacts with Gemini AI, and logs data to Firestore.
*   **Frontend:** Deployed on **Google Cloud Run**. Provides a real-time dashboard for monitoring waste statistics.
*   **Database:** **Google Firestore** is used for persistent storage of classification logs.

## How to Run the Simulation
To test the system using the IoT device simulation script against the deployed backend:

1.  **Configure Environment:**
    Create or update the `.env` file in the `simulation` directory with your deployed Cloud Function URL and dataset path:
    ```env
    CLOUD_FUNCTION_URL=https://<YOUR_REGION>-<YOUR_PROJECT_ID>.cloudfunctions.net/<FUNCTION_NAME>
    DATASET_PATH=path/to/your/dataset
    ```

2.  **Run Simulation:**
    Execute the simulation script to start sending images to the cloud:
    ```bash
    cd simulation
    python simulation.py
    ```

## Accessing the Dashboard
Navigate to [Frontend Dashboard](https://dustbin-dashboard-633176041818.asia-southeast1.run.app/) in a web browser to access the EcoSort Analytics Dashboard.

## Requirements
*   Python 3.10+
*   Google Cloud Platform Account (with Cloud Functions, Cloud Run, Vertex AI, and Firestore enabled)
*   Gemini 2.5 Flash API Access