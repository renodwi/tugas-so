# Prompt Desain UI: AgriStation Main Dashboard

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, font besar dan mudah dibaca), buatkan desain antarmuka untuk **AgriStation Main Dashboard** sebagai pusat kendali harian petani.

## Spesifikasi Tata Letak & Komponen

1. **Top Header:**
   - Sapaan singkat kepada petani dan tanggal hari ini.
   - Widget indikator cuaca lokal ringkas (suhu dan kondisi cerah/berawan/hujan).
   - Tombol aksi cepat berwarna hijau solid: `+ Catat Aktivitas`.

2. **Baris Ringkasan Atas (4 KPI Cards):**
   - **Total Lahan Aktif:** Menampilkan luas total dan jumlah blok (contoh: `4,5 Hektar • 6 Plot`).
   - **Kapasitas Gudang:** Menampilkan persentase terisi (contoh: `68% Terisi`) lengkap dengan *progress bar* horizontal hijau.
   - **Panen Terdekat:** Menampilkan komoditas dan hitung mundur hari (contoh: `Padi Ciherang • 5 Hari Lagi`).
   - **Saldo Kas Bulan Ini:** Menampilkan sisa kas pembukuan dengan angka tebal (contoh: `Rp 24.500.000`).

3. **Konten Utama (Layout 2 Kolom Asimetris: 60% Kiri, 40% Kanan):**
   - **Kolom Kiri — Daftar Tugas Hari Ini:**
     - Daftar *checklist* interaktif berukuran besar agar mudah dicentang.
     - Setiap baris tugas memuat nama kegiatan, lokasi blok lahan, dan *badge* kategori lembut (`Pemupukan`, `Pengairan`, `Penyemprotan`).
   - **Kolom Kanan — Kondisi Lahan & Jadwal Panen Terdekat:**
     - Daftar kartu ringkas untuk tiap blok lahan yang sedang aktif.
     - Menampilkan nama blok, jenis tanaman, fase pertumbuhan saat ini, dan *badge* peringatan warna Amber jika ada tindakan mendesak (seperti jadwal panen atau masa tunggu semprot).