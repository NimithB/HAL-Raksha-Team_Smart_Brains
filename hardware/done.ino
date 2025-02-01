#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <U8g2lib.h>

// WiFi Credentials
const char* ssid = "GATCSE4-2.4Ghz";
const char* password = "global123";

// Initialize server
ESP8266WebServer server(80);

// GPIO Pin Definitions
#define TILT1_PIN 14      
#define TILT2_PIN 3       
#define BUZZER_PIN 15     
#define VIBRATION_PIN 16  
#define HEARTBEAT_PIN A0  
#define TOUCH_PIN 12      

// OLED Display Pins
#define OLED_SDA 4  
#define OLED_SCL 5  
U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

// Initialize variables
bool isVibrating = false;
bool alarmTriggered = false;
bool sosTriggered = false;
unsigned long lastVibrationTime = 0;
unsigned long tiltStartTime = 0;
unsigned long tiltDuration = 3000;
bool vibrationOn = false;
bool isBuzzerOn = false;
const int numReadings = 10;
int heartbeatReadings[numReadings];
int readIndex = 0;
long total = 0;
int heartbeatBPM = 0;

void setup() {
  Serial.begin(115200);

  // Set pin modes
  pinMode(TILT1_PIN, INPUT_PULLUP);
  pinMode(TILT2_PIN, INPUT_PULLUP);
  pinMode(VIBRATION_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(TOUCH_PIN, INPUT);

  for (int i = 0; i < numReadings; i++) {
    heartbeatReadings[i] = 0;
  }

  Wire.begin(OLED_SDA, OLED_SCL);
  u8g2.begin();
  u8g2.clearBuffer();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.setCursor(0, 10);
  u8g2.print("WiFi Connected");
  u8g2.setCursor(0, 20);
  u8g2.print(WiFi.localIP().toString());
  u8g2.sendBuffer();
  delay(2000);

  server.on("/", HTTP_GET, handleRoot);
  server.on("/sos", HTTP_GET, handleSOS);
  server.on("/remind", HTTP_GET, handleRemind);
  server.on("/stop", HTTP_GET, handleStop);
  server.begin();
}

void loop() {
  server.handleClient();
  vibration_rhythm();  

  int tilt1State = digitalRead(TILT1_PIN);
  int tilt2State = digitalRead(TILT2_PIN);
  int rawHeartbeatValue = analogRead(HEARTBEAT_PIN);

  if (tilt1State == HIGH && tilt2State == HIGH) {
    if (tiltStartTime == 0) {
      tiltStartTime = millis();
    } else if (millis() - tiltStartTime >= tiltDuration) {
      if (!sosTriggered) {
        digitalWrite(BUZZER_PIN, HIGH);
        isVibrating = true;
        trigger_local_call();
        sosTriggered = true;
      }
    }
  } else {
    tiltStartTime = 0;
  }

  if (digitalRead(TOUCH_PIN) == HIGH) {
    digitalWrite(BUZZER_PIN, LOW);
    isVibrating = false;
    sosTriggered = false;
    alarmTriggered = false;
  }

  total -= heartbeatReadings[readIndex];
  heartbeatReadings[readIndex] = (rawHeartbeatValue > 990) ? map(rawHeartbeatValue, 999, 1030, 70, 90) : 0;
  total += heartbeatReadings[readIndex];
  readIndex = (readIndex + 1) % numReadings;
  heartbeatBPM = total / numReadings;

  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);

  u8g2.setCursor(0, 10);
  u8g2.print("Tilt1: "); u8g2.print(tilt1State == LOW ? "OFF" : "ON");
  u8g2.setCursor(0, 20);
  u8g2.print("Tilt2: "); u8g2.print(tilt2State == LOW ? "OFF" : "ON");

  if (heartbeatBPM > 70) {  
    u8g2.setCursor(0, 30);
    u8g2.print("HB: "); u8g2.print(heartbeatBPM); u8g2.print(" BPM");
  }

  if (sosTriggered) {
    u8g2.setCursor(60, 30);
    u8g2.print("SOS Triggered");
  } else if (alarmTriggered) {
    u8g2.setCursor(60, 30);
    u8g2.print("Reminder Triggered");
  }

  u8g2.sendBuffer();
  delay(50);
}

void handleRoot() {
  String message = "<html><body><h1>ESP8266 Alarm System</h1>";
  message += "<h3>Click a button to trigger an action</h3>";

  if (sosTriggered) {
    message += "<p>SOS Triggered</p>";
  } else if (alarmTriggered) {
    message += "<p>Reminder Triggered</p>";
  } else {
    message += "<p>No alarm triggered</p>";
  }

  message += "<p>ESP8266 IP: " + WiFi.localIP().toString() + "</p>";
  message += "<br><a href='/sos'><button>SOS</button></a><br><br>";
  message += "<a href='/remind'><button>Remind</button></a><br><br>";
  message += "<a href='/stop'><button>Stop Alarm</button></a>";
  message += "</body></html>";

  server.send(200, "text/html", message);
}

void handleSOS() {
  sosTriggered = true;
  alarmTriggered = false;
  digitalWrite(BUZZER_PIN, HIGH);
  isVibrating = true;
  trigger_local_call();
  server.send(200, "text/html", "<html><body><h1>SOS Triggered!</h1></body></html>");
}

void handleRemind() {
  alarmTriggered = true;
  sosTriggered = false;
  digitalWrite(BUZZER_PIN, HIGH);
  isVibrating = true;
  server.send(200, "text/html", "<html><body><h1>Reminder Triggered!</h1></body></html>");
}

void handleStop() {
  sosTriggered = false;
  alarmTriggered = false;
  digitalWrite(BUZZER_PIN, LOW);
  isVibrating = false;
  server.send(200, "text/html", "<html><body><h1>Alarm Stopped</h1></body></html>");
}

void trigger_local_call() {
  HTTPClient http;
  WiFiClient client;
  String url = "http://172.16.4.226:5000/call";

  Serial.print("Triggering local call: ");
  Serial.println(url);

  http.begin(client, url);
  int httpCode = http.GET();

  if (httpCode == 200) {
    Serial.println("Local call triggered successfully.");
  } else {
   // Serial.print("Failed to trigger local call. HTTP code: ");
    Serial.println(httpCode);
  }

  http.end();
}

void vibration_rhythm() {
  static unsigned long lastVibrationTime = 0;
  static bool vibrationOn = false;

  unsigned long vibrationInterval = 1000;

  if (heartbeatBPM >= 85) {
    vibrationInterval = 60000 / heartbeatBPM;
  }

  if (isVibrating) {
    unsigned long currentMillis = millis();

    if (currentMillis - lastVibrationTime >= vibrationInterval) {
      lastVibrationTime = currentMillis;
      vibrationOn = !vibrationOn;

      if (vibrationOn) {
        analogWrite(VIBRATION_PIN, 180);
      } else {
        analogWrite(VIBRATION_PIN, 0);
      }
    }
  } else {
    analogWrite(VIBRATION_PIN, 0);
  }
}
