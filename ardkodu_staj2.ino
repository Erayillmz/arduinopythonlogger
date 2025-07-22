#include <Wire.h>
uint8_t packet_id=0;
void setup() {
Wire.begin();
Serial.begin(9600);
Wire.beginTransmission(0x68); //iletişimi başlat
Wire.write(0x6B);   // slave adresi
Wire.write(0x00);  // 00 uyandırmayı sağlar
Wire.endTransmission();   // işlemi bitir

}
void loop() {
  int16_t ax, ay, az, temp, gx, gy, gz;   //tanımlıyoruz
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);  // Veri başlangıç adresi
  Wire.endTransmission(false); // STOP gönderme
  Wire.requestFrom(0x68, 14, true);   // 0x68 adresinden 14 bytelık veri isteme

  ax = (Wire.read() << 8) | Wire.read();  //shift register
  ay = (Wire.read() << 8) | Wire.read();
  az = (Wire.read() << 8) | Wire.read();
  temp = (Wire.read() << 8) | Wire.read();
  gx = (Wire.read() << 8) | Wire.read();
  gy = (Wire.read() << 8) | Wire.read();
  gz = (Wire.read() << 8) | Wire.read(); 
  Serial.print("AX: "); Serial.print(ax);
  Serial.print("  AY: "); Serial.print(ay);
  Serial.print("  AZ: "); Serial.println(az);

  char buffer [100];
  snprintf(buffer, sizeof(buffer), "%d,%d,%d,%d,%d,%d,%d,%d", ax, ay, az, gx, gy, gz, temp, packet_id++); //paket yaratıp yerleştirme taslağı hazırlıyoruz

   uint8_t checksum = 0;   //kalite kontrol için paketin içindekileri (1=49) toplayıp paketin sonuna ekliyoruz
  for (int i = 0; buffer[i]; i++) {
    checksum += buffer[i];
}
Serial.write(0x02);  //başlatma biti
Serial.print(buffer);
Serial.print(",");
Serial.print(checksum);
Serial.write(0x03);

delay(100);
}