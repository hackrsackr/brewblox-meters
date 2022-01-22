#include "Arduino.h"
#include "ArduinoJson.h"
#include "EspMQTTClient.h"

#include "secrets.h"

int PORT = 80;
char HOST[] = "192.168.1.2";
char CLIENT_ID[] = "flow-meters";
char TOPIC[] = "brewcast/history/flow-meters";

EspMQTTClient client(_SSID, _PASS, HOST);
String message = "{\"key\": \"flow-meters\",\"data\": 48.75}";

void onConnectionEstablished()
{
    client.publish(TOPIC, message);
}

void connect() {
  Serial.print("checking wifi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }

  Serial.print("\nconnecting...");
  while (!client.isConnected()) {
    Serial.print(".");
    delay(1000);
  }
}


void setup()
{
    Serial.begin(115200);
    WiFi.begin(_SSID, _PASS);
}

void loop()
{
    client.loop();
    delay(10);

    if (!client.isConnected())
    {
        connect();
    }

    while (client.isConnected()){
        client.publish(TOPIC, message);
        Serial.println(message);
        delay(5000);
    }
}