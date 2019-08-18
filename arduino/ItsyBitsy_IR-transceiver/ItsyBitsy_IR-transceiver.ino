/*
* Go Faster-Faster (GF2) transceiver
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Wire.h>
#include <pins_arduino.h>

RF24 radio(3, 2); // CE, CSN

#define BATTSENSE A0  // https://www.arduino.cc/en/Tutorial/AnalogInput
#define PIEZO1 A1
#define PIEZO2 A3
#define IRSENSE 7
#define LED1 9
#define LED2 10
#define LED3 11
#define LED4 12
#define LED5 13

// Utilize buzzer and LEDs at startup to aid testing, then
// go dark & silent to conserve battery power. This mode is
// active for TESTMODE_MS milliseconds.
#define TESTMODE_MS 300000

// Dead-man switch for beam-break detection. Sensor should be
// pulsing at about 95 Hz while beam is unbroken.
#define CUTOFF_ALARM_MS 15

volatile unsigned long lastVisiblePulse = 0;
volatile int irstate = HIGH;
bool beamBroken = false;
bool lastBeamState = beamBroken;
bool saturated = false;

void ledwalk() {
  digitalWrite(LED1, HIGH);
  delay(300);
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, HIGH);
  delay(300);
  digitalWrite(LED2, LOW);
  digitalWrite(LED3, HIGH);
  delay(300);
  digitalWrite(LED3, LOW);
  digitalWrite(LED4, HIGH);
  delay(300);
  digitalWrite(LED4, LOW);
  digitalWrite(LED5, HIGH);
  delay(300);
  digitalWrite(LED5, LOW);
}

void piezoBeep(int duration) {
  for (int i=0; i<duration*5; i++) {
    digitalWrite(PIEZO1, LOW);
    digitalWrite(PIEZO2, HIGH);
    delayMicroseconds(100);
    digitalWrite(PIEZO1, HIGH);
    digitalWrite(PIEZO2, LOW);
    delayMicroseconds(100);
  }
}

void showBatteryLevel() {
  int battvoltage = analogRead(BATTSENSE);

  /*
  if (battvoltage < 10) {
    digitalWrite(LED1, HIGH);
  }
  else if (battvoltage > 1000) {
    digitalWrite(LED5, HIGH);
  }
  delay(1000);
  digitalWrite(LED1, LOW);
  digitalWrite(LED5, LOW);
  delay(1000);
  */


  /* Normal scale for analogRead means max reading (1023) == 3.3 VDC.
     But we're reading through a 50% resistor matrix, so 1023 == 6.6 VDC.
     Therefore for a lithium-ion cell, our "acceptable" range is:
        574 == 3.7 VDC
        652 == 4.2 VDC  */

  //if ((battvoltage < 543) || (battvoltage > 667)) {  // Outside normal params
  if ((battvoltage < 543) || (battvoltage > 1020)) {  // Outside normal params
    for (int i=0; i<3; i++) {
      digitalWrite(LED2, HIGH);
      digitalWrite(LED4, HIGH);
      piezoBeep(400);
      digitalWrite(LED2, LOW);
      digitalWrite(LED4, LOW);
      delay(400);
    }
  }
  else if (battvoltage < 574) { // < 3.7 VDC: Crit low
    for (int i=0; i<5; i++) {
      digitalWrite(LED1, HIGH);
      piezoBeep(200);
      digitalWrite(LED1, LOW);
      delay(200);
    }
  }
  else { // 3.7 - 4.3 VDC: Normal
    digitalWrite(LED1, HIGH);                        // >= 3.7 VDC
    /*
    if (battvoltage > 590) digitalWrite(LED2, HIGH); // >= 3.8 VDC
    if (battvoltage > 606) digitalWrite(LED3, HIGH); // >= 3.9 VDC
    if (battvoltage > 622) digitalWrite(LED4, HIGH); // >= 4.0 VDC
    if (battvoltage > 638) digitalWrite(LED5, HIGH); // >= 4.1 VDC
    */
    if (battvoltage > 660) digitalWrite(LED2, HIGH); // >= 3.8 VDC
    if (battvoltage > 665) digitalWrite(LED3, HIGH); // >= 3.9 VDC
    if (battvoltage > 670) digitalWrite(LED4, HIGH); // >= 4.0 VDC
    if (battvoltage > 675) digitalWrite(LED5, HIGH); // >= 4.1 VDC
  }
  delay(1000);
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);
  digitalWrite(LED3, LOW);
  digitalWrite(LED4, LOW);
  digitalWrite(LED5, LOW);
}

