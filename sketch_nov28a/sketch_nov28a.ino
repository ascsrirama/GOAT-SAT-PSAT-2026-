#include <Arduino.h>

float lat = 17.76;
float lon = 83.21;

void setup() {
  Serial.begin(115200); // same baud as Python
}

void loop() {
  // Fake GPS: add tiny random movement
  lat += random(-10, 10) * 0.00001;
  lon += random(-10, 10) * 0.00001;

  // Fake accelerometer (-2 to 2 m/s²)
  float acc = random(-200, 200) / 100.0;

  // Fake altimeter (100 to 200 meters)
  float alt = 100 + random(0, 100);

  // Send as "LAT,LON,ACC,ALT\n"
  Serial.print(lat, 6);
  Serial.print(",");
  Serial.print(lon, 6);
  Serial.print(",");
  Serial.print(acc, 2);
  Serial.print(",");
  Serial.println(alt, 2);

  delay(500); // 20 Hz update
}
