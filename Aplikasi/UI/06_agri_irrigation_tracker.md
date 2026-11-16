# Prompt Desain UI: Agri-Irrigation Tracker

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, mudah dibaca), buatkan desain antarmuka untuk **Agri-Irrigation Tracker** yang digunakan untuk mencatat kegiatan pengairan lahan, lama pengairan, sumber air, jenis pompa, dan penggunaan bahan bakar.

## Spesifikasi Tata Letak & Komponen

1. **Top Header:**
   - Judul aplikasi: **Catatan Pengairan Lahan**.
   - Filter dropdown berdasarkan Blok Lahan.
   - Tombol aksi utama: `+ Catat Pengairan`.

2. **Baris Ringkasan (3 KPI Cards):**
   - **Total Durasi Pengairan:** Akumulasi jam pengairan bulan ini (contoh: `42 Jam 30 Menit`).
   - **Penggunaan Bahan Bakar:** Total konsumsi BBM pompa air (contoh: `38,5 Liter Solar`).
   - **Pengairan Terakhir:** Informasi blok lahan dan waktu terakhir kali diairi (contoh: `Blok C1 • Kemarin`).

3. **Konten Utama — Tabel Riwayat Pengairan:**
   - Tabel bersih dan terstruktur yang memuat kolom:
     1. **Tanggal & Waktu** (misal: `15 Nov 2026, 06:30`)
     2. **Lokasi Lahan** (misal: `Blok A2 - Sawah Selatan`)
     3. **Sumber Air** (*badge* biru/hijau lembut: `Irigasi Teknis`, `Sumur Bor`, `Sungai`, `Embung`)
     4. **Jenis Pompa** (misal: `Pompa Diesel 3 Inch`, `Pompa Listrik`, `Gravitasi / Tanpa Pompa`)
     5. **Lama Pengairan** (misal: `3 Jam 15 Menit`)
     6. **Pemakaian BBM** (misal: `4,0 Liter` atau `-` jika gravitasi/listrik).