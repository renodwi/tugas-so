# Prompt Desain UI: Agri-Crop Scheduler (Jadwal dan Plot Tanam)

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, keterbacaan tinggi), buatkan desain antarmuka untuk **Agri-Crop Scheduler** yang digunakan petani untuk mencatat data lahan, jenis tanaman, varietas, tanggal tanam, dan perkiraan waktu panen.

## Spesifikasi Tata Letak & Komponen

1. **Top Header & Filter:**
   - Judul aplikasi: **Jadwal & Plot Tanam**.
   - Filter cepat berbentuk pil (*pill tabs*): `Semua Plot`, `Sedang Tumbuh`, `Persiapan Lahan`, `Selesai Panen`.
   - Tombol aksi utama: `+ Tambah Plot Tanam`.

2. **Baris Ringkasan (3 KPI Cards):**
   - **Total Plot Aktif:** Jumlah blok lahan yang sedang ditanami.
   - **Total Luas Tertanam:** Akumulasi luas dalam satuan Hektar (`Ha`).
   - **Komoditas Utama:** Jenis tanaman yang paling banyak ditanam pada musim ini.

3. **Konten Utama — Daftar Plot Tanam (Grid 2 Kolom Rapi):**
   Setiap kartu merepresentasikan satu blok lahan dan menampilkan:
   - **Header Kartu:** Nama/Kode Lahan (misal: `Blok A1 - Sawah Utara`), luas lahan (`1,2 Ha`), dan *badge* status (`Sedang Tumbuh`).
   - **Info Tanaman:** Jenis tanaman dan varietas dengan *badge* hijau lembut (misal: `Jagung Hibrida • Varietas Bisi 18`).
   - **Jadwal Tanam & Panen:** Kotak informasi dua kolom yang membandingkan **Tanggal Tanam** (misal: `10 Sep 2026`) dan **Perkiraan Panen** (misal: `20 Des 2026`).
   - **Aksi Kartu:** Tombol teks sederhana `Edit Data` dan `Lihat Detail`.

4. **Formulir Input (Modal / Drawer Samping):**
   - Desain formulir sederhana dengan label jelas di atas kolom input untuk menambah plot baru: Nama Lahan, Luas (Ha), Jenis Tanaman, Varietas, Tanggal Penanaman, dan Estimasi Tanggal Panen.