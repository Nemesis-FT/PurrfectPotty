#include <WiFi101.h>
#include <PubSubClient.h>
#include "HX711.h"
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <HttpClient.h>
#include <ArduinoJson.h>
// MQTT Configuration
const char* ssid = "";
const char* password = "";
const char *broker = "iot.fermitech.info";
const char *topic = "esp32/config";
const char *mqtt_username = "";
const char *mqtt_password = "";
const int port = 1883;
WiFiClient wifiClient1;
WiFiClient wifiClient2;
PubSubClient mqttClient(wifiClient1);

// NTP Configuration
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP);

// Scale configuration
HX711 scale(5, 4);
float calibration_factor = 13000;

// DataProxy auth
const char *thing_token = "";
const char *http_address = "";
const int http_port = 8030;

// Device configurable parameters
int sampling_rate = 1500;
int use_counter = 10;
int used_offset = 3000;
int tare_timeout = 50;
int danger_threshold = 4500;
int danger_counter = 10;

// Flags
bool in_use = false;
bool dirty = false;

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
  char str_array[length];
  for (int i = 0; i < length; i++) {
      str_array[i] = (char) payload[i];
  }
  unpacker(str_array);
}


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  
  Serial.println("Attempting connection...");
  while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        delay(100);
  }
  delay(1000);
  
  Serial.println("\nConnected to the WiFi network");
  Serial.print("Local Arduino IP: ");
  Serial.println(WiFi.localIP());

  mqttClient.setServer(broker, port);
  mqttClient.setCallback(callback);
  while (!mqttClient.connected()){
    String client_id = "arduino-client-";
    client_id += "123";
    if (mqttClient.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
        Serial.println("iot.fermitech.info broker connected");
    } else {
        Serial.print("failed with state ");
        Serial.print(mqttClient.state());
        delay(2000);
    }
  }
  mqttClient.subscribe(topic);
  
  timeClient.begin(); 

  scale.set_scale();
  scale.tare();  //Reset the scale to 0
  long zero_factor = scale.read_average(); //Get a baseline reading
  Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
  Serial.println(zero_factor);
  digitalWrite(LED_BUILTIN, HIGH);
}

int get_scale(){
  scale.set_scale(calibration_factor); //Adjust to this calibration factor
  float units = scale.get_units(10);
  if (units < 0)
  {
    units = 0.00;
  }
  return int(units*1000);
}

void print_weight(float units){
  Serial.print(units);
  Serial.print(" kg"); 
  Serial.print(" calibration_factor: ");
  Serial.print(calibration_factor);
  Serial.println();
}

void send_rssi(){
  int rssi = WiFi.RSSI();
  if(wifiClient2.connect(http_address, http_port)){
    HttpClient http(wifiClient2, http_address, http_port);
    String data = "{\"thing_token\":\"";
    data.concat(thing_token);
    data.concat("\", \"timestamp\":\"");
    timeClient.update();
    data.concat(timeClient.getEpochTime());
    data.concat("\", \"rssi_str\":");
    data.concat(rssi);
    data.concat("}");
    http.post("/api/actions/v1/rssi", "application/json",data);
  }
}

void send_notification(String endpoint){
  if(wifiClient2.connect(http_address, http_port)){
    HttpClient http(wifiClient2, http_address, http_port);
    String data = "{\"thing_token\":\"";
    data.concat(thing_token);
    data.concat("\", \"timestamp\":\"");
    timeClient.update();
    data.concat(timeClient.getEpochTime());
    data.concat("\"}");

    http.post(endpoint, "application/json",data);
  }
}

// Counters
int use_c = 0;
int warning_c = 0;

// Data
int litter_weight = 0;
long prev_millis = 0;

void loop() {
  // Get latest configuration from MQTT broker
  mqttClient.loop();
  // Run measurement
  delay(sampling_rate);
  send_rssi();
  String msg = "Pesata: ";
  int units = get_scale();
  msg.concat(units);
  msg.concat(" Peso sabbia: ");
  msg.concat(litter_weight);
  Serial.println(msg);
  // Check if the weight is above used_offset (in grams)
  if(units > used_offset+litter_weight+500){
    warning_c = 0;
    Serial.println("Units > used_offset+litter_weight");
    use_c++;
    Serial.println(use_c);
    if(use_c < use_counter){
      Serial.println("  use_c < use_counter");
      return;
    }
    if(use_c < tare_timeout){
      Serial.println("  use_c < tare_timeout");
      in_use = true;
      return;
    }
    Serial.println("  use_c > tare_timeout");
    in_use = false;
    litter_weight = units;
    dirty = false;
  }
  else{
    Serial.println("Units < used_offset+litter_weight");
    use_c = 0;
    if(in_use){
      Serial.println("  Litterbox has been used!");
      send_notification("/api/actions/v1/litter_usage");
      in_use = false;
    }
    if(units < danger_threshold){
      Serial.println("  Litterbox below the threshold");
      warning_c++;
      if(warning_c>=danger_counter){
        Serial.println("    Litterbox empty!");
        warning_c = 0;
        if(!dirty){
          send_notification("/api/actions/v1/litter_alarm");
          dirty = true;
          Serial.println("      Notification sent!");
        }
      }
    }
  }
}
