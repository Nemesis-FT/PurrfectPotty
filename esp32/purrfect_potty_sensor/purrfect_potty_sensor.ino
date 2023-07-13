#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "";
const char* password = "";

const char *broker = "iot.fermitech.info";
const char *topic = "esp32/config";
const char *mqtt_username = "";
const char *mqtt_password = "";
const int port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

int sampling_rate = 1500;
int use_counter = 10;
int used_offset = 10;
int tare_timeout = 1000;
int danger_threshold = 10;
int danger_counter = 10;

void unpacker(char* str){
  char *ptrs[6];
  char *ptr = NULL;
  byte index = 0;
  ptr = strtok(str, ";");
  while(ptr != NULL){
    ptrs[index] = ptr;
    index++;
    ptr = strtok(NULL, ";");
  }
  sampling_rate = atoi(ptrs[0]);
  use_counter = atoi(ptrs[1]);
  used_offset = atoi(ptrs[2]);
  tare_timeout = atoi(ptrs[3]);
  danger_threshold = atoi(ptrs[4]);
  danger_counter = atoi(ptrs[5]);
}

void callback(char *topic, byte *payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  char str_array[length];
  for (int i = 0; i < length; i++) {
      str_array[i] = (char) payload[i];
  }
  unpacker(str_array);
}


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("Attempting connection...");
  while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        delay(100);
  }
  Serial.println("\nConnected to the WiFi network");
  Serial.print("Local ESP32 IP: ");
  Serial.println(WiFi.localIP());
  client.setServer(broker, port);
  client.setCallback(callback);
  while (!client.connected()){
    String client_id = "esp32-client-";
    client_id += String(WiFi.macAddress());
    if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
        Serial.println("iot.fermitech.info broker connected");
    } else {
        Serial.print("failed with state ");
        Serial.print(client.state());
        delay(2000);
    }
  }
  client.subscribe(topic);
}



void loop() {
  client.loop();
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(1000);                      // wait for a second
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
  delay(1000);                      // wait for a second
  Serial.println(sampling_rate);
}