void setupIRint() {
  pinMode(IRSENSE, INPUT_PULLUP);
  digitalWrite(IRSENSE, HIGH);
  // Enable pin-change interrupt on a given pin
  attachInterrupt(digitalPinToInterrupt(IRSENSE), irIntFire, CHANGE);
}

// Pin-change handler for digital pins 0 - 7
void irIntFire() {
  irstate = digitalRead(IRSENSE);
  if (irstate == LOW) {
    lastVisiblePulse = millis();
  }
}

void radioBroadcast(bool broken) {
  radio.stopListening();
  // Sentence construction: [Ir unit][unit#][
  char xmit[3];
  xmit[0] = 'I';
  xmit[1] = '1'; // Different value for every transceiver
  if (broken) {
    xmit[2] = '1';
  }
  else {
    xmit[2] = '0';
  }

  radio.write(&xmit, sizeof(xmit));
  radio.startListening();
}

void setup() {
  radio.begin();
  radio.openWritingPipe(0xE0E0E0E0E0);
  // Library docs recommend using a different pipe for RX
  radio.openReadingPipe(1, 0xE1E1E1E1E2);
  radio.setPALevel(RF24_PA_MAX);
  radio.enableDynamicPayloads();
  radio.startListening();

  setupIRint();

  pinMode(LED1, OUTPUT); digitalWrite(LED1, LOW);
  pinMode(LED2, OUTPUT); digitalWrite(LED2, LOW);
  pinMode(LED3, OUTPUT); digitalWrite(LED3, LOW);
  pinMode(LED4, OUTPUT); digitalWrite(LED4, LOW);
  pinMode(LED5, OUTPUT); digitalWrite(LED5, LOW);
  pinMode(BATTSENSE, INPUT);
  pinMode(PIEZO1, OUTPUT);
  pinMode(PIEZO2, OUTPUT);

  ledwalk();
  delay(1000);

  showBatteryLevel();
  delay(1000);

}

void loop() {
  // We should be seeing falling-edge (high->low) signal changes every 10.5 ms
  if (millis() - lastVisiblePulse > CUTOFF_ALARM_MS) {
    if (irstate == HIGH) {
      saturated = false;
      if (! beamBroken) {
        // Emitter's been missing for a while (and this is the first
        // time we're reacting to it)
        beamBroken = true;
        /* BEAM BROKEN! WOOP WOOP WOOP DING DING! */
      }
    } else {
      beamBroken = false;
      // Emitter's saturating the eye. That's no good either.
      // Use a higher threshold for this, because it seems touchy
      // in testing.
      if (millis() - lastVisiblePulse > (CUTOFF_ALARM_MS * 2)) saturated = true;
    }
  } else {
    /* Reset the alarm */
    beamBroken = false;
    saturated = false;
  }

  if ((saturated) && (millis() < TESTMODE_MS)) {
    // Throw a warning (keeps firing while condition is true)
    digitalWrite(LED1, HIGH);
    digitalWrite(LED5, HIGH);
    piezoBeep(80);
    delay(100);
  } else {
    digitalWrite(LED1, LOW);
    digitalWrite(LED5, LOW);
  }

  if (lastBeamState != beamBroken) {
    radioBroadcast(beamBroken);
    if (beamBroken) {
      if (millis() < TESTMODE_MS) {
        digitalWrite(LED3, HIGH);
        piezoBeep(800);
      }
    } else {
      digitalWrite(LED3, LOW);
    }
    lastBeamState = beamBroken;
  }
}

