#include "Arduino.h"
#include "WiFi.h"
#include "MQTT.h"
#include "EspMQTTClient.h"

#include "secrets.h"

char HOST[] = "192.168.1.2";

char CLIENT_ID[] = "flow-meters";
char TOPIC[] = "brewcast/history/flow-meters";

MQTTClient client;
WiFiClient net;

String message =
    "{\"key\": \"flow-meters\",\"data\": 48.75}";

void connect() {
  Serial.print("checking wifi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }

  Serial.print("\nconnecting...");
  while (!client.connect(TOPIC)) {
    Serial.print(".");
    delay(1000);
  }
}

void messageReceived(String &topic, String &payload) {
  Serial.println("incoming: " + topic + " - " + payload);
}


void setup()
{
    Serial.begin(115200);
    WiFi.begin(_SSID, _PASS);

    client.begin(HOST, net);
    client.onMessage(messageReceived);
    connect();

    Serial.println("");
}

void loop()
{
    client.loop();
    delay(10);

    if (!client.connected())
    {
        connect();
    }

    while (client.connected()){
        client.publish(TOPIC, message);
        Serial.println(message);
        delay(5000);
    }
}