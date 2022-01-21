#include "Arduino.h"

//#define Hall_Sensor A0 // A0 used with analog output, D2 with digital output
int flowMeterPin = 26;
int sensorInterrupt = 26;
int ledPin = 2;

float calibrationFactor = 9.93;

//volatile int flowFrequency;
volatile byte pulseCount; // Here you can store both values, the Val2 can be boolean

float flowRate;
unsigned int flowMilliLitres;
unsigned long totalMilliLitres;
unsigned long totalpulseCount;

unsigned long oldTime;

void pulseCounter()
{
    pulseCount++;
}

void setup()
{
    Serial.begin(115200);
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, HIGH);

    pinMode(flowMeterPin, INPUT_PULLUP);
    sei();
    pulseCount       = 0;
    flowRate         = 0.0;
    flowMilliLitres  = 0;
    totalMilliLitres = 0;

    // The Hall-effect sensor is connected to pin 2 which uses interrupt 0.
    // Configured to trigger on a FALLING state change (transition from HIGH
    // state to LOW state)
    //attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}

void loop()
{
    if((millis() - oldTime) > 1000) 
    {
        //detachInterrupt(sensorInterrupt);
        flowRate = ((1000 / (millis() - oldTime)) * pulseCount) / calibrationFactor;
        oldTime = millis();
        flowMilliLitres = (flowRate / 60) * 1000;
        totalMilliLitres += flowMilliLitres;

        Serial.println(analogReadMilliVolts(flowMeterPin));
        Serial.println(pulseCount);
        Serial.print(flowRate);
        Serial.println(" L/min");


        Serial.print("Flow rate: ");
        Serial.println(flowRate); // Print the ionteger part of the variable Serial.print("L/min");
    
        // Print the cumulative total of litres flowed since starting 
        Serial.print("Output Liquid Quantity: "); 
        Serial.print(totalMilliLitres);
        Serial.println("mL");
        
        pulseCount = 0;
        //attachInterrupt(sensorInterrupt, pulseCounter, FALLING);    
    }
}