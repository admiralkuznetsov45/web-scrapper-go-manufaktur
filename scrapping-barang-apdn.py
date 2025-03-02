import json
import asyncio
import time
from datetime import datetime
import os
import nest_asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def export_data_to_json(data_list):
    """
    Mengekspor data yang di-crawl ke dalam format JSON dengan nama file yang menyertakan timestamp,
    dan menyimpan file di dalam folder 'hasil-scrapping'.
    """
    try:
        # Buat folder 'hasil-scrapping' jika belum ada
          # Tentukan folder path relatif
        folder_name = os.path.join(os.getcwd(), "hasil-scrapping-barang")

        # Buat folder jika belum ada
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)


        # Dapatkan timestamp saat ini dengan jam, menit, dan detik
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")  # Format YYYY-MM-DD_HH-MM-SS

        # Buat nama file JSON dengan timestamp lengkap
        filename = f"hasil-scrapping-barang-{timestamp_str}.json"
        file_path = os.path.join(folder_name, filename)

        # Tulis data ke file JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4) # indent 4 agar file json mudah dibaca.
        print(f"Data berhasil diekspor ke {file_path}")

    except Exception as e:
        print(f"Gagal mengekspor data ke JSON: {e}")

# Apply nest_asyncio to enable nested event loops
nest_asyncio.apply()

async def atur_jumlah_baris():
    """
    Inisialisasi driver dan atur jumlah baris yang ditampilkan menjadi 100 dengan asyncio.
    """
    try:
        # Inisialisasi driver Chrome (sinkron)
        driver = webdriver.Chrome()

        # Buka halaman web (sinkron)
        driver.get('https://www.esdm.go.id/apdn/Barang/')

        # Maksimalkan jendela browser (sinkron)
        driver.maximize_window()

        # Tunggu hingga overlay "Please wait..." menghilang (sinkron, tetapi menunggu kondisi)
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'blockUI blockMsg blockPage'))
        )

        # Tunggu sebentar secara asinkron (opsional, memberikan jeda asinkron)
        await asyncio.sleep(2)

        # Tunggu hingga dropdown jumlah baris dapat diklik (sinkron, tetapi menunggu kondisi)
        dropdown = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, 'DataTables_Table_0_length'))
        )
        # Klik dropdown (sinkron)
        dropdown.click()
        # Tunggu hingga opsi 100 baris dapat diklik (sinkron, tetapi menunggu kondisi)
        option_100 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//select[@name="DataTables_Table_0_length"]/option[5]'))
        )
        # Klik opsi 100 baris (sinkron)
        option_100.click()
        # Berikan waktu agar perubahan diterapkan (asinkron)
        await asyncio.sleep(2)

        return driver  # Kembalikan driver yang telah diinisialisasi
    except Exception as e:
        print(f"Gagal mengatur jumlah baris menjadi 100: {e}")
        return None  # Kembalikan None jika terjadi kesalahan


# Fungsi untuk mengambil data dari halaman saat ini dan menampilkannya dalam format tabel
def ambil_data_halaman(driver, data_list,id_counter):
    """
    Fungsi ini mengambil data dari tabel di halaman web yang sedang aktif (menggunakan driver Selenium),
    kemudian menampilkan data tersebut dalam format tabel yang rapi di konsol.
    """

    # Membuat header tabel
    print("{:<30} {:<20} {:<20} {:<30} {:<10} {:<20} {:<20}".format("Nama Perusahaan", "Hasil Produksi", "Jenis Produk", "Spesifikasi", "TKDN", "Kapasitas Produksi", "Kategori"))
    print("-" * 150)

    try:
        # Mencari semua elemen 'tr' (table row) dalam tbody untuk mengetahui jumlah baris.
        rows = driver.find_elements("xpath", '//table[@id="DataTables_Table_0"]/tbody/tr')

        # Inisialisasi variabel untuk melacak nama perusahaan terakhir yang tidak kosong
        last_nama_perusahaan = ""

        # Looping melalui setiap baris tabel
        for i, row in enumerate(rows):
            try:
                # Mengambil teks dari setiap kolom di baris 'row'
                cols = row.find_elements(By.TAG_NAME, "td")
                nama = cols[0].text.strip()
                hasil = cols[1].text.strip()
                jenis = cols[2].text.strip()
                spesifikasi = cols[3].text.strip()
                tkdn = cols[4].text.strip()
                kapasitas = cols[5].text.strip()
                kategori = cols[6].text.strip()

                # Jika nama perusahaan kosong, gunakan nama perusahaan terakhir yang tidak kosong
                if not nama:
                    nama = last_nama_perusahaan

                # Jika nama perusahaan tidak kosong, update variabel last_nama_perusahaan
                else:
                    last_nama_perusahaan = nama

                # Menampilkan data dalam format tabel
                print("{:<30} {:<20} {:<20} {:<30} {:<10} {:<20} {:<20}".format(nama, hasil, jenis, spesifikasi, tkdn, kapasitas, kategori))

                # Tambahkan data ke list
                data_list.append({
                    "ID": id_counter,
                    "Nama Perusahaan": nama,
                    "Hasil Produksi": hasil,
                    "Jenis Produk": jenis,
                    "Spesifikasi": spesifikasi,
                    "TKDN": tkdn,
                    "Kapasitas Produksi": kapasitas,
                    "Kategori": kategori
                })
                id_counter += 1  # Increment ID counter


            except IndexError as ie:
                # Menangani error jika terjadi masalah saat mengambil data dari baris tertentu
                print(f"error mengambil baris ke {i+1}, dikarenakan indeks kolom tidak ditemukan: {ie}")
                continue  # Skip baris ini dan lanjutkan ke baris berikutnya
            except Exception as e:
                # Menangani error jika terjadi masalah saat mengambil data dari baris tertentu
                print(f"error mengambil baris ke {i+1}, dikarenakan: {e}")
                continue  # Skip baris ini dan lanjutkan ke baris berikutnya

    except Exception as e:
        # Menangani error jika terjadi masalah saat menemukan elemen tabel
        print(f"error menemukan table element: {e}")

