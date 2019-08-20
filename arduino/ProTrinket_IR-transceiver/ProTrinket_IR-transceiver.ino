/*
* IR Transceiver
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Wire.h>
#include <pins_arduino.h>

RF24 radio(10, 5); // CE, CSN

#define RGB_R 3
#define RGB_G 5
#define RGB_B 6
#define LED 3
#define IR_EYE 4

unsigned long lastVisiblePulse = 0;
int lastState;
bool beamBroken = false;

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

  lastState = digitalRead(IR_EYE);
}

void loop() {
  int state = digitalRead(IR_EYE);
  if (lastState != state) {
    if (state == LOW) {  /* IR eye is active-low */
      lastVisiblePulse = millis(); 
    }
    lastState = state;
  }

  // We should be seeing high-low emitter cycles every 10.5 ms
  if (millis() - lastVisiblePulse > 15) {
    if (state == HIGH) {
      if (! beamBroken) {
        // Emitter's been missing for a while (and htis is the first
        // time we're reacting to it)
        beamBroken = true;
        /* BEAM BROKEN! WOOP WOOP WOOP DING DING! */
      }
    } else {
      // Emitter's saturating the eye. That's no good either.
      /* Throw a warning LED */
    }
  } else {
    /* Reset the alarm */
    beamBroken = false;
  }

  // FIXME Do something prettier
  if (beamBroken) {
    digitalWrite(LED, HIGH);
  } else {
    digitalWrite(LED, LOW);
  }
}

