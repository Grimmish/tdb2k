/*
* Go Faster-Faster (GF2) headunit
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Wire.h>
#include "BMA_Adafruit_LEDBackpack.h"

BMA_Adafruit_7segment matrix = BMA_Adafruit_7segment();

RF24 radio(5, 6); // CE, CSN

#define RGB_R 10
#define RGB_G 9
#define RGB_B 8

#define RESETBUTTON 4

int ctr = 0;
char receive_payload[33]; // Need +1 byte for terminating char

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

  pinMode(RESETBUTTON, INPUT_PULLUP);
  digitalWrite(RESETBUTTON, HIGH);

  matrix.begin(0x70);
  matrix.println();
  matrix.writeDisplay();
}
void loop() {
  if (digitalRead(RESETBUTTON) == LOW) {
    ctr = 0;
    matrix.println(ctr);
    matrix.writeDisplay();
  }
  while (radio.available()) {
    uint8_t len = radio.getDynamicPayloadSize();
    if (!len) {
      continue;
    }

    radio.read(receive_payload, len);
    switch (receive_payload[0]) {
      case 'R':
        digitalWrite(RGB_R, HIGH);
        digitalWrite(RGB_G, LOW);
        digitalWrite(RGB_B, LOW);
        break;
      case 'G':
        digitalWrite(RGB_R, LOW);
        digitalWrite(RGB_G, HIGH);
        digitalWrite(RGB_B, LOW);
        break;
      case 'B':
        digitalWrite(RGB_R, LOW);
        digitalWrite(RGB_G, LOW);
        digitalWrite(RGB_B, HIGH);
        break;
      case 'Y':
        digitalWrite(RGB_R, HIGH);
        digitalWrite(RGB_G, HIGH);
        digitalWrite(RGB_B, LOW);
        break;
      case 'P':
        digitalWrite(RGB_R, HIGH);
        digitalWrite(RGB_G, LOW);
        digitalWrite(RGB_B, HIGH);
        break;
      case 'C':
        digitalWrite(RGB_R, LOW);
        digitalWrite(RGB_G, HIGH);
        digitalWrite(RGB_B, HIGH);
        break;
      case 'W':
        digitalWrite(RGB_R, HIGH);
        digitalWrite(RGB_G, HIGH);
        digitalWrite(RGB_B, HIGH);
        break;
      default:
        digitalWrite(RGB_R, LOW);
        digitalWrite(RGB_G, LOW);
        digitalWrite(RGB_B, LOW);
        break;
    }

    ctr++;
    matrix.println(ctr);
    matrix.writeDisplay();
  }

  /*
  const char text[] = "PING!";
  radio.write(&text, sizeof(text));
  delay(400);
  */
}
