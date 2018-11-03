/*
* Go Faster-Faster (GF2) headunit
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Wire.h>
#include <pins_arduino.h>
#include "BMA_Adafruit_LEDBackpack.h"

BMA_Adafruit_7segment matrix = BMA_Adafruit_7segment();

RF24 radio(5, 6); // CE, CSN

#define RGB_R 10
#define RGB_G 9
#define RGB_B 8

#define BUT_G 3
#define BUT_R 4

#define DOWN LOW
#define UP HIGH

int ctr = 0;
char receive_payload[33]; // Need +1 byte for terminating char

volatile unsigned long lastISR = 0;
volatile int buttonState[5] = {UP, UP, UP, UP, UP};
volatile byte buttonChanged = 0;

void setupButton(byte pin) {
  pinMode(pin, INPUT_PULLUP);
  digitalWrite(pin, HIGH);
  // Enable pin-change interrupt on a given pin
  *digitalPinToPCMSK(pin) |= bit (digitalPinToPCMSKbit(pin));  // enable pin
  PCIFR  |= bit (digitalPinToPCICRbit(pin)); // clear any outstanding interrupt
  PCICR  |= bit (digitalPinToPCICRbit(pin)); // enable interrupt for the group
}

void setup() {
  radio.begin();
  //radio.openWritingPipe(address);
  radio.openWritingPipe(0xE0E0E0E0E0);
  // Library docs recommend using a different pipe for RX
  radio.openReadingPipe(1, 0xE1E1E1E1E1);
  radio.setPALevel(RF24_PA_MAX);
  radio.enableDynamicPayloads();
  radio.startListening();

  pinMode(RGB_R, OUTPUT);
  digitalWrite(RGB_R, LOW);
  pinMode(RGB_G, OUTPUT);
  digitalWrite(RGB_G, LOW);
  pinMode(RGB_B, OUTPUT);
  digitalWrite(RGB_B, LOW);

  setupButton(BUT_G);
  setupButton(BUT_R);

  matrix.begin(0x70);
  matrix.println(ctr);
  matrix.writeDisplay();
}

void checkButtonStates() {
  if (micros() - lastISR > 50000) {
    // Probably not a bounce.
    if (buttonState[BUT_R] != digitalRead(BUT_R)) {
      buttonState[BUT_R] = digitalRead(BUT_R);
      buttonChanged |= 1<<BUT_R;
      lastISR = micros();
    }
	if (buttonState[BUT_G] != digitalRead(BUT_G)) {
      buttonState[BUT_G] = digitalRead(BUT_G);
      buttonChanged |= 1<<BUT_G;
      lastISR = micros();
    }
  }
}

// Pin-change handler for digital pins 0 - 7
ISR (PCINT2_vect) {
  checkButtonStates();
}

void setRGBLED(int r, int g, int b) {
  digitalWrite(RGB_R, r);
  digitalWrite(RGB_B, b);
  digitalWrite(RGB_G, g);
}

void setLEDcolor(char c) {
  switch (c) {
    case 'R':
      setRGBLED(HIGH, LOW, LOW); break;
    case 'G':
      setRGBLED(LOW, HIGH, LOW); break;
    case 'B':
      setRGBLED(LOW, LOW, HIGH); break;
    case 'Y':
      setRGBLED(HIGH, HIGH, LOW); break;
    case 'P':
      setRGBLED(HIGH, LOW, HIGH); break;
    case 'C':
      setRGBLED(LOW, HIGH, HIGH); break;
    case 'W':
      setRGBLED(HIGH, HIGH, HIGH); break;
    default:
      setRGBLED(LOW, LOW, LOW); break;
  }
}

void loop() {
  checkButtonStates(); // Call this in the main loop too, for INT misses
  if (buttonChanged) {
    radio.stopListening();
    // Sentence construction: [Button][button#][state: 1=press 0=release]
    char xmit[3];
    xmit[0] = 'B';
    if (buttonChanged & 1<<BUT_R) {
      xmit[1] = '1';
      if (buttonState[BUT_R] == DOWN) {
        xmit[2] = '1';
      } else {
        xmit[2] = '0';
      }
      buttonChanged &= ~(1<<BUT_R);
    }
    if (buttonChanged & 1<<BUT_G) {
      xmit[1] = '2';
      if (buttonState[BUT_G] == DOWN) {
        xmit[2] = '1';
      } else {
        xmit[2] = '0';
      }
      buttonChanged &= ~(1<<BUT_G);
    }
    radio.write(&xmit, sizeof(xmit));
    radio.startListening();
  }

  while (radio.available()) {
    uint8_t len = radio.getDynamicPayloadSize();
    if (!len) {
      continue;
    }
    String phrase;

    // memset to wipe out previous "end-of-string" marker
    memset(receive_payload, 0, sizeof receive_payload);
    radio.read(receive_payload, len);
    switch (receive_payload[0]) {
      case 'D':
        // Write something to the 7-segment display
        phrase = String(receive_payload);
        if (phrase.indexOf('.') > -1) { // Decimal point? Assume float
          matrix.println(phrase.substring(1).toFloat(), 1);
        } else { // Integer
          matrix.println(phrase.substring(1).toInt());
        }
        matrix.writeDisplay();
        break;
      case 'L':
        // Set a color on the LED
        setLEDcolor(receive_payload[1]);
        break;
    }
  }
}

