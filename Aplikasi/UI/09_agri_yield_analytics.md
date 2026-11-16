# Prompt Desain UI: Agri-Yield Analytics

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, visualisasi data sederhana dan jelas), buatkan desain antarmuka untuk **Agri-Yield Analytics** yang digunakan petani untuk menganalisis jumlah hasil panen, produktivitas lahan (`Ton/Ha`), kualitas hasil panen (`Grade A/B/C`), dan pencapaian target panen.

## Spesifikasi Tata Letak & Komponen

1. **Top Header & Filter Analisis:**
   - Judul aplikasi: **Analisis Hasil Panen**.
   - Dropdown pemilih Komoditas (`Semua Komoditas`, `Padi`, `Jagung`) dan Musim Panen (`Musim Tanam II - 2026`).
   - Tombol aksi utama: `+ Input Hasil Panen`.

2. **Baris Ringkasan (4 KPI Cards):**
   - **Total Hasil Panen:** Berat total panen bersih (contoh: `28,4 Ton`).
   - **Produktivitas Rata-Rata:** Rasio hasil per luas lahan (contoh: `6,3 Ton / Ha`).
   - **Pencapaian Target:** Persentase realisasi dibanding target awal (contoh: `105% Tercapai` dengan *badge* hijau).
   - **Kualitas Utama:** Persentase hasil kualitas terbaik (contoh: `76% Grade A`).

3. **Bagian Visualisasi Sederhana (2 Kolom Sejajar):**
   - **Kolom Kiri — Perbandingan Target vs Realisasi Panen per Blok:**
     - Grafik batang vertikal minimalis yang sangat bersih. Membandingkan batang abu-abu lembut (`Target Ton`) dengan batang hijau sage (`Realisasi Ton`) untuk setiap blok lahan.
   - **Kolom Kanan — Rincian Kualitas Hasil Panen (Grade A / B / C):**
     - Tiga baris indikator kualitas dengan *progress bar* horizontal dan angka berat:
       - **Grade A (Kualitas Super):** Warna hijau emerald (`76% • 21,5 Ton`)
       - **Grade B (Kualitas Standar):** Warna kuning amber (`18% • 5,1 Ton`)
       - **Grade C (Sortiran / Afkir):** Warna abu-abu/merah lembut (`6% • 1,8 Ton`).

4. **Bagian Bawah — Tabel Ringkasan Panen per Lahan:**
   - Tabel ringkas memuat: Nama Blok, Luas (`Ha`), Target (`Ton`), Realisasi (`Ton`), Produktivitas (`Ton/Ha`), dan Rincian Grade.