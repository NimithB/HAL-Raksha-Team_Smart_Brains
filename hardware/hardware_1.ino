#include <Wire.h>
#include <U8g2lib.h>

// GPIO Pin Definitions
#define TILT1_PIN 14      // GPIO14 (D5) - Tilt1 Sensor
#define TILT2_PIN  3      // GPIO3 (D9) - Tilt2 Sensor (Updated)
#define BUZZER_PIN 15     // GPIO15 (D8) - Buzzer
#define VIBRATION_PIN 16  // GPIO16 (D0)
#define HEARTBEAT_PIN A0  // Analog pin (A0)
#define TOUCH_PIN 12      // GPIO12 (D6)

// OLED Display Pins
#define OLED_SDA 4  // GPIO4 (D2)
#define OLED_SCL 5  // GPIO5 (D1)

// Initialize OLED Display
U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

void setup() {
  Serial.begin(115200);

  // Set pin modes
  pinMode(TILT1_PIN, INPUT_PULLUP);  // Tilt1 as input
  pinMode(TILT2_PIN, INPUT_PULLUP);  // Tilt2 (GPIO3/RX) as input
  pinMode(VIBRATION_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(TOUCH_PIN, INPUT);

  // Start I2C communication for OLED
  Wire.begin(OLED_SDA, OLED_SCL);
  u8g2.begin();
  u8g2.clearBuffer();
}

void loop() {
  // Read sensor values
  int tilt1State = digitalRead(TILT1_PIN);
  int tilt2State = digitalRead(TILT2_PIN);
  int touchState = digitalRead(TOUCH_PIN);
  int heartbeatValue = analogRead(HEARTBEAT_PIN);

  // Debugging Tilt2 in Serial Monitor
  Serial.print("Tilt1: "); Serial.print(tilt1State == LOW ? "OFF" : "ON");
  Serial.print(" | Tilt2: "); Serial.print(tilt2State == LOW ? "OFF" : "ON");
  Serial.print(" | Touch: "); Serial.print(touchState == HIGH ? "YES" : "NO");
  Serial.print(" | Heartbeat: "); Serial.println(heartbeatValue);

  // If both Tilt1 and Tilt2 are OFF, activate the buzzer for 3 seconds
  if (tilt1State == HIGH && tilt2State == HIGH) {
    digitalWrite(BUZZER_PIN, HIGH);  // Turn on buzzer
    delay(1000);  // Wait for 3 seconds
    digitalWrite(BUZZER_PIN, LOW);   // Turn off buzzer
  }

  // Activate vibration motor if touch sensor is pressed
  digitalWrite(VIBRATION_PIN, touchState == HIGH ? HIGH : LOW);

  // Display values on OLED
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  
  u8g2.setCursor(0, 10);
  u8g2.print("Tilt1: "); u8g2.print(tilt1State == LOW ? "OFF" : "ON");
  
  u8g2.setCursor(0, 20);
  u8g2.print("Tilt2: "); u8g2.print(tilt2State == LOW ? "OFF" : "ON");

  u8g2.setCursor(0, 30);
  u8g2.print("Touch: "); u8g2.print(touchState == HIGH ? "YES" : "NO");

  u8g2.setCursor(70, 10);
  u8g2.print("HB: "); u8g2.print(heartbeatValue);

  u8g2.sendBuffer();

  delay(500);
}
