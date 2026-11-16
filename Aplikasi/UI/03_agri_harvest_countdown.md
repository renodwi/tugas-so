# Prompt Desain UI: Agri-Harvest Countdown

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, kontras tinggi), buatkan desain antarmuka untuk **Agri-Harvest Countdown** yang menampilkan perkembangan tanaman dan menghitung sisa waktu menuju masa panen melalui indikator *progress bar*.

## Spesifikasi Tata Letak & Komponen

1. **Top Header & Pengurutan:**
   - Judul aplikasi: **Hitung Mundur Panen**.
   - Dropdown pengurutan sederhana: `Urutkan: Panen Terdekat` atau `Baru Ditanam`.
   - Ringkasan cepat di header: `2 Plot Siap Panen Minggu Ini`.

2. **Konten Utama — Kartu Progres Tanaman (Daftar Vertikal atau Grid 2 Kolom Lapang):**
   Setiap kartu menampilkan satu blok lahan dengan hierarki visual yang sangat jelas:
   - **Bagian Atas Kartu:**
     - Kiri: Nama Lahan (`Blok B2 - Lahan Timur`), Jenis Tanaman & Varietas (`Padi Inpari 32`).
     - Kanan: Indikator hitung mundur besar dan mencolok, contoh: **`7 Hari Lagi`** (teks hijau/amber tegas) atau *badge* hijau solid **`SIAP PANEN`** jika sisa waktu 0 hari.
   - **Bagian Tengah Kartu (Progress Bar Utama):**
     - *Progress bar* horizontal tebal (`height: 14px`) dengan sudut membulat yang menunjukkan persentase umur tanaman (misal: `88%` terisi warna hijau sage).
     - Keterangan umur di atas *progress bar*: `Umur Tanaman: 98 HST (Hari Setelah Tanam) dari 112 Hari`.
     - Penanda fase pertumbuhan kecil di bawah *progress bar*: `Tanam` → `Vegetatif` → `Berbuah/Bunga` → `Siap Panen`.
   - **Bagian Bawah Kartu:**
     - Tanggal Tanam dan Target Tanggal Panen ditampilkan secara ringkas di sudut bawah.