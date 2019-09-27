/*
  TDB2k headunit - Adafruit ItsyBitsy MCU
*/
#include <SPI.h>
#include <Wire.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <pins_arduino.h>
#include "BMA_Dual8x8.h"

#define BTN_G 11
#define BTN_R 12
#define BTN_Y 13

// How much radio silence before we start pinging home?
#define PINGTHRESH 1000000
// How much radio silence before we throw a visual warning?
#define WARNTHRESH 3000000

#define DOWN LOW
#define UP HIGH

#define CALL '0'
#define RESPONSE '1'

RF24 radio(7, 5); // CE, CSN
BMA_Dual8x8 scr = BMA_Dual8x8();

char receive_payload[33]; // Need +1 byte for terminating char

volatile unsigned long lastISR = 0;
volatile unsigned long lastcontact = 0;
volatile unsigned long lastpingcall = 0;
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
    if (buttonState[BTN_Y] != digitalRead(BTN_Y)) {
      buttonState[BTN_Y] = digitalRead(BTN_Y);
      buttonChanged |= 1<<BTN_Y;
      lastISR = micros();
    }
  }
}

void radioSendPing(char callorresponse) {
  radio.stopListening();
  // Sentence construction: [Ping][Device ID][0(call) or 1(response)]
  char xmit[3];
  xmit[0] = 'P';
  xmit[1] = '1';
  xmit[2] = callorresponse;
  radio.write(&xmit, sizeof(xmit));
  lastpingcall = micros();
  radio.startListening();
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
  if (buttonChanged & 1<<BTN_Y) {
    xmit[1] = '3';
    if (buttonState[BTN_Y] == DOWN) {
      xmit[2] = '1';
    } else {
      xmit[2] = '0';
    }
    buttonChanged &= ~(1<<BTN_Y);
  }
  radio.write(&xmit, sizeof(xmit));
  radio.startListening();
}

void tricolorWipe() {
  int timestep = 20;
  for (int z=15; z>=0; z--) {
    for (int x=0; x<8; x++) { scr.greenbuffer[x] |= 1<<z; }
    scr.writeDisplay();
    delay(timestep);
  }
  for (int z=15; z>=0; z--) {
    for (int x=0; x<8; x++) { scr.redbuffer[x] |= 1<<z; }
    scr.writeDisplay();
    delay(timestep);
  }
  for (int z=15; z>=0; z--) {
    for (int x=0; x<8; x++) { scr.greenbuffer[x] &= ~(1<<z); }
    scr.writeDisplay();
    delay(timestep);
  }
  for (int z=15; z>=0; z--) {
    for (int x=0; x<8; x++) { scr.redbuffer[x] &= ~(1<<z); }
    scr.writeDisplay();
    delay(timestep);
  }
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
    case 'b':
      scr.setBrightness(sentence[2]);
      break;
    case 'R':
      for (int i=0; i<8; i++) {
        scr.redbuffer[i] = sentence[2+(i*2)]<<8 | (sentence[2+(i*2)+1] & 0xFF);
      }
      break;
    case 'G':
      for (int i=0; i<8; i++) {
        //scr.greenbuffer[i] = sentence[2+(i*2)]<<8 | sentence[2+(i*2)+1];
        scr.greenbuffer[i] = sentence[2+(i*2)]<<8 | (sentence[2+(i*2)+1] & 0xFF);
      }
      break;
  }
}

void handlePing(char sentence[]) {
  switch (sentence[1]) {
    /*
    Ping sentences are either 'P0' (call) or 'P1' (response).
    */
    case CALL:
      // We must answer
      radioSendPing(RESPONSE);
      break;
    case RESPONSE:
      /*
      Hooray, we're not alone! We don't need to actually do anything here, since
      every incoming message automatically bumps the lastcontact counter.
      */
      break;
  }
}

// Pin-change handler for digital pins 0 - 7
ISR (PCINT0_vect) {
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
  // The last digit of the RX pipe is effectively this device's unique ID
  radio.openReadingPipe(1, 0xE1E1E1E1E1);
  radio.setPALevel(RF24_PA_MAX);
  radio.enableDynamicPayloads();
  radio.startListening();

  setupButton(BTN_R);
  setupButton(BTN_G);
  setupButton(BTN_Y);

  scr.begin();
  tricolorWipe();
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

  if (micros() - lastcontact > PINGTHRESH && micros() - lastpingcall > PINGTHRESH)  {
    // Haven't heard from home base in a while. Ping?
    radioSendPing(CALL);
  }

  if (micros() - lastcontact > WARNTHRESH) {
    // Haven't heard from home in a LONG while. Warn the user!
    uint16_t questionmark [] = { 0x0000,0x0ba0,0x28a8,0xa9aa,0xa92a,0x2828,0x0920,0x0000 };
    for (int i=0; i<8; i++) {
      scr.greenbuffer[i] = 0;
      scr.redbuffer[i] = questionmark[i];
    }
    scr.writeDisplay();
  }

  while (radio.available()) {
    uint8_t len = radio.getDynamicPayloadSize();
    if (!len) {
      continue;
    }
    lastcontact = micros();

    // memset to wipe out previous "end-of-string" marker
    memset(receive_payload, 0, sizeof receive_payload);
    radio.read(receive_payload, len);
    switch (receive_payload[0]) {
      case 'D':
        // Write something to the display
        applyBitmapSentence(receive_payload);
        scr.writeDisplay();
        break;
      case 'P':
        // Incoming ping (call or response)
        handlePing(receive_payload);
        break;
    }
  }
}
