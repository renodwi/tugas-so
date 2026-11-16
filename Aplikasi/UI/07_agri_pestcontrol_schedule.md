# Prompt Desain UI: Agri-PestControl Schedule

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, warna peringatan kontras tinggi), buatkan desain antarmuka untuk **Agri-PestControl Schedule** untuk mengatur jadwal penyemprotan, mencatat pestisida, dosis, hama sasaran, serta memantau masa tunggu sebelum panen (*Pre-Harvest Interval* / PHI).

## Spesifikasi Tata Letak & Komponen

1. **Top Header:**
   - Judul aplikasi: **Jadwal Semprot & Pengendalian Hama**.
   - Filter status keamanan panen (`Semua Lahan`, `Dalam Masa Tunggu PHI`, `Aman Dipanen`).
   - Tombol aksi utama: `+ Catat Penyemprotan`.

2. **Banner Peringatan Masa Tunggu Panen (PHI Alert Banner):**
   - Kotak peringatan berwarna Amber lembut (`#FEF3C7` dengan teks `#D97706`) di bagian atas konten jika ada lahan yang baru disemprot dan belum boleh dipanen.
   - Contoh teks: *"Perhatian: Blok A1 dan Blok B2 masih dalam Masa Tunggu Panen (PHI). Aman dipanen kembali setelah tanggal 22 Nov 2026."*

3. **Konten Utama — Tabel & Log Penyemprotan:**
   - Tabel rapi yang memuat kolom:
     1. **Tanggal Semprot**
     2. **Blok Lahan**
     3. **Hama / Penyakit Sasaran** (misal: `Wereng Batang Coklat`, `Ulat Grayak`, `Blas Daun`)
     4. **Jenis & Merek Pestisida** (misal: `Insektisida Virtako`)
     5. **Dosis Aplikasi** (misal: `1,5 ml / Liter Air`)
     6. **Status Masa Tunggu (PHI):** Kolom paling menonjol dengan *badge* kuning **`Masa Tunggu: Sisa 5 Hari`** atau *badge* hijau **`Aman Dipanen`**.