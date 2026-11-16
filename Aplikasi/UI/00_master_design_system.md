# Master Design System: Agri-Clean Minimalist

Gunakan dokumen ini sebagai acuan utama (*system instruction* / panduan gaya global) saat merancang atau membangun antarmuka untuk ke-10 modul aplikasi AgriStation.

## 1. Filosofi & Prinsip UX
- **Sasaran Pengguna:** Petani dan pengelola lahan pertanian yang membutuhkan pencatatan pembukuan harian secara cepat, akurat, dan tanpa hambatan teknis.
- **Ultra-Clean & Minimalis:** Hindari elemen dekoratif berlebihan, animasi berat, atau kepadatan informasi yang membingungkan. Gunakan bahasa Indonesia yang lugas dan akrab di lapangan.
- **Ergonomis & Keterbacaan Tinggi:** Ukuran font besar (minimal `16px` untuk teks isi, `24px–32px` untuk angka ringkasan utama). Tombol aksi berukuran besar dengan jarak antar elemen yang lega agar nyaman digunakan di layar sentuh maupun di luar ruangan.
- **Hierarki Visual Tegas:** Informasi paling krusial (ringkasan angka, status peringatan, dan tombol tambah data) selalu berada di bagian atas layar.

## 2. Palet Warna (Strictly Light Mode)
> **Aturan Mutlak:** Dilarang menggunakan tema gelap (*dark mode*) atau latar belakang hitam pekat.

- **Latar Belakang Utama (*Canvas*):** `#F8FAF8` (Warm Alabaster / Off-White) — lembut di mata dan minim pantulan silau.
- **Permukaan Kartu (*Surface / Card*):** `#FFFFFF` (Pure White) dengan garis tepi tipis `#E2E8F0` dan bayangan sangat halus (`0 1px 3px rgba(0,0,0,0.05)`).
- **Warna Primer (Identitas & Aksi Utama):** `#2E7D32` / `#1B5E20` (Forest Sage Green) — memberikan kesan alami, tenang, dan terpercaya.
- **Warna Sekunder / Aksen Lembut:** `#E8F5E9` (Soft Mint) — digunakan untuk latar belakang *badge*, sorotan baris aktif, atau wadah ikon.
- **Warna Status Semantik (Kontras Tinggi):**
  - **Aman / Selesai / Siap Panen:** `#16A34A` (Emerald Green) dengan latar `#DCFCE7`
  - **Peringatan / Jadwal Dekat / Masa Tunggu (PHI):** `#D97706` (Turmeric Amber) dengan latar `#FEF3C7`
  - **Kritis / Stok Menipis / Rusak:** `#DC2626` (Terracotta Red) dengan latar `#FEE2E2`
- **Warna Teks:**
  - **Teks Utama / Judul:** `#1E293B` (Dark Charcoal)
  - **Teks Pendukung / Label:** `#64748B` (Slate Grey)

## 3. Tipografi & Komponen Standar
- **Jenis Huruf:** Sans-serif modern dengan keterbacaan tinggi (`Plus Jakarta Sans` atau `Inter`).
- **Format Angka:** Wajib menggunakan `tabular-nums` untuk seluruh nominal Rupiah, berat (Kg/Ton), luas (Ha), dan tanggal agar sejajar rapi dalam tabel.
- **Struktur Halaman Standar:**
  1. **Top Header:** Judul aplikasi, konteks tanggal/musim tanam, dan satu tombol aksi utama berwarna hijau (`+ Catat ...`).
  2. **KPI Summary Row:** 3 hingga 4 kartu ringkasan angka penting di bagian atas.
  3. **Filter Bar:** Tab berbentuk pil (*pill tabs*) untuk menyaring data dengan cepat.
  4. **Main Content Area:** Tabel pembukuan bersih (dengan baris bergantian sangat halus) atau kartu grid terstruktur (maksimal 2–3 kolom).