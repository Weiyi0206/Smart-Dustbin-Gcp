import requests
import os
import random
import time
from dotenv import load_dotenv  

load_dotenv()

CLOUD_URL = os.getenv("CLOUD_FUNCTION_URL")
DATASET_PATH = os.getenv("DATASET_PATH")

if not CLOUD_URL or not DATASET_PATH:
    print("Error: Please set CLOUD_FUNCTION_URL and DATASET_PATH in .env file")
    exit()

def start_simulation():
    print(f"--- IoT Device Simulation Started ---")
    
    categories = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))]
    
    categories.sort()

    for category in categories:
        try:
            folder = os.path.join(DATASET_PATH, category)
            files_in_folder = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            
            if not files_in_folder:
                print(f"[DEVICE] No images found in {category}, skipping...")
                continue

            image_file = random.choice(files_in_folder)
            full_path = os.path.join(folder, image_file)
            
            print(f"\n[DEVICE] Camera captured: {category}/{image_file}")
            
            # Upload to Cloud
            with open(full_path, 'rb') as img:
                files = {'file': img}
                print("[DEVICE] Uploading...")
                response = requests.post(CLOUD_URL, files=files)
            
            # Result
            if response.status_code == 200:
                data = response.json()
                print(f"[CLOUD] AI Detected: {data['class'].upper()}")
                print(f"[CLOUD] Command: {data['command']}")
                
                if category in data['class']: 
                    print("✅ Correct Prediction")
                else: 
                    print("❌ Incorrect Prediction")
            else:
                print(f"Error: {response.text}")

            time.sleep(2) # Wait 2 seconds before next trash

        except Exception as e:
            print(f"Error processing {category}: {e}")
            time.sleep(2)

if __name__ == "__main__":
    start_simulation()