/*
  TDB2k headunit - Adafruit ItsyBitsy MCU
*/
#include <SPI.h>
#include <Wire.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <pins_arduino.h>
#include "BMA_Dual8x8.h"

#define DELAYCONST 30

//FIXME
#define BTN_G 3
#define BTN_R 4

#define DOWN LOW
#define IP HIGH

RF24 radio(5, 6); // CE, CSN
BMA_Dual8x8 scr = BMA_Dual8x8();

char receive_payload[33]; // Need +1 byte for terminating char

volatile unsigned long lastISR = 0;
// The BTN_G/BTN_R constants will be used as indexes for this array
volatile int buttonState[5] = {UP, UP, UP, UP, UP};
volatile int buttonChanged = 0;

void setupButton(byte pin) {
  pinMode(pin, INPUT_PULLUP);
  digitalWrite(pin, HIGH);
  // Enable pin-change interrupt on a given pin
  *digitalPinToPCMSK(pin) |= bit (digitalPinToPCMSKbit(pin));  // enable pin
  PCIFR  |= bit (digitalPinToPCICRbit(pin)); // clear any outstanding interrupt
  PCICR  |= bit (digitalPinToPCICRbit(pin)); // enable interrupt for the group
}

void checkButtonStates() {
  if (micros() - lastISR > 50000) {
    // Probably not a bounce.
    if (buttonState[BTN_R] != digitalRead(BTN_R)) {
      buttonState[BTN_R] = digitalRead(BTN_R);
      buttonChanged |= 1<<BTN_R;
      lastISR = micros();
    }
    if (buttonState[BTN_G] != digitalRead(BTN_G)) {
      buttonState[BTN_G] = digitalRead(BTN_G);
      buttonChanged |= 1<<BTN_G;
      lastISR = micros();
    }
  }
}

void radioSendButton() {
  radio.stopListening();
  // Sentence construction: [Button][button#][state: 1=press 0=release]
  char xmit[3];
  xmit[0] = 'B';
  if (buttonChanged & 1<<BTN_R) {
    xmit[1] = '1';
    if (buttonState[BTN_R] == DOWN) {
      xmit[2] = '1';
    } else {
      xmit[2] = '0';
    }
    buttonChanged &= ~(1<<BTN_R);
  }
  if (buttonChanged & 1<<BTN_G) {
    xmit[1] = '2';
    if (buttonState[BTN_G] == DOWN) {
      xmit[2] = '1';
    } else {
      xmit[2] = '0';
    }
    buttonChanged &= ~(1<<BTN_G);
  }
  radio.write(&xmit, sizeof(xmit));
  radio.startListening();
}

void applyBitmapSentence(char sentence[]) {
  switch (sentence[1]) {
    /*
    Sentence is in bytes: [ Domain, Sub-domain, payload (16) ]
    The payload is 8-bit "strips" of horizontal display data: 1st-row-left,
    1st-row-right, 2nd-row-left, etc.
    BUT, the 16x8 display buffer is in rows [ 1st-row, 2nd-row, 3rd-row, etc ].
    Thus each pair of payload bytes must be joined to form a complete row. In
    addition, we always need to fast-forward past the first 2 bytes of the
    sentence.
    */
    case 'R':
      for (int i=0; i<8; i++) {
        scr.redbuffer[i] = sentence[2+(i*2)]<<8 | sentence[2+(i*2)+1];
      }
      break;
    case 'G':
      for (int i=0; i<8; i++) {
        scr.greenbuffer[i] = sentence[2+(i*2)]<<8 | sentence[2+(i*2)+1];
      }
      break;
  }
}

// Pin-change handler for digital pins 0 - 7
ISR (PCINT2_vect) {
  checkButtonStates();
}

/*
###############################################################
####
####    SETUP
####
###############################################################
*/
void setup() {
  radio.begin();
  radio.openWritingPipe(0xE0E0E0E0E0);
  radio.openReadingPipe(1, 0xE1E1E1E1E1);
  radio.setPALevel(RF24_PA_MAX);
  radio.enableDynamicPayloads();
  radio.startListening();

  setupButton(BTN_G);
  setupButton(BTN_R);

  scr.begin();
}

/*
###############################################################
###############################################################
####
####    MAIN
####
###############################################################
###############################################################
*/
void loop() {
  checkButtonStates(); // Call in main loop too, in case an INT is missed

  if (buttonChanged) {
    radioSendButton();
  }

  while (radio.available()) {
    uint8_t len = radio.getDynamicPayloadSize();
    if (!len) {
      continue;
    }

    // memset to wipe out previous "end-of-string" marker
    memset(receive_payload, 0, sizeof receive_payload);
    radio.read(receive_payload, len);
    switch (receive_payload[0]) {
      case 'D':
        // Write something to the display
        applyBitmapSentence(receive_payload);
        scr.writeDisplay();
        break;
    }
  }
}
