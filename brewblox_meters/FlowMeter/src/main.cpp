// https://www.iotdesignpro.com/projects/iot-based-water-flow-meter

#include <Arduino.h>
#include <ArduinoJson.h>

#define SENSOR IO26

long currentMillis = 0;
long previousMillis = 0;
int interval = 1000;

float calibrationFactor = 9.93;
volatile byte pulseCount;
byte pulse1Sec = 0;
float flowRate;
unsigned int flowMilliLitres;
unsigned long totalMilliLitres;

// void ICACHE_RAM_ATTR pulseCounter()  // use for ESP8266
void IRAM_ATTR pulseCounter() // may be only for ESP32
{
    pulseCount++;
}

void setup()
{
    Serial.begin(115200);
    pinMode(SENSOR, INPUT_PULLUP);
    pulseCount = 0;
    flowRate = 0.0;
    flowMilliLitres = 0;
    totalMilliLitres = 0;
    previousMillis = 0;
    attachInterrupt(digitalPinToInterrupt(SENSOR), pulseCounter, FALLING);
}

void loop()
{

    currentMillis = millis();
    StaticJsonDocument<100> doc;
    if (currentMillis - previousMillis > interval)
    {
        detachInterrupt(digitalPinToInterrupt(SENSOR));
        pulse1Sec = pulseCount;
        pulseCount = 0;
        flowRate = ((1000.0 / (millis() - previousMillis)) * pulse1Sec) / calibrationFactor;
        previousMillis = millis();
        flowMilliLitres = (flowRate / 60.0) * 1000.0;
        totalMilliLitres += flowMilliLitres;

        // Json Output
        doc["sensor"] = "flow";
        doc["L/min"] = flowRate;
        doc["total mL"] = totalMilliLitres;
        doc["total L"] = totalMilliLitres / 1000.0;

        serializeJsonPretty(doc, Serial);
        Serial.println("");
    }
    attachInterrupt(digitalPinToInterrupt(SENSOR), pulseCounter, FALLING);
}