/*
* Go Faster-Faster (GF2) headunit
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Wire.h>
#include <pins_arduino.h>


RF24 radio(10, 5); // CE, CSN

#define LED 3
#define IR_EYE 4

void setup() {
  radio.begin();
  radio.openWritingPipe(0xE0E0E0E0E0);
  // Library docs recommend using a different pipe for RX
  radio.openReadingPipe(1, 0xE1E1E1E1E2);
  radio.setPALevel(RF24_PA_MAX);
  radio.enableDynamicPayloads();
  //radio.startListening();

  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);
  pinMode(IR_EYE, INPUT_PULLUP);
  digitalWrite(IR_EYE, HIGH);

  // Blink to confirm readiness
  for (int i=0; i<3; i++) {
    digitalWrite(LED, HIGH);
    delay(100);
    digitalWrite(LED, LOW);
    delay(100);
  }
  delay(400);
}

void loop() {
  // FIXME Add low-batt indicator
  if (digitalRead(IR_EYE)) {
    digitalWrite(LED, LOW);
  } else {
    digitalWrite(LED, HIGH);
  }
}

