# Prompt Desain UI: Agri-Finance Ledger

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, angka tabular tegas), buatkan desain antarmuka untuk **Agri-Finance Ledger** sebagai buku kas digital petani untuk mencatat pemasukan hasil panen, pengeluaran operasional, dan menghitung sisa saldo secara otomatis.

## Spesifikasi Tata Letak & Komponen

1. **Top Header:**
   - Judul aplikasi: **Buku Kas Pertanian**.
   - Filter periode: `Bulan Ini`, `Musim Tanam Ini`, `Semua Waktu`.
   - Dua tombol aksi utama yang kontras dan jelas:
     - Tombol Hijau Solid: `+ Catat Pemasukan`
     - Tombol Merah Terakota Outline/Solid: `- Catat Pengeluaran`

2. **Baris Ringkasan Keuangan (3 KPI Cards Besar):**
   - **Sisa Saldo Kas:** Kartu utama dengan sorotan bingkai hijau, angka sangat besar dan jelas (contoh: `Rp 32.750.000`).
   - **Total Pemasukan:** Menampilkan total uang masuk dari penjualan panen dengan teks hijau emerald (`+ Rp 48.000.000`).
   - **Total Pengeluaran:** Menampilkan total biaya operasional dengan teks merah terakota (`- Rp 15.250.000`).

3. **Konten Utama — Tabel Buku Kas Digital:**
   - Filter kategori sederhana (`Semua Transaksi`, `Penjualan Panen`, `Pupuk & Pestisida`, `Upah Tenaga`, `BBM & Perawatan`).
   - Tabel pembukuan standar yang mudah dibaca dan diaudit dengan kolom:
     1. **Tanggal**
     2. **Keterangan Transaksi** (misal: `Penjualan Padi Gabah Kering 2,5 Ton - Blok A1`)
     3. **Kategori** (*badge* abu-abu/hijau lembut)
     4. **Pemasukan** (warna hijau, rata kanan)
     5. **Pengeluaran** (warna merah terakota, rata kanan)
     6. **Saldo Berjalan** (teks gelap tebal, rata kanan).