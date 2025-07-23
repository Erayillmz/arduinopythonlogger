#include <Wire.h>

uint8_t packet_id = 0;

void setup() {
  Wire.begin();
  Serial.begin(9600);

  // MPU6050'i uyandır
  Wire.beginTransmission(0x68);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();
}

void loop() {
  int16_t ax, ay, az, temp_raw, gx, gy, gz;

  // Her döngüde yeniden uyandır
  Wire.beginTransmission(0x68);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();

  // Veri iste
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) {
    Serial.println(" MPU6050 iletişim hatası!");
    delay(500);
    return;
  }

  Wire.requestFrom(0x68, 14, true);
  if (Wire.available() < 14) {
    Serial.println(" Yetersiz veri geldi!");
    delay(500);
    return;
  }

  // RAW verileri oku
  ax = (Wire.read() << 8) | Wire.read();
  ay = (Wire.read() << 8) | Wire.read();
  az = (Wire.read() << 8) | Wire.read();
  temp_raw = (Wire.read() << 8) | Wire.read();
  gx = (Wire.read() << 8) | Wire.read();
  gy = (Wire.read() << 8) | Wire.read();
  gz = (Wire.read() << 8) | Wire.read();

  //  Birim dönüşümleri
  float ax_g = ax / 16384.0;
  float ay_g = ay / 16384.0;
  float az_g = az / 16384.0;

  float gx_dps = gx / 131.0;
  float gy_dps = gy / 131.0;
  float gz_dps = gz / 131.0;

  float tempC = temp_raw / 340.0 + 36.53;

  //  Paket oluştur
  String paket = "";
  paket += String(ax_g, 2) + "," + String(ay_g, 2) + "," + String(az_g, 2) + ",";
  paket += String(gx_dps, 2) + "," + String(gy_dps, 2) + "," + String(gz_dps, 2) + ",";
  paket += String(tempC, 2) + "," + String(packet_id++);

  //  Checksum hesapla (ASCII toplamı % 256)
  uint8_t checksum = 0;
  for (int i = 0; i < paket.length(); i++) {
    checksum += paket[i];
  }




  //  Paketi gönder
  Serial.write(0x02);        // STX
  Serial.print(paket);       // Veri
  Serial.print(",");
  Serial.print(checksum);    // Checksum
  Serial.write(0x03);        // ETX

  delay(100);  // 10 Hz
}
