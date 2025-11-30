#include <Arduino.h>
#include "gps.h"
#include "LoRa.h"


void setup(){
Serial.begin(115200);
setupGPS();
setupLoRa();
}

void loop(){
  readGPSData();
  loopLoRa();
}

