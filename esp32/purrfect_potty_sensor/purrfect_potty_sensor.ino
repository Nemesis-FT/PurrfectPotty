#include <WiFi101.h>
#include <PubSubClient.h>
#include "HX711.h"
#include <HttpClient.h>
#include <DHT11.h>
#include <WDTZero.h>

#ifdef __arm__
// should use uinstd.h to define sbrk but Due causes a conflict
extern "C" char* sbrk(int incr);
#else  // __ARM__
extern char *__brkval;
#endif  // __arm__

int freeMemory() {
  char top;
#ifdef __arm__
  return &top - reinterpret_cast<char*>(sbrk(0));
#elif defined(CORE_TEENSY) || (ARDUINO > 103 && ARDUINO != 151)
  return &top - __brkval;
#else  // __arm__
  return __brkval ? &top - __brkval : &top - __malloc_heap_start;
#endif  // __arm__
}

// MQTT Configuration
const char* ssid = "";
const char* password = "";
const char *broker = "";
const char *topic = "";
const char *mqtt_username = "";
const char *mqtt_password = "";
const int port = 1883;
WiFiClient wifiClient1;
WiFiClient wifiClient2;
PubSubClient mqttClient(wifiClient1);

// Scale configuration
HX711 scale(5, 4);
float calibration_factor = 13000;

// DHT11 configuration
DHT11 dht11(6);
float temperature;

// DataProxy auth
const char *thing_token = "";
const char *http_address = "";
const int http_port = 8000;

// Device configurable parameters
int sampling_rate = 1500;
int use_counter = 10;
int used_offset = 3000;
int tare_timeout = 20;

// Watchdog setup

WDTZero MyWatchDoggy;
bool keepAlive = true;

// Debug setup
bool logLatency = true;

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
  pinMode(7, OUTPUT);
  digitalWrite(7, HIGH);
  Serial.begin(9600);
  MyWatchDoggy.attachShutdown(resetFunction);
  MyWatchDoggy.setup(WDT_SOFTCYCLE8S);
  WiFi.begin(ssid, password);
  
  Serial.println("Attempting connection...");
  while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        delay(100);
  }
  MyWatchDoggy.clear();
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
  MyWatchDoggy.clear();

  Serial.println("Setting up the scale...");
  scale.set_scale();
  scale.tare();  //Reset the scale to 0
  long zero_factor = scale.read_average(); //Get a baseline reading
  Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
  Serial.println(zero_factor);
  MyWatchDoggy.clear();
  
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

unsigned long time = 0;
int counter = 0;


void send_latency(){

}


void report_time(){
  Serial.print("Latenza su ");
  Serial.print(counter);
  Serial.print(": ");
  Serial.print(time/counter);
  Serial.println(" ms.");
  if(counter >= 10){
    if(wifiClient2.connect(http_address, http_port)){
        HttpClient http(wifiClient2, http_address, http_port);
        String data = "{\"thing_token\":\"";
        data.concat(thing_token);
        data.concat("\", \"latency\":");
        data.concat(time/counter);
        data.concat("}");
        http.post("/api/actions/v1/latency", "application/json",data);
    }
    time = 0;
    counter = 0;
  }
}

void send_rssi(){
  int rssi = WiFi.RSSI();
  Serial.print("RSSI: ");
  Serial.println(rssi);
  if(rssi==-100){
    keepAlive = false;
  }
  unsigned long start_time = millis();
  if(wifiClient2.connect(http_address, http_port)){
    HttpClient http(wifiClient2, http_address, http_port);
    String data = "{\"thing_token\":\"";
    data.concat(thing_token);
    data.concat("\", \"rssi_str\":");
    data.concat(rssi);
    data.concat("}");
    http.post("/api/actions/v1/rssi", "application/json",data);
    unsigned long end_time = millis();
    counter++;
    time+=end_time-start_time;
  }

}

void send_temp(float temp){
  unsigned long start_time = millis();
  if(wifiClient2.connect(http_address, http_port)){
    HttpClient http(wifiClient2, http_address, http_port);
    String data = "{\"thing_token\":\"";
    data.concat(thing_token);
    data.concat("\", \"temperature\":");
    data.concat(temp);
    data.concat("}");
    http.post("/api/actions/v1/temperature", "application/json",data);
    unsigned long end_time = millis();
    counter++;
    time+=end_time-start_time;
  }
}

void send_notification(String endpoint){
  unsigned long start_time = millis();
  if(wifiClient2.connect(http_address, http_port)){
    HttpClient http(wifiClient2, http_address, http_port);
    String data = "{\"thing_token\":\"";
    data.concat(thing_token);
    data.concat("\"}");

    http.post(endpoint, "application/json",data);
    unsigned long end_time = millis();
    counter++;
    time+=end_time-start_time;
  }
}

void resetFunction(){
  Serial.println("RESET SIGNAL");
}

// Counters
int use_c = 0;
int tare_c = 0;
int cooldown_c;

int cooldown_t = 5;

// Data
int litter_weight = 0;
long prev_millis = 0;

// Flags
bool in_use = false;
bool dirty = false;


// Timers
unsigned long end_loop = 0;
unsigned long start_loop = 0;

void loop() {
  // Get latest configuration from MQTT broker
  end_loop = millis();
  Serial.print("Elapsed time since last loop: ");
  Serial.println(end_loop-start_loop);
  Serial.print("Free memory: ");
  int mem = freeMemory();
  Serial.println(mem, DEC);
  mqttClient.loop();
  // Run measurement
  delay(sampling_rate);
  if(keepAlive){
    MyWatchDoggy.clear();
  }
  
  start_loop = millis();
  send_rssi();
  temperature = dht11.readTemperature();
  send_temp(temperature);
  String tmp = "Temperatura: ";
  tmp.concat(temperature);
  tmp.concat(" C");
  Serial.println(tmp);
  String msg = "Pesata: ";
  int units = get_scale();
  msg.concat(units);
  msg.concat(" Peso sabbia: ");
  msg.concat(litter_weight);
  Serial.println(msg);
  if(units > used_offset){
    Serial.println("Units > used_offset");
    use_c++;
    if(tare_c>10){
      tare_c=tare_c-10;
    }
    if(use_c < use_counter){
      Serial.println("  use_c < use_counter");
      return;
    }
    if(use_c > use_counter){
      in_use = true;
      cooldown_c = 0;
      Serial.println("  !!!");
      return;
    }
  }
  else if(!in_use){
    tare_c++;
    if(tare_c>tare_timeout){
      scale.tare();
      Serial.println("Tare set!");
      tare_c = 0;
    }
  }
  else{
    if(cooldown_c < cooldown_t){
      cooldown_c++;
    }
    else{
      Serial.println("  Litterbox has been used!");
      send_notification("/api/actions/v1/litter_usage");
      in_use = false;
      use_c = 0;
      cooldown_c = 0;
    }

  }
  report_time();
}
