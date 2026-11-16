# Prompt Desain UI: Agri-Equipment Log (Katalog dan Kondisi Alsintan)

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, tombol besar), buatkan desain antarmuka untuk **Agri-Equipment Log** yang digunakan untuk mendata dan memantau kondisi alat serta mesin pertanian (traktor, pompa air, sprayer), jadwal perawatan, dan riwayat penggunaannya.

## Spesifikasi Tata Letak & Komponen

1. **Top Header & Filter Status:**
   - Judul aplikasi: **Katalog & Kondisi Alsintan**.
   - Tab filter status kondisi: `Semua Unit`, `Siap Pakai`, `Perlu Servis`, `Sedang Diperbaiki`.
   - Tombol aksi utama: `+ Tambah Alsintan`.

2. **Baris Ringkasan (3 KPI Cards):**
   - **Total Unit Alsintan:** Jumlah keseluruhan alat/mesin terdaftar (contoh: `8 Unit`).
   - **Kondisi Siap Pakai:** Jumlah unit yang normal digunakan (teks hijau, contoh: `6 Unit`).
   - **Perlu Perawatan / Servis:** Jumlah unit yang mendekati jadwal ganti oli/servis atau rusak (teks amber/merah, contoh: `2 Unit`).

3. **Konten Utama — Grid Kartu Katalog Alsintan (3 Kolom):**
   Setiap kartu mewakili satu alat/mesin dan berisi:
   - **Header Kartu:** Nama Mesin & Nomor Seri/Kode (misal: `Traktor Roda 2 • Quick G1000`) dan *badge* status kondisi (`Siap Pakai` warna hijau atau `Jadwal Servis Dekat` warna kuning).
   - **Metrik Pemakaian:** Total jam kerja mesin (misal: `142 Jam Operasi`) dan tanggal terakhir digunakan (misal: `Terakhir dipakai: 14 Nov 2026 di Blok A1`).
   - **Info Perawatan Berikutnya:** Kotak kecil abu-abu lembut bertuliskan jadwal servis berikutnya (misal: `Servis Rutin & Ganti Oli: 8 Jam Kerja Lagi`).
   - **Tombol Aksi Kartu (2 Tombol Sejajar):** `+ Catat Pakai` dan `Log Servis`.