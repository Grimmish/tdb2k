/*
* Arduino Wireless Communication Tutorial
*     Example 1 - Transmitter Code
*                
* by Dejan Nedelkovski, www.HowToMechatronics.com
* 
* Library: TMRh20/RF24, https://github.com/tmrh20/RF24/
*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(6, 8); // CE, CSN
const byte address[6] = "00001";
void setup() {
	radio.begin();
	//radio.openWritingPipe(address);
	radio.openWritingPipe(1);
	radio.setPALevel(RF24_PA_MAX);
	radio.enableDynamicPayloads();
	radio.stopListening();

	pinMode(10, OUTPUT);
	digitalWrite(10, LOW);
}
void loop() {
	const char text[] = "PING!";
	radio.write(&text, sizeof(text));
	
	digitalWrite(10, HIGH);
	delay(10);
	digitalWrite(10, LOW);
	delay(590);
}
