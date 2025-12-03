#pragma once
// put library
//#define LORA_AT_WIOE5
#include <Arduino.h>
// #include <SoftwareSerial.h>
// #include <LoRa_AT.h>

void setupLoRa();
void loopLoRa();
void sendLoRaLine(const char* line);