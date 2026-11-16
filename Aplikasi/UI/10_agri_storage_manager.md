# Prompt Desain UI: Agri-Storage Manager (Stok Komoditas dan Gudang)

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, indikator kapasitas jelas), buatkan desain antarmuka untuk **Agri-Storage Manager** yang berfungsi untuk mencatat dan memantau jumlah stok hasil pertanian serta kapasitas tempat penyimpanan seperti gudang komoditas, gudang benih, dan silo.

## Spesifikasi Tata Letak & Komponen

1. **Top Header:**
   - Judul aplikasi: **Stok Komoditas & Gudang**.
   - Dua tombol aksi utama yang jelas:
     - Tombol Hijau Solid: `+ Stok Masuk`
     - Tombol Hijau Outline: `- Stok Keluar / Jual`

2. **Bagian Atas — Pemantauan Kapasitas Tempat Penyimpanan (Grid 3 Kartu):**
   Menampilkan kondisi daya tampung tiap fasilitas penyimpanan secara visual:
   - **Kartu 1: Gudang Komoditas Utama** (misal: `15,0 Ton / 20,0 Ton` • `75% Terisi` — *progress bar* hijau).
   - **Kartu 2: Gudang Benih & Saprotan** (misal: `1,8 Ton / 5,0 Ton` • `36% Terisi` — *progress bar* hijau).
   - **Kartu 3: Silo Pengering Gabah** (misal: `9,2 Ton / 10,0 Ton` • `92% Hampir Penuh` — *progress bar* amber peringatan).

3. **Bagian Bawah — Tabel Inventaris Stok:**
   - Tab filter kategori di atas tabel: `Semua Stok`, `Hasil Panen`, `Benih`, `Pupuk & Obat`.
   - Tabel bersih yang mudah dibaca dengan kolom:
     1. **Nama Komoditas / Barang** (misal: `Gabah Kering Giling (GKG) - Ciherang`, `Benih Jagung Bisi 18`)
     2. **Kategori** (*badge* lembut)
     3. **Lokasi Penyimpanan** (misal: `Gudang Komoditas Utama`)
     4. **Jumlah Stok Saat Ini** (angka tebal tabular, misal: `12.500 Kg` atau `250 Karung`)
     5. **Tanggal Masuk Terakhir**
     6. **Keterangan Kondisi / Kadar Air** (misal: `Kadar Air 13,5% • Baik`).