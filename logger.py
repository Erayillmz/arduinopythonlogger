import serial
from datetime import datetime

ser = serial.Serial("COM7", 9600, timeout=1)  # Port ve baud
print(" Arduino'dan veri bekleniyor...")

buffer = bytearray()  # byte'ları tutacak geçici alan

while True:
    if ser.in_waiting:
        gelen = ser.read(ser.in_waiting)
        buffer += gelen  # Gelen veriyi biriktir

        # STX ve ETX arası varsa paketi çıkar
        while b'\x02' in buffer and b'\x03' in buffer:
            start = buffer.find(b'\x02')
            end = buffer.find(b'\x03', start)

            if start != -1 and end != -1:
                paket = buffer[start + 1:end]  # STX-ETX arası

                try:
                    payload = paket.decode()
                    parcalar = payload.split(',')
                    veri_kismi = ','.join(parcalar[:-1])
                    gelen_checksum = int(parcalar[-1])

                    # ASCII toplamı
                    hesaplanan_checksum = sum(ord(c) for c in veri_kismi) % 256

                    if gelen_checksum == hesaplanan_checksum:
                        print(" Doğru veri:", veri_kismi)
                        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        satir = f"{zaman},{veri_kismi}\n"
                        with open("veri_logu.txt", "a", encoding="utf-8") as f:
                            f.write(satir)
                    else:
                        print(" Hatalı paket - Checksum uyuşmuyor")
                        print("Gelen:", gelen_checksum, "| Hesaplanan:", hesaplanan_checksum)

                except Exception as e:
                    print(" Decode veya split hatası:", e)
                    print("Ham veri:", paket)

                # Bu paketi buffer'dan çıkar (temizle)
                buffer = buffer[end + 1:]

            else:
                break
