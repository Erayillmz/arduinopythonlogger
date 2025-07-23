## Amaç  

MPU6050 den alınan verileri Arduinodan Pythona gönderip Python timestampli .txt dosyası olarak kaydetme 

 

# Kullanılan Donanım 

- Arduino Uno 

- MPU6050  IMU sensörü 

- Jumper kablolar 

- USB kablosu (Arduino–PC bağlantısı) 

 # Devre Bağlantısı

| MPU6050 Pin | Arduino Uno |
|-------------|-------------|
| VCC         | 5V          |
| GND         | GND         |
| SDA         | A4          |
| SCL         | A5          |


# Arduino Kodu  

-MPU6050'dan 14 byte veri okunur 

-Veriler 14 byte olarak okunur (ax,ay,az,gx,gy,gz,temp) 

-G cinsine çevirmek için hesaplamalar yapılır ve string olarak pythona yollanır 
```cpp

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

 ```


 

-Python üzerinden check etmek için checksum hesaplanır 

```cpp
//  Checksum hesapla (ASCII toplamı % 256)

uint8_t checksum = 0;

for (int i = 0; i < paket.length(); i++) {
  checksum += paket[i];
}

 ```


-I2C üzerinden haberleşiyoruz kütüphane gerekmez 

-Bağlantımız COM7 Arduino Uno 

 

# Python Kodu 

-Import Serial yapabilmek için pip install pyserial gerekli 

-import serial      - arduinodan veri almak için 

-from datetime import datetime   - timestamp koymak için 

-Gelen veriyi başlangıç ve bitiş biti hariç okur 

```cpp
 while b'\x02' in paket and b'\x03' in paket: 

            start = paket.find(b'\x02') 

            end = paket.find(b'\x03', start) 

 

            if start != -1 and end != -1 and end > start: 

                icerik = paket[start + 1:end] 

                paket = paket[end + 1:] 
```

 

-Checksumın uyuşup uyuşmadığını kontrol eder 
```cpp

               veri_kismi = ','.join(parcalar[:-1]) 
                gelen_checksum = int(parcalar[-1]) 
                hesaplanan_checksum = sum(ord(c) for c in veri_kismi) % 256 
 ```


-Üst üste yazma ihtimaline karşı maximum sınır belirlenmiş ve gerekirse  kodda atlıyor o paketi 

```cpp

      
          #Aşırı uzun paket kontrolü 
   

                if len(icerik) > MAX_PACKET_LENGTH: 

                    print(" Çok uzun paket atlandı:", list(icerik)) 

                    with open(error_log, 'a', encoding='utf-8') as f: 

                        f.write(f"{datetime.now()} - LONG PACKET: {list(icerik)}\n") 

                    continue 

 ```


-Kodun çalışması için Arduinoda serial monitorün kapalı olması gerek 

-Gelen veriyi timestampli dosya adına kaydeder 

```cpp
 if gelen_checksum == hesaplanan_checksum: 

                        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] 

                        with open(filename, 'a', encoding='utf-8') as f: 

                            f.write(f"{zaman},{veri_kismi}\n") 

                        print(f" [{zaman}] → {veri_kismi}") 

 ```


 
