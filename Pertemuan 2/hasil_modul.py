import penambahan
import pengurangan
import perkalian
import pembagian

a = int(input("masukkan angka pertama:"))
b = int(input("masukkan angka kedua:"))

print(f"hasil penjumlahan: {penambahan.tambah(a,b)}")
print(f"hasil pengurangan: {pengurangan.kurang(a,b)}")
print(f"hasil perkalian: {perkalian.kali(a,b)}")
print(f"hasil pembagian:{pembagian.bagi(a,b)}")




