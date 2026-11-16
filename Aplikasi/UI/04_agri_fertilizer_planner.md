# Prompt Desain UI: Agri-Fertilizer Planner

Mengacu pada aturan dalam **Master Design System: Agri-Clean Minimalist** (Light Mode `#F8FAF8`, aksen Forest Sage Green `#2E7D32`, kartu putih bersih `#FFFFFF`, angka tabular), buatkan desain antarmuka untuk **Agri-Fertilizer Planner** yang digunakan untuk mengatur dan mencatat jadwal pemupukan, jenis pupuk, jumlah, cara pemberian, dan biaya.

## Spesifikasi Tata Letak & Komponen

1. **Top Header:**
   - Judul aplikasi: **Jadwal & Catatan Pemupukan**.
   - Pemilih filter musim tanam atau bulan.
   - Tombol aksi utama: `+ Catat Pemupukan`.

2. **Baris Ringkasan (3 KPI Cards):**
   - **Total Biaya Pupuk:** Total pengeluaran pupuk pada periode terpilih (contoh: `Rp 8.450.000`).
   - **Total Pupuk Digunakan:** Akumulasi berat dalam Kg atau Karung (contoh: `650 Kg / 13 Karung`).
   - **Jadwal Berikutnya:** Tanggal dan nama blok untuk pemupukan terdekat (contoh: `19 Nov • Blok A1`).

3. **Konten Utama — Tabel Pembukuan Pemupukan:**
   - Tab navigasi di atas tabel: `Semua Catatan`, `Jadwal Mendatang`, `Sudah Selesai`.
   - Tabel bersih dengan jarak baris lega yang memuat kolom:
     1. **Tanggal** (jadwal atau realisasi)
     2. **Lokasi Lahan / Blok**
     3. **Jenis Pupuk** (misal: `Urea`, `NPK Phonska`, `Pupuk Kandang`)
     4. **Jumlah / Dosis** (misal: `100 Kg`)
     5. **Cara Pemberian** (*badge* lembut: `Tabur`, `Kocor`, `Semprot Daun`)
     6. **Biaya Pupuk** (rata kanan, format Rupiah)
     7. **Status** (*badge* hijau `Selesai` atau kuning `Terjadwal` dengan tombol cepat tandai selesai).