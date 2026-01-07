# Smart Dustbin IoT Application on Google Cloud Platform

**Course:** CPC357: IoT Architecture & Smart Applications  
**Session:** 2025/2026  
**Project:** Intelligent Waste Classification System

## Project Overview
This project is a Proof of Concept (PoC) for a smart dustbin that uses Generative AI (Gemini 2.5) to recognize waste and automatically sort it into "Recyclable" or "General Waste" bins.

## System Architecture
1.  **Edge Layer:** Maker Feather AIoT S3 (Simulated) captures images.
2.  **Cloud Layer:** Google Cloud Functions acts as the controller.
3.  **Intelligence:** Vertex AI (Gemini 2.5 Flash) performs Zero-Shot image classification.
4.  **Data Layer:** Google Firestore stores sorting logs.
5.  **Application Layer:** Streamlit Dashboard (Cloud Run) visualizes waste statistics.

## How to Run
1.  **Backend:** Deploy the code in `2_cloud_backend` to Google Cloud Functions.
2.  **Frontend:** Build and deploy `3_dashboard_frontend` to Cloud Run.
3.  **Simulation:** Update `simulation.py` with your GCP URL and dataset path, then run:
    ```bash
    python simulation.py
    ```

## Requirements
*   Python 3.10+
*   Google Cloud Platform Account
*   Gemini 2.5 Flash API Access