#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h> 

#include "secrets.h" 

const int serverPort = 443; 
const unsigned long SERIAL_TIMEOUT = 5000;
const int BUFFER_SIZE = 1024; 

#define SERVO_PIN 5
#define LED_PIN   4

WiFiClientSecure client;
Servo sortingServo;

void setup() {
  Serial.begin(921600); 
  
  pinMode(LED_PIN, OUTPUT);
  sortingServo.attach(SERVO_PIN);
  sortingServo.write(0); 

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Blink while connecting
  }
  digitalWrite(LED_PIN, LOW);
  
  client.setInsecure(); 
  
  Serial.println("ESP32_READY");
}

void loop() {
  // Protocol: Laptop sends "IMG_START:<size_in_bytes>"
  if (Serial.available() > 0) {
    String header = Serial.readStringUntil('\n');
    header.trim();
    
    if (header.startsWith("IMG_START:")) {
      long imageSize = header.substring(10).toInt();
      processImageUpload(imageSize);
    }
  }
}

void processImageUpload(long imageLen) {
  digitalWrite(LED_PIN, HIGH);
  
  if (client.connect(serverName, serverPort)) {
    
    String boundary = "Esp32Boundary";
    String head = "--" + boundary + "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"capture.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
    String tail = "\r\n--" + boundary + "--\r\n";
    
    long totalLen = imageLen + head.length() + tail.length();
  
    client.println("POST " + String(serverPath) + " HTTP/1.1");
    client.println("Host: " + String(serverName));
    client.println("Content-Length: " + String(totalLen));
    client.println("Content-Type: multipart/form-data; boundary=" + boundary);
    client.println();
    client.print(head);
    
    long bytesRemaining = imageLen;
    uint8_t buff[BUFFER_SIZE];
    unsigned long lastRead = millis();
    
    while (bytesRemaining > 0) {
      // Timeout protection
      if (millis() - lastRead > SERIAL_TIMEOUT) {
        client.stop();
        return;
      }
      
      int available = Serial.available();
      if (available > 0) {
        int toRead = min(available, BUFFER_SIZE);
        if (toRead > bytesRemaining) toRead = bytesRemaining;
        
        Serial.readBytes(buff, toRead);
        client.write(buff, toRead);
        
        bytesRemaining -= toRead;
        lastRead = millis();
      }
    }
    
    client.print(tail);
    
    handleCloudResponse();
    
  } else {
    while(Serial.available()) Serial.read();
  }
  
  digitalWrite(LED_PIN, LOW);
}

void handleCloudResponse() {
  String responseBody = "";
  bool headerEnded = false;
  
  // Read timeout
  unsigned long start = millis();
  while (client.connected() && millis() - start < 10000) {
    if (client.available()) {
      String line = client.readStringUntil('\n');
      if (line == "\r") { 
        headerEnded = true; 
        continue; 
      }
      if (headerEnded) {
        responseBody += line;
      }
    }
  }
  client.stop();

  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, responseBody);

  if (!error) {
    const char* binType = doc["bin"];
    
    Serial.print("RESULT:");
    Serial.println(binType);

    if (String(binType) == "Recycle") {
      openBin(0);
    } else {
      openBin(180);
    }
  }
}

void openBin(int angle) {
  sortingServo.write(angle);
  delay(3000);
  sortingServo.write(90);
}