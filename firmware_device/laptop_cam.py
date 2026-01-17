import cv2
import serial
import time
import sys


SERIAL_PORT = "COM5" 
BAUD_RATE = 921600 

def main():
    try:
        print(f"🔌 Connecting to ESP32 on {SERIAL_PORT} @ {BAUD_RATE}...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2) 
        print("✅ Serial Connected.")
    except Exception as e:
        print(f"❌ Error opening serial port: {e}")
        return

    # Open Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        return

    print("\n--- PASSTHROUGH MODE READY ---")
    print("1. Aim camera")
    print("2. Press [SPACE] to capture & send to ESP32")
    print("3. Press [Q] to quit\n")

    # Flush any startup messages from ESP32
    ser.reset_input_buffer()

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame_resized = cv2.resize(frame, (320, 240))
        
        cv2.imshow("Laptop Camera Source", frame_resized)

        key = cv2.waitKey(1)

        if key == ord(' '): # SPACEBAR pressed
            print("📸 Capturing image...")
            
            # Compress to JPG in memory
            _, img_encoded = cv2.imencode('.jpg', frame_resized, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            img_bytes = img_encoded.tobytes()
            img_size = len(img_bytes)

            print(f"📦 Image Size: {img_size} bytes")
            
            # Send Header Protocol
            header = f"IMG_START:{img_size}\n"
            ser.write(header.encode())
            print(f"➡️  Sending Header: {header.strip()}")
            
            # Send Binary Data
            print("➡️  Streaming Data to ESP32...", end='')
            ser.write(img_bytes)
            print(" Done.")
            
            # Wait for ESP32 Response
            print("⏳ Waiting for Cloud Result from ESP32...")
            start_wait = time.time()
            while time.time() - start_wait < 15: # 15s timeout
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"🤖 ESP32 says: {line}")
                        
                    if "RESULT:" in line:
                        bin_type = line.split("RESULT:")[1]
                        print(f"✅ FINAL SORTING DECISION: [{bin_type}]")
                        break
            print("------------------------------------------------")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    ser.close()

if __name__ == "__main__":
    main()