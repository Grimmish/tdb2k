/****************************************************
 * Ben's library for a serial-wireless control module
 *
 * **************************************************/
#ifndef BMA_Headunit_h
#define BMA_Headunit_h

#include <Stream.h>
#include <SoftwareSerial.h>

class BMA_Headunit : public SoftwareSerial {
	public:
		BMA_Headunit(uint8_t receivePin, uint8_t transmitPin) : SoftwareSerial(receivePin, transmitPin) {};

		bool ping();

		
		void printInt(int n);
		void printTenths(int n, bool zeropadded);
		void printString(char s[]);
		// Send "points" as a 4-bit register indicating which decimal points should be visible
		//void printIntWithPoint(int n, uint8_t points);
		//void printString(char[] s);

	private:
		// Nothing yet
};

#endif
