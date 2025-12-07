
//RAMA TRIAL 1

#include "LoRa.h"
#include <Arduino.h>

// Pins on the ESP32 that will connect to the RA-08H UART
// (change to what we are using)
static const int LORA_RX_PIN = 16;       // ESP32 RX2  <- LoRa TX
static const int LORA_TX_PIN = 17;       // ESP32 TX2  -> LoRa RX
static const uint32_t LORA_BAUD = 9600;  // adjust if your module uses different

// Use hardware UART2 on ESP32
HardwareSerial LoRaSerial(2);

void setupLoRa() {
    // Start UART used to talk to the LoRa module
    LoRaSerial.begin(LORA_BAUD, SERIAL_8N1, LORA_RX_PIN, LORA_TX_PIN);
    delay(200);

    Serial.println("LoRa UART started");

    // If a module with AT firmware is wired, this should make it respond "OK"
    LoRaSerial.println("AT");
}

void loopLoRa() {
    // For now, just echo anything from LoRa to the USB Serial Monitor
    while (LoRaSerial.available()) {
        char c = LoRaSerial.read();
        Serial.write(c);
    }
}

void sendLoRaLine(const String& line) {
    // Send one line of text to the LoRa module
    LoRaSerial.println(line);
}