# Fungsi untuk mengklik tombol "Next" halaman
def klik_next(driver):
    try:
        #### klik tombol next yang ada di web itu 
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'DataTables_Table_0_next'))
        )
        if 'disabled' not in next_button.get_attribute('class'):
            next_button.click()
            return True
        else:
            return False
    except Exception as e:
        print(f"Gagal klik next: {e}")
        return False

# Fungsi untuk melakukan scraping dengan jumlah halaman maksimal yang ditentukan
def scrap_with_max_pages(driver, max_pages , data_list):
    """
    Fungsi ini melakukan scraping data dari beberapa halaman web, dengan batasan jumlah halaman maksimal.

    Args:
        driver: Objek driver Selenium yang sudah diinisialisasi.
        max_pages: Jumlah halaman maksimal yang ingin di-scrape.
    """

    # Mengatur halaman awal ke 0
    current_page = 0
    id_counter = 1  # Inisialisasi ID counter


    # Loop selama nomor halaman saat ini kurang dari atau sama dengan halaman maksimum
    while current_page <= max_pages:

        # Memanggil fungsi untuk mengambil data dari halaman saat ini
        ambil_data_halaman(driver , data_list,id_counter)

        # Memeriksa apakah tombol "Next" dapat diklik
        if not klik_next(driver):
            # Jika tombol "Next" tidak dapat diklik (misalnya, di halaman terakhir), keluar dari loop
            break

        # Memberikan jeda waktu 2 detik sebelum melanjutkan ke halaman berikutnya
        time.sleep(2)

        # Menaikkan nomor halaman saat ini
        current_page += 1


    # Mencetak informasi halaman terakhir yang di-scrape
    print(f"Scrapping berhenti di halaman {current_page-1} dari maksimal {max_pages} yang ditentukan")


##### Fungsi Awal Dimulai Dari Sini ##########
async def main():
    """
    Fungsi utama asinkron yang mengatur alur keseluruhan dari skrip web scraping.

    Fungsi ini melakukan langkah-langkah berikut:
    1.  Memanggil fungsi 'atur_jumlah_baris' untuk menginisialisasi WebDriver dan mengatur opsi jumlah baris pada halaman web.
    2.  Memeriksa apakah inisialisasi WebDriver berhasil.
    3.  Jika berhasil, melanjutkan dengan proses scraping data dari halaman web.
    4.  Mencetak pesan sukses jika WebDriver berhasil diinisialisasi dan opsi jumlah baris berhasil diatur.
    5.  Memanggil fungsi 'scrap_with_max_pages' untuk memulai proses scraping data hingga batas maksimum halaman.
    6.  Menutup WebDriver setelah proses scraping selesai untuk melepaskan sumber daya.
    7.  Memanggil fungsi 'export_data_to_json' untuk menyimpan data hasil scraping ke dalam format JSON.
    8.  Jika inisialisasi WebDriver gagal, mencetak pesan kegagalan.
    """

    # Memanggil fungsi atur_jumlah_baris() secara asinkron untuk menginisialisasi driver dan mengatur jumlah baris.
    driver = await atur_jumlah_baris()

    # Memeriksa apakah driver berhasil diinisialisasi (tidak None)
    if driver:
        # Jika driver berhasil diinisialisasi, cetak pesan sukses
        print("Driver and row settings successful.")

        # Inisialisasi list kosong untuk menyimpan data hasil scraping
        data_list = []

        # Memanggil fungsi scrap_with_max_pages() untuk memulai proses scraping,
        # dengan driver yang telah diinisialisasi, batas maksimum halaman 5, dan list data.
        scrap_with_max_pages(driver, 5, data_list)

        # Menutup driver setelah proses scraping selesai untuk melepaskan sumber daya.
        # driver.quit()

        # Memanggil fungsi export_data_to_json() untuk menyimpan data hasil scraping ke dalam file JSON.
        export_data_to_json(data_list)
    else:
        # Jika driver gagal diinisialisasi (atur_jumlah_baris() mengembalikan None), cetak pesan error
        print("Driver initialization failed.")

# Blok ini memastikan bahwa fungsi main() hanya dijalankan jika file ini dijalankan sebagai skrip utama
if __name__ == "__main__":
    # Menjalankan fungsi main() secara asinkron menggunakan asyncio.run()
    asyncio.run(main())