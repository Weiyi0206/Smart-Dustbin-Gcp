#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Servo.h>
#include "esp_camera.h"

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";
const char* serverUrl = "YOUR_CLOUD_FUNCTION_URL";

Servo myServo;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  myServo.attach(13); // Servo Pin
  
  // Camera Init code (Standard OV2640 setup)...
}

void loop() {
  // Capture Photo
  camera_fb_t * fb = esp_camera_fb_get();
  
  // Send to Cloud
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "image/jpeg");
  
  int responseCode = http.POST(fb->buf, fb->len);
  String payload = http.getString(); // JSON Response
  
  // Actuate Servo based on response
  if(payload.indexOf("Recycle") > 0) {
    myServo.write(90); // Open Recycle Bin
  } else {
    myServo.write(0);  // Open General Bin
  }
  
  esp_camera_fb_return(fb);
  delay(5000);
}