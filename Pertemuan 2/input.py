nama = input("masukkan nama anda:")
print("hallo,",nama,"| selamat datang di program python")

# proses input = meminta angka dari pengguna
angka_str= input("masukkan sebuah angka:")

# konversi tipe data dari string ke integer(bilangan bulat)
angka = int(angka_str)

#proses output
if angka % 2 == 0:
    print(angka, "adalah bilangan genap.")
else:
    print(angka,"adalah bilangan ganjil.")