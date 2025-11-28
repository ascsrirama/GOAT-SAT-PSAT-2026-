#include <Arduino.h>
#include "gps.h"


void setup(){
Serial.begin(115200);
setupGPS();
}

void loop(){
  readGPSData();
}

