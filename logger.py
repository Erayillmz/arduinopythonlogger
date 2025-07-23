import serial
from datetime import datetime

#  Zaman damgalı dosyalar
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"data_{timestamp}.txt"
error_log = f"errors_{timestamp}.log"

#  Dosya başlıkları
with open(filename, 'w', encoding='utf-8') as f:
    f.write("Zaman,AX_g,AY_g,AZ_g,GX_dps,GY_dps,GZ_dps,TempC,PacketID\n")

#  Seri port başlat
ser = serial.Serial("COM7", 9600, timeout=1)
print(" Arduino'dan veri bekleniyor...")

paket = bytearray()
MAX_PACKET_LENGTH = 100  # STX-ETX arası azami uzunluk

while True:
    if ser.in_waiting:
        gelen = ser.read(ser.in_waiting)
        paket += gelen

        # Buffer taşmasını önle
        if len(paket) > 2048:
            print(" Veri tamponu çok doldu, sıfırlanıyor.")
            paket.clear()

        while b'\x02' in paket and b'\x03' in paket:
            start = paket.find(b'\x02')
            end = paket.find(b'\x03', start)

            if start != -1 and end != -1 and end > start:
                icerik = paket[start + 1:end]
                paket = paket[end + 1:]

                # Aşırı uzun paket kontrolü
                if len(icerik) > MAX_PACKET_LENGTH:
                    print(" Çok uzun paket atlandı:", list(icerik))
                    with open(error_log, 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.now()} - LONG PACKET: {list(icerik)}\n")
                    continue

                try:
                    # ASCII decode + split
                    payload = icerik.decode('ascii')
                    parcalar = payload.split(',')

                    # 9 parça beklenir: 8 veri + 1 checksum
                    if len(parcalar) != 9:
                        print(" Beklenmeyen parça sayısı:", parcalar)
                        continue

                    veri_kismi = ','.join(parcalar[:-1])
                    gelen_checksum = int(parcalar[-1])
                    hesaplanan_checksum = sum(ord(c) for c in veri_kismi) % 256

                    if gelen_checksum == hesaplanan_checksum:
                        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        with open(filename, 'a', encoding='utf-8') as f:
                            f.write(f"{zaman},{veri_kismi}\n")
                        print(f" [{zaman}] → {veri_kismi}")
                    else:
                        print(f"Checksum hatalı → Gelen: {gelen_checksum}, Hesaplanan: {hesaplanan_checksum}")
                        with open(error_log, 'a', encoding='utf-8') as f:
                            f.write(f"{datetime.now()} - BAD CHECKSUM: {payload}\n")

                except Exception as e:
                    print(" Decode veya işlem hatası:", e)
                    with open(error_log, 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.now()} - EXCEPTION: {str(e)} | Paket: {list(icerik)}\n")

            else:
                break
