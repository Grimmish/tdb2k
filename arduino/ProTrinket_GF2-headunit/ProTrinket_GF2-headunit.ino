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

#define BUT_G 3
#define BUT_R 4

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

  pinMode(BUT_G, INPUT_PULLUP);
  digitalWrite(BUT_G, HIGH);
  pinMode(BUT_R, INPUT_PULLUP);
  digitalWrite(BUT_R, HIGH);

  matrix.begin(0x70);
  matrix.println();
  matrix.writeDisplay();
}

void setRGBLED(int r, int g, int b) {
  digitalWrite(RGB_R, r);
  digitalWrite(RGB_B, b);
  digitalWrite(RGB_G, g);
}

void loop() {
  if (digitalRead(BUT_R) == LOW) {
    ctr--;
    matrix.println(ctr);
    matrix.writeDisplay();
  }
  if (digitalRead(BUT_G) == LOW) {
    ctr++;
    matrix.println(ctr);
    matrix.writeDisplay();
  }

  while (radio.available()) {
    uint8_t len = radio.getDynamicPayloadSize();
    if (!len) {
      continue;
    }
    String phrase;

    // Need to clear the array before reading in a new value
    // to reset the "end-of-string" marker
    memset(receive_payload, 0, sizeof receive_payload);
    radio.read(receive_payload, len);
    switch (receive_payload[0]) {
      case 'D':
        // Write something to the 7-segment display
        phrase = String(receive_payload);
        if (phrase.indexOf('.') == -1) {
          // No decimal; assume integer
          ctr = phrase.substring(1).toInt();
          matrix.println(ctr);
          matrix.writeDisplay();
        }
        else {
          // Looks like a decimal
          //matrix.println(phrase.substring(1).toDouble());
          matrix.print(0xBEEF, HEX);
          matrix.writeDisplay();
        }
        
        break;
      case 'L':
        // Set a color on the LED
        switch (receive_payload[1]) {
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
        break;
      }
    }
    //ctr++;
    //matrix.println(ctr);
    //matrix.writeDisplay();
  }

  /*
  const char text[] = "PING!";
  radio.write(&text, sizeof(text));
  delay(400);
  */
}

