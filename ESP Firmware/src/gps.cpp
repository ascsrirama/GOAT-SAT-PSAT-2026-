#include "gps.h"
#include "LoRa.h"            // ⬅️ NEW: for sendLoRaLine
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

/*
   GPS + LoRa bridge.

   GPS module on SoftwareSerial:
     RXPin = 18 (ESP32 reads from GPS TX)
     TXPin = 19
*/

static const int RXPin = 18, TXPin = 19;
static const uint32_t GPSBaud = 9600;

// Uncomment if you want raw NMEA logging control via build flags
// #define GPS_DEBUG_RAW 1

TinyGPSPlus gps;

// The serial connection to the GPS device
SoftwareSerial ss(RXPin, TXPin);

static void displayInfo()
{
  Serial.print(F("Location: "));
  if (gps.location.isValid())
  {
    Serial.print(gps.location.lat(), 6);
    Serial.print(F(","));
    Serial.print(gps.location.lng(), 6);
  }
  else
  {
    Serial.print(F("INVALID"));
  }

  Serial.print(F("  Date/Time: "));
  if (gps.date.isValid())
  {
    Serial.print(gps.date.month());
    Serial.print(F("/"));
    Serial.print(gps.date.day());
    Serial.print(F("/"));
    Serial.print(gps.date.year());
  }
  else
  {
    Serial.print(F("INVALID"));
  }

  Serial.print(F(" "));
  if (gps.time.isValid())
  {
    if (gps.time.hour() < 10) Serial.print(F("0"));
    Serial.print(gps.time.hour());
    Serial.print(F(":"));
    if (gps.time.minute() < 10) Serial.print(F("0"));
    Serial.print(gps.time.minute());
    Serial.print(F(":"));
    if (gps.time.second() < 10) Serial.print(F("0"));
    Serial.print(gps.time.second());
    Serial.print(F("."));
    if (gps.time.centisecond() < 10) Serial.print(F("0"));
    Serial.print(gps.time.centisecond());
  }
  else
  {
    Serial.print(F("INVALID"));
  }

  Serial.println();
}

void setupGPS()
{
  ss.begin(GPSBaud);

  Serial.println(F("DeviceExample.ino"));
  Serial.println(F("TinyGPSPlus + LoRa bridge"));
  Serial.print(F("TinyGPSPlus version: "));
  Serial.println(TinyGPSPlus::libraryVersion());
  Serial.println(F("Reading GPS and forwarding to LoRa..."));
}

void readGPSData()
{
  // Buffer to accumulate one raw NMEA line
  static String rawLine = "";

  while (ss.available() > 0)
  {
    char c = ss.read();

    // ---- RAW NMEA LINE BUILDING ----
    if (c != '\r')
    {
      rawLine += c;
      if (c == '\n')
      {
        // We have a complete NMEA sentence in rawLine
        Serial.print(F("GPS RAW: "));
        Serial.print(rawLine);

        // 🔥 SEND THIS LINE TO LORA TX BOARD 🔥
        // (RA-08 TX node will receive this over UART and can forward via LoRa)
        sendLoRaLine(rawLine);

        rawLine = "";
      }
    }

    // Feed TinyGPSPlus parser
    if (gps.encode(c))
    {
      // New valid sentence processed; show summary
      displayInfo();

      // OPTIONAL: also send a compact lat/lon line to LoRa
      if (gps.location.isValid())
      {
        String fixLine = "LAT=" + String(gps.location.lat(), 6) +
                         ",LON=" + String(gps.location.lng(), 6);
        fixLine += "\n";
        sendLoRaLine(fixLine);

        Serial.print(F("LoRa SENT: "));
        Serial.print(fixLine);
      }
    }
  }

  // Safety: if GPS seems dead
  if (millis() > 5000 && gps.charsProcessed() < 10)
  {
    Serial.println(F("No GPS detected: check wiring."));
    while (true) { }
  }
}
