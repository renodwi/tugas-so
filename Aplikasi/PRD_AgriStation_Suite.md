# Product Requirements Document (PRD)
# Suite Aplikasi Pertanian AgriStation

- **Dokumen ID:** PRD-AGRI-2026-001
- **Versi:** 1.0.0
- **Status:** Disetujui (Approved)
- **Bahasa:** Bahasa Indonesia (Standar ASD-STE100 Adaptation)
- **Tanggal Efektif:** 16 November 2026
- **Penulis:** Senior Product Manager & Technical Writer

---

## 1. Definisi Istilah (Glosarium)

Bagian ini mendefinisikan istilah resmi dalam dokumen. Seluruh spesifikasi wajib menggunakan istilah ini secara konsisten.

| Istilah | Definisi Resmi |
| :--- | :--- |
| **AgriStation** | Nama resmi suite aplikasi manajemen pertanian terpadu. |
| **Agent** | Sistem kecerdasan buatan otonom pelaksana tugas teknis pembangunan aplikasi. |
| **Plot / Lahan** | Petak bidang tanah pertanian yang memiliki batas fisik dan ukuran luas tertentu. |
| **HST** | Hari Setelah Tanam. Satuan hitung umur tanaman sejak bibit ditanam di lahan. |
| **PHI** | *Pre-Harvest Interval* (Masa Tunggu Panen). Jeda hari aman antara penyemprotan dan waktu panen. |
| **Alsintan** | Alat dan Mesin Pertanian mekanis (contoh: traktor, pompa air, mesin panen). |
| **Silo** | Tempat penyimpanan silinder berkapasitas besar khusus biji-bijian atau gabah. |
| **Grade A/B/C** | Klasifikasi mutu hasil panen berdasarkan parameter kebersihan, ukuran, dan kadar air. |
| **Paket .deb** | Format arsip perangkat lunak untuk sistem operasi Linux berbasis Debian atau Ubuntu. |
| **Database Terpusat** | Satu berkas basis data SQLite tunggal yang digunakan bersama oleh seluruh aplikasi. |

---

## 2. Ringkasan Proyek dan Tujuan

### 2.1 Ringkasan Proyek
AgriStation adalah kumpulan 10 aplikasi desktop mandiri untuk manajemen pertanian modern. Aplikasi berjalan pada sistem operasi Linux. Aplikasi menggunakan bahasa pemrograman Python. Seluruh aplikasi terintegrasi dengan satu database SQLite terpusat. Seluruh aplikasi didistribusikan dalam bentuk paket instalasi Debian (.deb).

### 2.2 Tujuan Produk
- **REQ-OBJ-001:** Sistem harus mendigitalkan seluruh catatan operasional budidaya pertanian harian.
- **REQ-OBJ-002:** Sistem harus menyediakan akses data terpadu tanpa ketergantungan koneksi internet (*offline-first*).
- **REQ-OBJ-003:** Sistem harus mencegah kegagalan panen akibat pelanggaran masa tunggu pestisida (PHI).
- **REQ-OBJ-004:** Sistem harus menghitung produktivitas panen dan arus kas keuangan secara otomatis.
- **REQ-OBJ-005:** Sistem harus menjamin keamanan data melalui mekanisme pencadangan lokal otomatis.

---

## 3. Ruang Lingkup (Scope of Work)

### 3.1 Cakupan Pekerjaan (In-Scope)
- **REQ-SCP-001:** Pembangunan 10 aplikasi desktop berbasis antarmuka grafis Python.
- **REQ-SCP-002:** Penggunaan satu basis data SQLite tunggal pada direktori data lokal terstandar.
- **REQ-SCP-003:** Penyediaan berkas konfigurasi UI merujuk pada direktori `UI/`.
- **REQ-SCP-004:** Penyediaan identitas visual aplikasi merujuk pada direktori `Maskot/`.
- **REQ-SCP-005:** Pembuatan berkas ikon berformat `.svg` untuk masing-masing aplikasi ke dalam direktori `Icon/`.
- **REQ-SCP-006:** Implementasi fitur cadangan (*backup*) data terjadwal, mandiri, dan fitur pemulihan (*restore*).
- **REQ-SCP-007:** Pembuatan berkas instalasi `.deb` untuk setiap aplikasi mandiri.
- **REQ-SCP-008:** Pengujian integritas basis data dan pengujian fungsi aplikasi.

### 3.2 Di Luar Cakupan (Out-of-Scope)
- **REQ-SCP-009:** Sinkronisasi basis data menuju peladen komputasi awan (*cloud server*).
- **REQ-SCP-010:** Aplikasi berbasis web peramban (*web browser application*).
- **REQ-SCP-011:** Aplikasi gawai pintar berbasis Android atau iOS.
- **REQ-SCP-012:** Integrasi perangkat keras sensor IoT secara waktu nyata (*real-time hardware streaming*).

---

## 4. Arsitektur Umum Sistem

### 4.1 Tumpukan Teknologi
- **Bahasa Inti:** Python versi 3.10 atau versi lebih tinggi.
- **Basis Data:** SQLite versi 3.35 atau versi lebih tinggi.
- **Antarmuka Grafis:** Pustaka GUI Python modern dengan dukungan tema terang (*Strict Light Mode*).
- **Distribusi:** Paket instalasi Debian Linux (`.deb`).
- **Format Aset Visual:** Ikon vektor SVG (*Scalable Vector Graphics*).

### 4.2 Struktur Direktori Proyek
Struktur repositori kerja diatur dengan hierarki berikut:

```text
/home/renodwi/Downloads/Aplikasi/
├── PRD_AgriStation_Suite.md        # Dokumen persyaratan produk terpusat
├── UI/                             # Spesifikasi panduan UI dan tata letak
│   ├── 00_master_design_system.md
│   ├── 01_agristation_main_dashboard.md
│   ├── 02_agri_crop_scheduler.md
│   ├── 03_agri_harvest_countdown.md
│   ├── 04_agri_fertilizer_planner.md
│   ├── 05_agri_finance_ledger.md
│   ├── 06_agri_irrigation_tracker.md
│   ├── 07_agri_pestcontrol_schedule.md
│   ├── 08_agri_equipment_log.md
│   ├── 09_agri_yield_analytics.md
│   └── 10_agri_storage_manager.md
├── Maskot/                         # Referensi ilustrasi maskot resmi
│   ├── file_000000002450821187ed2bce8b5c22a9.png
│   └── file_0000000066c08211af4f16efd77f56cf.png
├── Icon/                           # Direktori baru khusus ikon SVG aplikasi
│   ├── agristation-main-dashboard.svg
│   ├── agri-crop-scheduler.svg
│   ├── agri-harvest-countdown.svg
│   ├── agri-fertilizer-planner.svg
│   ├── agri-finance-ledger.svg
│   ├── agri-irrigation-tracker.svg
│   ├── agri-pestcontrol-schedule.svg
│   ├── agri-equipment-log.svg
│   ├── agri-yield-analytics.svg
│   └── agri-storage-manager.svg
├── apps/                           # Modul sumber kode aplikasi terpisah
├── database/                       # Skema migrasi dan utilitas SQLite
├── debian/                         # Konfigurasi pembuatan paket .deb
└── backups/                        # Direktori penyimpanan cadangan data lokal
```

### 4.3 Jalur Lokasi Data dan Berkas Konfigurasi
- **REQ-ARC-001:** Berkas basis data SQLite harus berada pada jalur `~/.local/share/agristation/agristation.db`.
- **REQ-ARC-002:** Berkas cadangan (*backup archive*) harus disimpan pada jalur `~/.local/share/agristation/backups/`.
- **REQ-ARC-003:** Berkas konfigurasi pengguna harus disimpan pada jalur `~/.config/agristation/`.
- **REQ-ARC-004:** Seluruh aplikasi harus membaca dan menulis pada berkas basis data terpusat yang sama.
- **REQ-ARC-005:** Setiap aplikasi adalah proses independen yang dapat dijalankan secara terpisah tanpa dependensi runtime aplikasi lain.

---

## 5. Spesifikasi Database Terpusat

### 5.1 Pengaturan Mesin Basis Data SQLite
- **REQ-DB-001:** Basis data wajib mengaktifkan mode *Write-Ahead Logging* (`PRAGMA journal_mode=WAL;`).
- **REQ-DB-002:** Basis data wajib menegakkan pemeriksaan kunci asing (`PRAGMA foreign_keys=ON;`).
- **REQ-DB-003:** Basis data harus menggunakan pengodean karakter UTF-8.
- **REQ-DB-004:** Setiap transaksi penulisan wajib menggunakan mekanisme transaksi atomik (`BEGIN IMMEDIATE`).

### 5.2 Daftar Tabel Basis Data Terpusat

Berikut adalah rincian 14 tabel terpusat yang menghubungkan ke-10 aplikasi AgriStation:

#### Tabel 1: `plots` (Daftar Lahan / Blok Sawah)
Menyimpan informasi identitas petak lahan fisik. Digunakan oleh Aplikasi 1, 2, 3, 4, 6, 7, 8, 9.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi unik lahan. |
| `plot_code` | TEXT | UNIQUE NOT NULL | Kode blok lahan (contoh: BLK-A1). |
| `plot_name` | TEXT | NOT NULL | Nama deskriptif blok lahan. |
| `area_ha` | REAL | NOT NULL CHECK(area_ha > 0) | Luas lahan dalam satuan Hektar. |
| `location_desc` | TEXT | NULL | Deskripsi lokasi geografis lahan. |
| `soil_type` | TEXT | NULL | Jenis tanah (lempung, aluvial, pasir). |
| `status` | TEXT | NOT NULL DEFAULT 'Aktif' | Status lahan ('Aktif', 'Persiapan', 'Istirahat'). |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pembaruan data terakhir. |

#### Tabel 2: `crops` (Tanaman dan Jadwal Budidaya)
Menyimpan riwayat musim tanam per petak lahan. Digunakan oleh Aplikasi 1, 2, 3, 4, 7, 9.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi unik tanaman. |
| `plot_id` | INTEGER | NOT NULL REFERENCES plots(id) | Relasi ke tabel lahan. |
| `crop_type` | TEXT | NOT NULL | Jenis tanaman (Padi, Jagung, Kedelai). |
| `variety` | TEXT | NOT NULL | Varietas tanaman (Ciherang, Bisi 18). |
| `planting_date` | TEXT | NOT NULL | Tanggal penanaman bibit (YYYY-MM-DD). |
| `est_harvest_date` | TEXT | NOT NULL | Estimasi tanggal panen (YYYY-MM-DD). |
| `current_stage` | TEXT | NOT NULL DEFAULT 'Tanam' | Fase ('Tanam', 'Vegetatif', 'Bunga', 'Siap Panen'). |
| `target_yield_ton` | REAL | NOT NULL DEFAULT 0.0 | Target tonase hasil panen. |
| `status` | TEXT | NOT NULL DEFAULT 'Sedang Tumbuh' | Status ('Sedang Tumbuh', 'Selesai Panen', 'Gagal'). |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pembaruan data terakhir. |

#### Tabel 3: `fertilizer_logs` (Catatan Pemupukan)
Menyimpan riwayat pemupukan berkala. Digunakan oleh Aplikasi 1, 4, 5.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi unik pemupukan. |
| `plot_id` | INTEGER | NOT NULL REFERENCES plots(id) | Relasi ke tabel lahan. |
| `crop_id` | INTEGER | NOT NULL REFERENCES crops(id) | Relasi ke tabel tanaman. |
| `application_date` | TEXT | NOT NULL | Tanggal pemupukan (YYYY-MM-DD). |
| `fertilizer_name` | TEXT | NOT NULL | Merek atau jenis pupuk (Urea, Phonska). |
| `quantity_kg` | REAL | NOT NULL CHECK(quantity_kg > 0) | Bobot pupuk dalam Kilogram. |
| `method` | TEXT | NOT NULL | Cara aplikasi ('Tabur', 'Kocor', 'Semprot Daun'). |
| `cost_idr` | REAL | NOT NULL CHECK(cost_idr >= 0) | Biaya pembelian pupuk dalam Rupiah. |
| `status` | TEXT | NOT NULL DEFAULT 'Terjadwal' | Status ('Terjadwal', 'Selesai'). |
| `notes` | TEXT | NULL | Catatan tambahan pelaksanaan. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

#### Tabel 4: `irrigation_logs` (Catatan Pengairan)
Menyimpan riwayat operasional pompa dan pasokan air. Digunakan oleh Aplikasi 1, 6.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi unik pengairan. |
| `plot_id` | INTEGER | NOT NULL REFERENCES plots(id) | Relasi ke tabel lahan. |
| `equipment_id` | INTEGER | NULL REFERENCES equipment(id) | Relasi ke tabel mesin pompa. |
| `irrigation_date` | TEXT | NOT NULL | Tanggal dan waktu mulai (YYYY-MM-DD HH:MM). |
| `duration_minutes` | INTEGER | NOT NULL CHECK(duration_minutes > 0) | Durasi pengairan dalam hitungan menit. |
| `water_source` | TEXT | NOT NULL | Sumber air ('Irigasi Teknis', 'Sumur Bor', 'Sungai', 'Embung'). |
| `pump_type` | TEXT | NOT NULL | Jenis pompa ('Diesel 3 Inch', 'Pompa Listrik', 'Gravitasi'). |
| `fuel_liters` | REAL | NOT NULL DEFAULT 0.0 CHECK(fuel_liters >= 0) | Volume konsumsi BBM solar dalam Liter. |
| `notes` | TEXT | NULL | Catatan kondisi debit air. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

#### Tabel 5: `pest_control_logs` (Catatan Pengendalian Hama & PHI)
Menyimpan riwayat penyemprotan dan batas keselamatan pangan. Digunakan oleh Aplikasi 1, 3, 7.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi unik penyemprotan. |
| `plot_id` | INTEGER | NOT NULL REFERENCES plots(id) | Relasi ke tabel lahan. |
| `crop_id` | INTEGER | NOT NULL REFERENCES crops(id) | Relasi ke tabel tanaman. |
| `spray_date` | TEXT | NOT NULL | Tanggal penyemprotan (YYYY-MM-DD). |
| `target_pest` | TEXT | NOT NULL | Nama hama atau penyakit sasaran. |
| `pesticide_name` | TEXT | NOT NULL | Nama merek dagang pestisida. |
| `dosage` | TEXT | NOT NULL | Takaran dosis (contoh: 1.5 ml/Liter). |
| `phi_days` | INTEGER | NOT NULL CHECK(phi_days >= 0) | Masa tunggu aman panen dalam hari. |
| `safe_harvest_date` | TEXT | NOT NULL | Tanggal aman panen (spray_date + phi_days). |
| `status` | TEXT | NOT NULL DEFAULT 'Masa Tunggu' | Status ('Masa Tunggu', 'Aman Dipanen'). |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

#### Tabel 6: `equipment` (Katalog Alat dan Mesin Pertanian)
Menyimpan data master alsintan. Digunakan oleh Aplikasi 1, 6, 8.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi unik alsintan. |
| `equipment_code` | TEXT | UNIQUE NOT NULL | Kode aset (contoh: TRK-01, PMP-02). |
| `name` | TEXT | NOT NULL | Nama dan tipe mesin (Traktor Quick G1000). |
| `category` | TEXT | NOT NULL | Kategori ('Traktor', 'Pompa Air', 'Sprayer', 'Combine'). |
| `status` | TEXT | NOT NULL DEFAULT 'Siap Pakai' | Kondisi ('Siap Pakai', 'Perlu Servis', 'Sedang Diperbaiki'). |
| `total_hours` | REAL | NOT NULL DEFAULT 0.0 | Total jam kerja operasional akumulatif. |
| `next_service_hours` | REAL | NOT NULL DEFAULT 50.0 | Jam kerja target servis rutin berikutnya. |
| `last_used_date` | TEXT | NULL | Tanggal terakhir mesin dioperasikan. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pembaruan data terakhir. |

#### Tabel 7: `equipment_usage_logs` (Riwayat Pemakaian Alsintan)
Menyimpan riwayat jam kerja harian mesin. Digunakan oleh Aplikasi 8.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci unik catatan pemakaian mesin. |
| `equipment_id` | INTEGER | NOT NULL REFERENCES equipment(id) | Relasi ke tabel alsintan. |
| `plot_id` | INTEGER | NOT NULL REFERENCES plots(id) | Relasi ke tabel lahan lokasi kerja. |
| `usage_date` | TEXT | NOT NULL | Tanggal operasional (YYYY-MM-DD). |
| `hours_used` | REAL | NOT NULL CHECK(hours_used > 0) | Durasi penggunaan dalam jam. |
| `operator_name` | TEXT | NOT NULL | Nama petugas operator mesin. |
| `activity_desc` | TEXT | NOT NULL | Jenis aktivitas olah tanah atau semprot. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

#### Tabel 8: `equipment_maintenance_logs` (Riwayat Servis Alsintan)
Menyimpan catatan pemeliharaan mesin. Digunakan oleh Aplikasi 5, 8.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci unik catatan servis mesin. |
| `equipment_id` | INTEGER | NOT NULL REFERENCES equipment(id) | Relasi ke tabel alsintan. |
| `service_date` | TEXT | NOT NULL | Tanggal pelaksanaan servis (YYYY-MM-DD). |
| `service_type` | TEXT | NOT NULL | Jenis ('Ganti Oli', 'Perbaikan Berat', 'Ganti Suku Cadang'). |
| `cost_idr` | REAL | NOT NULL CHECK(cost_idr >= 0) | Biaya jasa dan suku cadang dalam Rupiah. |
| `workshop_technician`| TEXT | NOT NULL | Bengkel pelaksana atau nama teknisi. |
| `notes` | TEXT | NULL | Uraian pekerjaan teknis. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

#### Tabel 9: `harvest_yields` (Catatan Panen dan Kualitas Mutu)
Menyimpan tonase panen dan sortasi kualitas. Digunakan oleh Aplikasi 1, 5, 9, 10.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci unik catatan hasil panen. |
| `crop_id` | INTEGER | NOT NULL REFERENCES crops(id) | Relasi ke tabel tanaman. |
| `plot_id` | INTEGER | NOT NULL REFERENCES plots(id) | Relasi ke tabel lahan. |
| `harvest_date` | TEXT | NOT NULL | Tanggal pelaksanaan panen (YYYY-MM-DD). |
| `total_yield_ton` | REAL | NOT NULL CHECK(total_yield_ton >= 0) | Berat kotor/bersih total hasil panen (Ton). |
| `productivity_ton_ha`| REAL | NOT NULL CHECK(productivity_ton_ha >= 0) | Hasil panen dibagi luas lahan (Ton/Ha). |
| `grade_a_ton` | REAL | NOT NULL DEFAULT 0.0 | Berat kualitas Super / Grade A (Ton). |
| `grade_b_ton` | REAL | NOT NULL DEFAULT 0.0 | Berat kualitas Standar / Grade B (Ton). |
| `grade_c_ton` | REAL | NOT NULL DEFAULT 0.0 | Berat kualitas Afkir / Grade C (Ton). |
| `target_ton` | REAL | NOT NULL DEFAULT 0.0 | Target acuan panen awal (Ton). |
| `achievement_pct` | REAL | NOT NULL DEFAULT 0.0 | Persentase realisasi terhadap target (%). |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

#### Tabel 10: `storage_locations` (Master Fasilitas Gudang dan Silo)
Menyimpan profil fisik gudang dan silo. Digunakan oleh Aplikasi 1, 10.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi fasilitas simpan. |
| `code` | TEXT | UNIQUE NOT NULL | Kode lokasi (GD-01, SL-01). |
| `name` | TEXT | NOT NULL | Nama fasilitas (Gudang Komoditas Utama, Silo Gabah). |
| `facility_type` | TEXT | NOT NULL | Kategori ('Gudang Komoditas', 'Gudang Benih', 'Silo'). |
| `capacity_ton` | REAL | NOT NULL CHECK(capacity_ton > 0) | Daya tampung maksimum (Ton). |
| `used_ton` | REAL | NOT NULL DEFAULT 0.0 | Bobot terisi saat ini (Ton). |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pembaruan data terakhir. |

#### Tabel 11: `storage_inventory` (Rincian Stok Barang dan Komoditas)
Menyimpan inventaris stok barang per gudang. Digunakan oleh Aplikasi 1, 10.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi unik item stok. |
| `storage_location_id`| INTEGER | NOT NULL REFERENCES storage_locations(id) | Relasi ke tabel fasilitas simpan. |
| `item_name` | TEXT | NOT NULL | Nama barang (Gabah Ciherang, Benih Jagung). |
| `category` | TEXT | NOT NULL | Kategori ('Hasil Panen', 'Benih', 'Pupuk', 'Obat'). |
| `quantity_kg` | REAL | NOT NULL CHECK(quantity_kg >= 0) | Bobot barang dalam Kilogram. |
| `package_count` | INTEGER | NOT NULL DEFAULT 0 | Jumlah kemasan fisik (karung/sak). |
| `moisture_pct` | REAL | NULL | Persentase kadar air gabah/biji (%). |
| `condition_status` | TEXT | NOT NULL DEFAULT 'Baik' | Kondisi fisik ('Baik', 'Lembab', 'Rusak'). |
| `last_in_date` | TEXT | NOT NULL | Tanggal barang masuk terakhir. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pembaruan data terakhir. |

#### Tabel 12: `storage_movements` (Mutasi Keluar-Masuk Stok)
Menyimpan riwayat penerimaan dan pengeluaran barang. Digunakan oleh Aplikasi 10.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci unik transaksi mutasi barang. |
| `storage_inventory_id`| INTEGER| NOT NULL REFERENCES storage_inventory(id) | Relasi ke inventaris barang. |
| `movement_type` | TEXT | NOT NULL | Arah barang ('Masuk', 'Keluar'). |
| `quantity_kg` | REAL | NOT NULL CHECK(quantity_kg > 0) | Bobot mutasi dalam Kilogram. |
| `movement_date` | TEXT | NOT NULL | Tanggal transaksi mutasi (YYYY-MM-DD). |
| `destination_or_source`| TEXT| NOT NULL | Penerima/pembeli atau asal blok panen. |
| `notes` | TEXT | NULL | Catatan transaksi mutasi. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

#### Tabel 13: `finance_transactions` (Buku Kas Keuangan)
Menyimpan seluruh transaksi debit dan kredit. Digunakan oleh Aplikasi 1, 4, 5, 8, 9, 10.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci unik catatan pembukuan kas. |
| `transaction_date` | TEXT | NOT NULL | Tanggal transaksi (YYYY-MM-DD). |
| `category` | TEXT | NOT NULL | Kategori ('Penjualan Panen', 'Pupuk', 'Upah', 'Servis'). |
| `transaction_type` | TEXT | NOT NULL | Aliran dana ('Pemasukan', 'Pengeluaran'). |
| `description` | TEXT | NOT NULL | Uraian penjelasan transaksi. |
| `amount_idr` | REAL | NOT NULL CHECK(amount_idr > 0) | Nominal nilai transaksi dalam Rupiah. |
| `source_module` | TEXT | NOT NULL | Asal aplikasi pelapor transaksi. |
| `ref_id` | INTEGER | NULL | Kunci rujukan tabel eksternal. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

#### Tabel 14: `daily_tasks` (Daftar Tugas Mandor Harian)
Menyimpan daftar tugas operasional. Digunakan oleh Aplikasi 1.

| Nama Kolom | Tipe Data | Batasan / Konstrain | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Kunci identifikasi tugas harian. |
| `task_date` | TEXT | NOT NULL | Tanggal pelaksanaan tugas (YYYY-MM-DD). |
| `task_title` | TEXT | NOT NULL | Ringkasan instruksi tugas. |
| `category` | TEXT | NOT NULL | Kategori tugas ('Pemupukan', 'Pengairan', 'Semprot'). |
| `plot_id` | INTEGER | NOT NULL REFERENCES plots(id) | Relasi ke blok lokasi tugas. |
| `is_completed` | INTEGER | NOT NULL DEFAULT 0 CHECK(is_completed IN (0,1)) | Status selesai (1 = Selesai, 0 = Belum). |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Waktu pencatatan data. |

### 5.3 Aturan Integritas Data dan Kunci Asing
- **REQ-DB-005:** Sistem dilarang menghapus data master plot jika plot masih terhubung pada musim tanam aktif (`ON DELETE RESTRICT`).
- **REQ-DB-006:** Penghitungan produktivitas panen pada tabel `harvest_yields` harus otomatis mengalikan tonase panen dibagi luas lahan dari tabel `plots`.
- **REQ-DB-007:** Setiap penambahan transaksi pengeluaran pupuk dari Aplikasi 4 harus otomatis memasukkan baris baru ke tabel `finance_transactions`.
- **REQ-DB-008:** Setiap penambahan transaksi biaya pemeliharaan mesin dari Aplikasi 8 harus otomatis memasukkan baris baru ke tabel `finance_transactions`.
- **REQ-DB-009:** Setiap mutasi pengeluaran penjualan barang pada Aplikasi 10 harus otomatis memperbarui kolom `used_ton` pada tabel `storage_locations`.

---

## 6. Fitur Backup dan Pemulihan (Backup & Restore)

### 6.1 Jadwal Pencadangan Data
- **REQ-BKP-001:** Sistem harus menjalankan pencadangan data otomatis setiap hari pada pukul 02:00 WIB menggunakan *systemd timer* atau penjadwal internal.
- **REQ-BKP-002:** Sistem wajib menyediakan tombol cadangkan mandiri (*manual on-demand backup*) pada setiap aplikasi.
- **REQ-BKP-003:** Sistem harus menyimpan riwayat cadangan selama 30 hari kalender terakhir secara bergulir (*rotation policy*).

### 6.2 Lokasi dan Penamaan Berkas Cadangan
- **REQ-BKP-004:** Berkas cadangan harus disimpan pada direktori aman `~/.local/share/agristation/backups/`.
- **REQ-BKP-005:** Format nama berkas cadangan harus menggunakan pola: `agristation_backup_YYYYMMDD_HHMMSS.tar.gz`.
- **REQ-BKP-006:** Setiap arsip cadangan harus disertai berkas tanda tangan kontrol integritas bertipe `agristation_backup_YYYYMMDD_HHMMSS.sha256`.

### 6.3 Prosedur Pemulihan Data (Restore Flow)
Agent dan sistem harus mematuhi alur bernomor berikut saat melakukan pemulihan basis data:
1. Periksa status berkas arsip `.tar.gz` pada direktori cadangan.
2. Hitung nilai *hash* SHA-256 dari berkas arsip cadangan.
3. Bandingkan nilai *hash* hasil perhitungan dengan isi berkas `.sha256`.
4. Hentikan seluruh koneksi aktif aplikasi menuju basis data utama `agristation.db`.
5. Buat salinan darurat dari berkas `agristation.db` aktif saat ini dengan nama `agristation.db.pre-restore`.
6. Ekstrak berkas `agristation.db` dari dalam arsip `.tar.gz` menuju lokasi sementara.
7. Jalankan perintah verifikasi integritas SQLite pada berkas hasil ekstraksi.
8. Ganti berkas basis data aktif dengan berkas hasil ekstraksi jika verifikasi sukses.
9. Pulihkan berkas `agristation.db.pre-restore` jika verifikasi menemukan kerusakan berkas.
10. Catat status pemulihan ke dalam catatan riwayat sistem (*system log*).

### 6.4 Verifikasi Integritas Data
- **REQ-BKP-007:** Sistem wajib menjalankan perintah `PRAGMA integrity_check;` terhadap basis data sebelum arsip cadangan ditutup.
- **REQ-BKP-008:** Sistem wajib membatalkan proses pencadangan jika hasil pemeriksaan integritas mengembalikan nilai selain `ok`.
- **REQ-BKP-009:** Sistem harus menampilkan dialog peringatan kritis kepada pengguna jika berkas cadangan gagal diverifikasi.

---

## 7. Spesifikasi per Aplikasi

Setiap aplikasi merupakan produk mandiri terpisah dengan berkas eksekusi masing-masing.

---

### 7.1 AgriStation Main Dashboard

#### A. Tujuan Produk
Menjadi pusat kendali operasional harian yang merangkum seluruh kondisi kebun, tugas kerja, dan peringatan kritis.

#### B. Pengguna Sasaran
Pemilik lahan, manajer perkebunan, dan ketua kelompok tani.

#### C. Fitur Utama
- **Widget Cuaca Lokal:** Menampilkan temperatur udara dan kondisi langit terkini.
- **4 Kartu KPI Atas:**
  1. Total Lahan Aktif (akumulasi luas Hektar dan jumlah plot).
  2. Kapasitas Gudang (persentase terisi dan indikator visual horizontal hijau).
  3. Panen Terdekat (nama komoditas dan hitung mundur sisa hari).
  4. Saldo Kas Bulan Ini (sisa nominal kas dalam format Rupiah).
- **Daftar Tugas Harian:** *Checklist* interaktif berisi nama kegiatan, lokasi blok, dan label kategori.
- **Ringkasan Kondisi Lahan:** Kartu blok lahan aktif dengan penanda peringatan amber jika mendekati masa panen atau masa tunggu semprot.
- **Tombol Tambah Aktivitas:** Tombol hijau cepat untuk mencatat kegiatan harian baru.

#### D. Data Input dan Output
- **Input:** Centang status tugas harian, input aktivitas harian baru.
- **Output:** Agregasi metriks lahan, kapasitas gudang, tanggal panen terdekat, sisa kas, dan cuaca.

#### E. Aturan Bisnis
- **REQ-APP01-001:** Kartu panen terdekat harus mengambil data tanaman dengan estimasi panen paling dekat dari tanggal hari ini.
- **REQ-APP01-002:** Tugas harian yang dicentang selesai harus memperbarui kolom `is_completed` pada tabel `daily_tasks`.
- **REQ-APP01-003:** Peringatan warna amber wajib tampil jika terdapat blok yang berada dalam masa tunggu PHI pestisida.

#### F. Kriteria Penerimaan
- **REQ-APP01-004:** Aplikasi menampilkan 4 kartu KPI sesuai data riil pada database dalam waktu kurang dari 1 detik.
- **REQ-APP01-005:** Aplikasi menerapkan palet Light Mode (#F8FAF8) sesuai berkas `UI/01_agristation_main_dashboard.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP01-006:** Berkas ikon wajib disimpan dengan nama `Icon/agristation-main-dashboard.svg`.
- **REQ-APP01-007:** Ikon harus menampilkan ilustrasi visual dasbor pemantauan pertanian dengan siluet daun dan kartu metrik.

---

### 7.2 Agri-Crop Scheduler

#### A. Tujuan Produk
Mencatat data petak lahan fisik, jenis tanaman, varietas benih, tanggal tanam, dan menghitung estimasi panen.

#### B. Pengguna Sasaran
Petani pelaksana, agronom lapangan, dan pengelola rotasi tanam.

#### C. Fitur Utama
- **Filter Pil Cepat (*Pill Tabs*):** Navigasi penyaringan plot (`Semua Plot`, `Sedang Tumbuh`, `Persiapan Lahan`, `Selesai Panen`).
- **3 Kartu KPI Atas:** Total Plot Aktif, Total Luas Tertanam (Ha), dan Komoditas Terbanyak.
- **Grid Kartu Plot Tanam:** Kartu petak dua kolom memuat nama blok, luas, varietas benih, tanggal tanam, dan estimasi panen.
- **Formulir Pendaftaran Plot:** Modal dialog input untuk menambah plot dan masa tanam baru.

#### D. Data Input dan Output
- **Input:** Nama lahan, luas (Ha), jenis tanaman, nama varietas, tanggal tanam, estimasi panen.
- **Output:** Daftar visual status plot, agregasi luas garapan, jadwal panen terencana.

#### E. Aturan Bisnis
- **REQ-APP02-001:** Luas lahan yang dimasukkan wajib bernilai lebih besar dari 0 Hektar.
- **REQ-APP02-002:** Estimasi tanggal panen harus berupa tanggal setelah tanggal penanaman.
- **REQ-APP02-003:** Perubahan status plot menjadi 'Selesai Panen' harus memperbarui tabel `crops` dan membuka status lahan untuk persiapan musim tanam berikutnya.

#### F. Kriteria Penerimaan
- **REQ-APP02-004:** Formulir input menolak penyimpanan data jika kolom wajib kosong.
- **REQ-APP02-005:** Tampilan antarmuka mematuhi spesifikasi `UI/02_agri_crop_scheduler.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP02-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-crop-scheduler.svg`.
- **REQ-APP02-007:** Ikon harus menampilkan metafora kalender jadwal, garis pematang sawah, dan tunas tanaman hijau.

---

### 7.3 Agri-Harvest Countdown

#### A. Tujuan Produk
Menghitung sisa hari menuju panen dan memvisualisasikan fase pertumbuhan tanaman dengan bilah kemajuan (*progress bar*).

#### B. Pengguna Sasaran
Petani pemantau masa panen, mandor panen, dan perencana logistik tebas panen.

#### C. Fitur Utama
- **Penyortiran Jadwal:** Pilihan sortir berdasarkan panen paling dekat atau waktu tanam terbaru.
- **Kartu Progres Pertumbuhan:**
  - Header kartu memuat nama blok, varietas, dan teks hitung mundur mencolok (contoh: `5 Hari Lagi`).
  - Label badge hijau solid `SIAP PANEN` jika sisa hari bernilai 0.
  - Bilah kemajuan horizontal tebal (`height: 14px`) berwarna hijau sage.
  - Penanda 4 fase tumbuh: Tanam -> Vegetatif -> Berbuah/Bunga -> Siap Panen.
  - Informasi umur tanaman dalam satuan Hari Setelah Tanam (HST).

#### D. Data Input dan Output
- **Input:** Perubahan fase tumbuh tanaman, penyesuaian target panen.
- **Output:** Bilah kemajuan persentase umur tanaman, angka sisa hari hitung mundur, status kesiapan panen.

#### E. Aturan Bisnis
- **REQ-APP03-001:** Persentase kemajuan dihitung dari: `(Tanggal Hari Ini - Tanggal Tanam) / (Estimasi Panen - Tanggal Tanam) * 100%`.
- **REQ-APP03-002:** Nilai persentase dilarang melebihi 100%.
- **REQ-APP03-003:** Jika hari ini melewati estimasi panen, sistem harus menampilkan status terlambat panen dengan warna amber menyala.

#### F. Kriteria Penerimaan
- **REQ-APP03-004:** Nilai HST bertambah secara otomatis setiap pergantian tanggal kalender sistem.
- **REQ-APP03-005:** Tampilan antarmuka mematuhi spesifikasi `UI/03_agri_harvest_countdown.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP03-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-harvest-countdown.svg`.
- **REQ-APP03-007:** Ikon harus menampilkan simbol penghitung waktu mundur jam pasir atau *stopwatch* dengan latar tanaman padi matang.

---

### 7.4 Agri-Fertilizer Planner

#### A. Tujuan Produk
Mengatur jadwal pemupukan, menghitung kebutuhan dosis nutrisi tanaman, cara aplikasi, dan mengontrol pengeluaran biaya pupuk.

#### B. Pengguna Sasaran
Pengelola nutrisi tanaman, staf gudang saprotan, dan petani.

#### C. Fitur Utama
- **3 Kartu KPI Atas:** Total Biaya Pupuk (Rupiah), Total Pupuk Digunakan (Kg/Karung), dan Jadwal Pemupukan Terdekat.
- **Filter Tab Jadwal:** Pilihan penyaringan (`Semua Catatan`, `Jadwal Mendatang`, `Sudah Selesai`).
- **Tabel Catatan Pemupukan:** Kolom tanggal, lokasi blok lahan, jenis pupuk, jumlah/dosis, metode aplikasi, biaya, dan status.
- **Aksi Cepat Selesai:** Tombol untuk menandai jadwal pemupukan yang telah diaplikasikan di lapangan.

#### D. Data Input dan Output
- **Input:** Lokasi blok, tanaman sasaran, tanggal pemupukan, nama pupuk, jumlah (Kg), metode, biaya (Rp).
- **Output:** Jadwal kerja pemupukan, total akumulasi biaya pupuk, agregasi kebutuhan fisik pupuk.

#### E. Aturan Bisnis
- **REQ-APP04-001:** Setiap penandaan status pupuk 'Selesai' wajib mencatat pengeluaran uang secara otomatis ke tabel `finance_transactions`.
- **REQ-APP04-002:** Metode aplikasi wajib terbatas pada tiga pilihan standar: 'Tabur', 'Kocor', atau 'Semprot Daun'.
- **REQ-APP04-003:** Nilai biaya pemupukan dilarang bernilai negatif.

#### F. Kriteria Penerimaan
- **REQ-APP04-004:** Format angka rupiah pada tabel menggunakan format angka moneter rata kanan (`tabular-nums`).
- **REQ-APP04-005:** Tampilan antarmuka mematuhi spesifikasi `UI/04_agri_fertilizer_planner.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP04-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-fertilizer-planner.svg`.
- **REQ-APP04-007:** Ikon harus menampilkan ilustrasi karung pupuk pertanian dan butiran mineral tanaman hijau.

---

### 7.5 Agri-Finance Ledger

#### A. Tujuan Produk
Menyediakan pembukuan kas digital untuk mencatat arus masuk hasil penjualan panen dan seluruh pengeluaran operasional usaha tani.

#### B. Pengguna Sasaran
Petani pemilik, bendahara kelompok tani, dan manajer keuangan agribisnis.

#### C. Fitur Utama
- **3 Kartu Saldo Kas Besar:** Sisa Saldo Kas (sorotan hijau), Total Pemasukan (+ Rp), dan Total Pengeluaran (- Rp).
- **Tombol Transaksi Ganda:** Tombol Hijau `+ Catat Pemasukan` dan Tombol Terakota `- Catat Pengeluaran`.
- **Filter Kategori Pembukuan:** Tab filter cepat (`Semua Transaksi`, `Penjualan Panen`, `Pupuk & Obat`, `Upah Tenaga`, `BBM & Perawatan`).
- **Tabel Buku Kas Standar:** Kolom tanggal, keterangan transaksi, lencana kategori, nominal pemasukan hijau, nominal pengeluaran merah, dan saldo berjalan.

#### D. Data Input dan Output
- **Input:** Tanggal, tipe transaksi, kategori belanja, deskripsi transaksi, nominal Rupiah.
- **Output:** Total laba/rugi kotor, sisa saldo kas riil, riwayat mutasi keuangan terperinci.

#### E. Aturan Bisnis
- **REQ-APP05-001:** Saldo berjalan dihitung dari rumus: `Saldo Sebelumnya + Pemasukan - Pengeluaran`.
- **REQ-APP05-002:** Nominal transaksi wajib bernilai lebih besar dari 0 Rupiah.
- **REQ-APP05-003:** Transaksi yang telah disimpan dilarang dihapus tanpa konfirmasi ganda oleh pengguna demi menjaga jejak audit (*audit trail*).

#### F. Kriteria Penerimaan
- **REQ-APP05-004:** Tabel mampu memuat 1.000 baris transaksi dengan penelusuran lancar tanpa kendala jeda visual.
- **REQ-APP05-005:** Tampilan antarmuka mematuhi spesifikasi `UI/05_agri_finance_ledger.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP05-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-finance-ledger.svg`.
- **REQ-APP05-007:** Ikon harus menampilkan simbol buku kas pembukuan dengan lambang mata uang dan daun tunas.

---

### 7.6 Agri-Irrigation Tracker

#### A. Tujuan Produk
Mencatat kegiatan pengairan lahan, durasi pasokan air, sumber pasokan, tipe pompa air, dan menghitung efisiensi bahan bakar (BBM).

#### B. Pengguna Sasaran
Operator pompa irigasi, petugas pengairan sawah (*ulu-ulu*), dan mandor perkebunan.

#### C. Fitur Utama
- **3 Kartu KPI Atas:** Total Durasi Pengairan Bulan Ini (Jam:Menit), Penggunaan Bahan Bakar (Liter Solar), dan Pengairan Terakhir.
- **Filter Blok Lahan:** Dropdown untuk menyaring riwayat pengairan per blok sawah.
- **Tabel Riwayat Pengairan:** Kolom tanggal/waktu, lokasi lahan, lencana sumber air, jenis pompa, lama pengairan, dan pemakaian BBM.
- **Formulir Catat Pengairan:** Dialog pencatatan pengairan baru lengkap dengan kalkulator menit.

#### D. Data Input dan Output
- **Input:** Blok lahan, waktu mulai, durasi menit, sumber air, mesin pompa yang digunakan, volume konsumsi BBM (liter).
- **Output:** Akumulasi jam pompa, konsumsi total BBM solar, frekuensi kebasahan blok lahan.

#### E. Aturan Bisnis
- **REQ-APP06-001:** Jika sumber air dipilih 'Gravitasi', maka kolom bahan bakar otomatis bernilai 0 liter.
- **REQ-APP06-002:** Durasi pengairan wajib bernilai minimal 1 menit.
- **REQ-APP06-003:** Penggunaan pompa mekanis harus memperbarui akumulasi jam operasional pada mesin terkait di tabel `equipment`.

#### F. Kriteria Penerimaan
- **REQ-APP06-004:** Kolom pemakaian bahan bakar menampilkan tanda garis strip (-) jika pengairan dilakukan tanpa mesin berbahan bakar.
- **REQ-APP06-005:** Tampilan antarmuka mematuhi spesifikasi `UI/06_agri_irrigation_tracker.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP06-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-irrigation-tracker.svg`.
- **REQ-APP06-007:** Ikon harus menampilkan elemen tetesan air bersih, saluran irigasi sawah, dan roda mesin pompa.

---

### 7.7 Agri-PestControl Schedule

#### A. Tujuan Produk
Menjadwalkan penyemprotan perlindungan tanaman, mencatat dosis pestisida, mengidentifikasi hama, dan mengawal masa tunggu panen (*Pre-Harvest Interval* / PHI).

#### B. Pengguna Sasaran
Petugas pengendali organisme pengganggu tumbuhan (POPT), aplikator pestisida, dan mandor kebun.

#### C. Fitur Utama
- **Banner Peringatan PHI Kontras Tinggi:** Banner warna Amber (`#FEF3C7` teks `#D97706`) di bagian atas jika ada lahan dalam masa tunggu pestisida.
- **Filter Keamanan Lahan:** Tab filter (`Semua Lahan`, `Dalam Masa Tunggu PHI`, `Aman Dipanen`).
- **Tabel Log Penyemprotan:** Kolom tanggal semprot, blok lahan, hama sasaran, jenis & merek pestisida, dosis aplikasi, dan lencana status PHI.
- **Lencana Status Dinamis:** Status `Masa Tunggu: Sisa X Hari` (kuning) atau `Aman Dipanen` (hijau).

#### D. Data Input dan Output
- **Input:** Blok lahan, tanaman, tanggal semprot, target hama, nama pestisida, dosis, jumlah hari masa tunggu (PHI).
- **Output:** Tanggal aman panen terhitung, peringatan larangan panen dini, riwayat aplikasi pestisida.

#### E. Aturan Bisnis
- **REQ-APP07-001:** Tanggal aman panen dihitung otomatis: `Tanggal Semprot + Angka Hari PHI`.
- **REQ-APP07-002:** Jika tanggal hari ini masih sebelum tanggal aman panen, status lahan wajib dikunci pada status 'Masa Tunggu'.
- **REQ-APP07-003:** Sistem harus mengirim sinyal larangan panen ke Aplikasi 3 (Harvest Countdown) selama status PHI belum selesai.

#### F. Kriteria Penerimaan
- **REQ-APP07-004:** Banner peringatan PHI otomatis menghilang jika seluruh blok lahan telah melewati tanggal aman panen.
- **REQ-APP07-005:** Tampilan antarmuka mematuhi spesifikasi `UI/07_agri_pestcontrol_schedule.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP07-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-pestcontrol-schedule.svg`.
- **REQ-APP07-007:** Ikon harus menampilkan siluet nosel semprotan (*sprayer nozzle*), perisai pelindung daun, dan simbol tanda seru aman.

---

### 7.8 Agri-Equipment Log

#### A. Tujuan Produk
Mendata inventaris alat dan mesin pertanian (alsintan), mencatat total jam kerja, melacak riwayat pemakaian, dan mengatur jadwal perawatan mesin.

#### B. Pengguna Sasaran
Mekanik bengkel tani, operator traktor, dan manajer aset perkebunan.

#### C. Fitur Utama
- **3 Kartu KPI Atas:** Total Unit Alsintan, Kondisi Siap Pakai (hijau), dan Perlu Perawatan/Servis (merah/kuning).
- **Filter Status Kondisi:** Filter pil (`Semua Unit`, `Siap Pakai`, `Perlu Servis`, `Sedang Diperbaiki`).
- **Katalog Alsintan Tiga Kolom:** Kartu unit mesin memuat nama, nomor seri, lencana status, jam operasi, riwayat terakhir, dan kotak peringatan jadwal servis berikutnya.
- **Tombol Aksi Kartu Ganda:** Tombol `+ Catat Pakai` dan `Log Servis` pada masing-masing kartu mesin.

#### D. Data Input dan Output
- **Input:** Pendaftaran unit mesin baru, catatan jam pemakaian harian, catatan penggantian oli dan suku cadang.
- **Output:** Total akumulasi jam mesin, status kelayakan alat, pengingat jatuh tempo servis berkala.

#### E. Aturan Bisnis
- **REQ-APP08-001:** Jika jam kerja mesin melampaui ambang batas `next_service_hours`, sistem otomatis mengubah status mesin menjadi 'Perlu Servis'.
- **REQ-APP08-002:** Pencatatan servis rutin harus memperbarui nilai `next_service_hours` sebesar 50 jam operasional ke depan secara otomatis.
- **REQ-APP08-003:** Biaya perawatan mesin yang dicatat wajib otomatis dimasukkan ke tabel `finance_transactions`.

#### F. Kriteria Penerimaan
- **REQ-APP08-004:** Pengguna dapat memperbarui status mesin secara instan dari dialog pop-up.
- **REQ-APP08-005:** Tampilan antarmuka mematuhi spesifikasi `UI/08_agri_equipment_log.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP08-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-equipment-log.svg`.
- **REQ-APP08-007:** Ikon harus menampilkan siluet traktor roda pertanian bergaya minimalis dipadukan dengan roda gigi industri (*gear*).

---

### 7.9 Agri-Yield Analytics

#### A. Tujuan Produk
Menganalisis hasil produksi panen bersih, menghitung produktivitas per satuan luas lahan (Ton/Ha), memantau komposisi mutu panen (Grade A/B/C), dan mengukur pencapaian target.

#### B. Pengguna Sasaran
Analis produksi agribisnis, manajer operasional, dan pemilik usaha perkebunan.

#### C. Fitur Utama
- **Dropdown Filter Analisis:** Pemilih komoditas tanaman dan periode musim panen.
- **4 Kartu KPI Atas:** Total Hasil Panen (Ton), Produktivitas Rata-rata (Ton/Ha), Pencapaian Target (% Tercapai), dan Kualitas Utama (% Grade A).
- **Grafik Batang Perbandingan Target vs Realisasi:** Diagram batang minimalis membandingkan target panen (abu-abu) dan realisasi tonase panen (hijau sage) per blok lahan.
- **Bilah Komposisi Mutu Tiga Lapis:** Tiga bilah kemajuan horizontal untuk Grade A (Super - Emerald), Grade B (Standar - Amber), dan Grade C (Afkir - Merah muda/abu-abu).
- **Tabel Ringkasan Panen per Lahan:** Kolom nama blok, luas (Ha), target (Ton), realisasi (Ton), produktivitas (Ton/Ha), dan rincian grade.

#### D. Data Input dan Output
- **Input:** Masukan data hasil panen (berat bersih, pembagian berat Grade A, B, dan C per petak lahan).
- **Output:** Angka produktivitas ton per hektar, persentase keberhasilan target panen, sebaran mutu komoditas.

#### E. Aturan Bisnis
- **REQ-APP09-001:** Penjumlahan bobot `grade_a_ton + grade_b_ton + grade_c_ton` harus sama dengan nilai `total_yield_ton`.
- **REQ-APP09-002:** Nilai produktivitas dihitung otomatis: `total_yield_ton / area_ha`.
- **REQ-APP09-003:** Persentase pencapaian target dihitung: `(total_yield_ton / target_ton) * 100%`.

#### F. Kriteria Penerimaan
- **REQ-APP09-004:** Visualisasi diagram batang dapat diakses dengan jelas tanpa memerlukan koneksi pustaka pihak ketiga berbasis daring.
- **REQ-APP09-005:** Tampilan antarmuka mematuhi spesifikasi `UI/09_agri_yield_analytics.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP09-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-yield-analytics.svg`.
- **REQ-APP09-007:** Ikon harus menampilkan grafik batang analitik meningkat dengan simbol lencana bintang atau timbangan panen.

---

### 7.10 Agri-Storage Manager

#### A. Tujuan Produk
Mencatat stok hasil pertanian dan sarana produksi, memantau daya tampung fasilitas penyimpanan (gudang komoditas, gudang benih, dan silo pengering), serta melacak keluar-masuk komoditas.

#### B. Pengguna Sasaran
Kepala pergudangan pertanian, pengelola logistik, dan pengawas inventaris pascapanen.

#### C. Fitur Utama
- **Tombol Transaksi Mutasi:** Tombol Hijau Solid `+ Stok Masuk` dan Tombol Hijau Garis Tepi `- Stok Keluar / Jual`.
- **3 Kartu Pemantau Kapasitas Fasilitas:**
  1. Gudang Komoditas Utama (Kapasitas, Terisi, % Bilah Kemajuan).
  2. Gudang Benih & Saprotan (Kapasitas, Terisi, % Bilah Kemajuan).
  3. Silo Pengering Gabah (Kapasitas, Terisi, % Bilah Kemajuan Peringatan Amber jika hampir penuh).
- **Filter Kategori Stok:** Tab pilihan (`Semua Stok`, `Hasil Panen`, `Benih`, `Pupuk & Obat`).
- **Tabel Inventaris Barang:** Kolom nama komoditas/barang, kategori, lokasi penyimpanan, jumlah stok (angka tabular tebal Kg/Karung), tanggal masuk terakhir, dan keterangan kondisi fisik/kadar air (%).

#### D. Data Input dan Output
- **Input:** Registrasi barang masuk, pencatatan komoditas keluar untuk penjualan, pembaruan kadar air lab.
- **Output:** Kapasitas sisa gudang, daftar inventaris aktif, peringatan gudang penuh (*overcapacity*).

#### E. Aturan Bisnis
- **REQ-APP10-001:** Penambahan stok baru dilarang melebihi sisa kapasitas maksimum fasilitas penyimpanan yang bersangkutan.
- **REQ-APP10-002:** Pengeluaran stok dilarang melebihi jumlah saldo barang yang tersedia di lokasi terpilih.
- **REQ-APP10-003:** Komoditas gabah dengan kadar air di atas 14% harus menampilkan label peringatan berwarna kuning pada kolom kondisi.

#### F. Kriteria Penerimaan
- **REQ-APP10-004:** Bilah kapasitas gudang otomatis berubah warna menjadi merah jika kapasitas terisi mencapai 95% atau lebih.
- **REQ-APP10-005:** Tampilan antarmuka mematuhi spesifikasi `UI/10_agri_storage_manager.md`.

#### G. Persyaratan Ikon SVG
- **REQ-APP10-006:** Berkas ikon wajib disimpan dengan nama `Icon/agri-storage-manager.svg`.
- **REQ-APP10-007:** Ikon harus menampilkan siluet bangunan gudang lumbung pertanian dengan silo silindris dan tumpukan karung panen.

---

## 8. Ringkasan Matriks Spesifikasi 10 Aplikasi

Tabel berikut merangkum kesepuluh aplikasi mandiri dalam suite AgriStation:

| No | Nama Aplikasi | Berkas UI Acuan | Berkas Ikon SVG | Entitas Data Utama |
| :---: | :--- | :--- | :--- | :--- |
| 1 | AgriStation Main Dashboard | `UI/01_agristation_main_dashboard.md` | `Icon/agristation-main-dashboard.svg` | Agregasi Lahan, Kas, Gudang, Tugas |
| 2 | Agri-Crop Scheduler | `UI/02_agri_crop_scheduler.md` | `Icon/agri-crop-scheduler.svg` | Plot Lahan, Tanaman, Varietas |
| 3 | Agri-Harvest Countdown | `UI/03_agri_harvest_countdown.md` | `Icon/agri-harvest-countdown.svg` | Umur Tanaman, HST, Sisa Hari |
| 4 | Agri-Fertilizer Planner | `UI/04_agri_fertilizer_planner.md` | `Icon/agri-fertilizer-planner.svg` | Pupuk, Dosis, Cara, Biaya |
| 5 | Agri-Finance Ledger | `UI/05_agri_finance_ledger.md` | `Icon/agri-finance-ledger.svg` | Kas Masuk, Kas Keluar, Saldo |
| 6 | Agri-Irrigation Tracker | `UI/06_agri_irrigation_tracker.md` | `Icon/agri-irrigation-tracker.svg` | Durasi Pompa, Air, Bahan Bakar |
| 7 | Agri-PestControl Schedule | `UI/07_agri_pestcontrol_schedule.md` | `Icon/agri-pestcontrol-schedule.svg` | Pestisida, Hama, Tanggal Aman PHI |
| 8 | Agri-Equipment Log | `UI/08_agri_equipment_log.md` | `Icon/agri-equipment-log.svg` | Alsintan, Jam Operasi, Jadwal Servis |
| 9 | Agri-Yield Analytics | `UI/09_agri_yield_analytics.md` | `Icon/agri-yield-analytics.svg` | Tonase Panen, Ton/Ha, Grade A/B/C |
| 10| Agri-Storage Manager | `UI/10_agri_storage_manager.md` | `Icon/agri-storage-manager.svg` | Gudang, Silo, Stok Masuk/Keluar |

---

## 9. Alur Kerja Agent (Instruksi Langkah Operasional)

Agent pelaksana wajib mengikuti langkah-langkah kerja bernomor berikut secara urut dan tertib:

1. **Baca Spesifikasi UI dan Referensi Maskot:**
   Buka dan pelajari seluruh berkas spesifikasi antarmuka di dalam folder `UI/`. Buka dan teliti referensi visual maskot resmi di dalam folder `Maskot/`.
2. **Buat Direktori Ikon Baru:**
   Buat folder baru bernama `Icon/` pada tingkat utama repositori kerja.
3. **Desain dan Simpan Ikon SVG Tiap Aplikasi:**
   Buat 10 berkas ikon berformat `.svg` berkualitas tinggi di dalam folder `Icon/`. Pastikan setiap ikon merepresentasikan fungsi spesifik aplikasi dan selaras dengan gaya maskot serta tema warna *Forest Sage Green* (`#2E7D32`).
4. **Bangun Struktur Aplikasi Python Mandiri:**
   Bangun arsitektur perangkat lunak untuk ke-10 modul aplikasi Python. Pertahankan pemisahan kode yang bersih dan pastikan setiap aplikasi dapat dijalankan secara terpisah.
5. **Inisialisasi Database Terpusat:**
   Buat skema basis data SQLite terpusat sesuai 14 tabel yang ditetapkan dalam PRD ini. Aktifkan mode WAL dan verifikasi seluruh integritas relasi kunci asing.
6. **Integrasikan Fitur Backup dan Restore:**
   Implementasikan modul pencadangan data otomatis harian dan tombol pencadangan manual. Uji coba proses verifikasi integritas berkas cadangan menggunakan SHA-256 dan perintah integritas SQLite.
7. **Terapkan Master Design System:**
   Terapkan tampilan tema terang (*Strict Light Mode*) pada antarmuka ke-10 aplikasi sesuai pedoman berkas `UI/00_master_design_system.md`. Pastikan tipografi, warna semantik, dan angka tabular konsisten.
8. **Bangun Paket Instalasi Debian (.deb):**
   Susun skrip pengemasan dan bangun berkas paket instalasi `.deb` untuk setiap aplikasi agar dapat dipasang pada sistem operasi Linux.
9. **Jalankan Pengujian Validasi Sistem:**
   Jalankan pengujian menyeluruh terhadap ke-10 aplikasi. Uji interaksi database bersama, kebenaran kalkulasi data, dan kestabilan antarmuka pengguna.
10. **Susun Dokumentasi Serah Terima:**
    Selesaikan dokumentasi teknis instalasi dan laporkan hasil pengujian sistem kepada pemilik produk.

---

## 10. Persyaratan Non-Fungsional (NFR)

### 10.1 Kinerja (Performance)
- **REQ-NFR-001:** Setiap aplikasi harus dapat terbuka dan menampilkan layar utama dalam waktu kurang dari 2 detik pada spesifikasi komputer standar (RAM 4GB, CPU dual-core).
- **REQ-NFR-002:** Eksekusi kueri pembacaan data pada basis data SQLite harus selesai dalam waktu kurang dari 200 milidetik untuk 50.000 baris data.
- **REQ-NFR-003:** Konsumsi memori RAM setiap aplikasi dilarang melebihi 150 MB saat kondisi operasional normal.

### 10.2 Keamanan Data (Data Security)
- **REQ-NFR-004:** Berkas basis data harus memiliki hak akses berkas terbatas (*file permission 0600*) agar tidak dapat dibaca oleh pengguna Linux lain tanpa hak akses.
- **REQ-NFR-005:** Sistem dilarang mengirimkan data pertanian pengguna ke jaringan publik luar tanpa persetujuan eksplisit.
- **REQ-NFR-006:** Seluruh transaksi keuangan dan mutasi barang harus mencatat waktu dan modul asal secara permanen untuk keperluan pelacakan audit.

### 10.3 Kemudahan Penggunaan dan Ergonomi (Usability)
- **REQ-NFR-007:** Aplikasi harus menggunakan palet warna terang (*Strict Light Mode*) dengan latar belakang `#F8FAF8` dan kartu putih murni `#FFFFFF`.
- **REQ-NFR-008:** Ukuran font teks konten utama minimal adalah 16 piksel agar nyaman dibaca di lingkungan luar ruangan (*outdoor*).
- **REQ-NFR-009:** Seluruh tombol aksi utama harus memiliki ukuran sentuh yang lega (tinggi tombol minimal 44 piksel).
- **REQ-NFR-010:** Seluruh nominal angka moneter, berat timbangan, dan luas lahan wajib menggunakan tata letak angka tabular (*tabular-nums*).

### 10.4 Lokalisasi Bahasa Indonesia (Localization)
- **REQ-NFR-011:** Seluruh teks antarmuka, pesan kesalahan, dialog konfirmasi, dan label tombol wajib menggunakan Bahasa Indonesia yang baku dan lugas.
- **REQ-NFR-012:** Format penulisan tanggal wajib menggunakan standar Indonesia (contoh: 16 Nov 2026 atau 16/11/2026).
- **REQ-NFR-013:** Format penulisan mata uang wajib menggunakan simbol `Rp` dengan pemisah ribuan titik (contoh: `Rp 24.500.000`).
- **REQ-NFR-014:** Format desimal untuk berat dan luas wajib menggunakan tanda koma (contoh: `4,5 Ha`, `28,4 Ton`).

---

## 11. Kriteria Penerimaan Global (Global Acceptance Criteria)

Sistem suite AgriStation dinyatakan lulus uji dan siap dirilis jika memenuhi seluruh kriteria berikut:

- **REQ-GAC-001:** Ke-10 aplikasi mandiri berhasil dibangun dan masing-masing dapat dijalankan secara independen melalui berkas eksekusi biner atau paket `.deb`.
- **REQ-GAC-002:** Folder `Icon/` berisi 10 berkas SVG valid yang dapat dibuka dan ditampilkan dengan sempurna oleh sistem desktop Linux.
- **REQ-GAC-003:** Basis data SQLite tunggal mampu melayani pembacaan dan penulisan dari kesepuluh aplikasi secara bersamaan tanpa menimbulkan insiden penguncian (*database locked error*).
- **REQ-GAC-004:** Mekanisme pembuatan cadangan data otomatis dan mandiri berjalan sukses dan menghasilkan berkas arsip `.tar.gz` yang terverifikasi nilai *hash* SHA-256 miliknya.
- **REQ-GAC-005:** Mekanisme pemulihan data (*restore*) berhasil mengembalikan seluruh data saat dilakukan simulasi kehilangan berkas basis data.
- **REQ-GAC-006:** Seluruh antarmuka aplikasi terbukti mematuhi pedoman visual `UI/00_master_design_system.md` tanpa penyimpangan skema warna gelap.
- **REQ-GAC-007:** Paket perangkat lunak berformat `.deb` berhasil dipasang (*install*), diuji coba, dan dicopot (*uninstall*) pada sistem operasi Debian/Ubuntu tanpa merusak dependensi sistem operasi.

---

## 12. Risiko dan Asumsi Proyek

### 12.1 Analisis Risiko dan Mitigasi
- **Risiko 1: Perebutan Akses Basis Data Bersama (*Concurrency Locking*)**
  - *Deskripsi:* Beberapa aplikasi melakukan operasi penulisan pada basis data SQLite di saat yang bersamaan.
  - *Mitigasi:* Sistem wajib menggunakan mode SQLite WAL (`journal_mode=WAL`), mengatur batas waktu tunggu sibuk (`busy_timeout = 5000` milidetik), dan menutup koneksi segera setelah transaksi selesai.
- **Risiko 2: Kerusakan Berkas Basis Data Akibat Pemadaman Listrik Mendadak**
  - *Deskripsi:* Komputer mati mendadak saat proses penulisan data berlangsung di lapangan.
  - *Mitigasi:* Sistem menggunakan transaksi atomik penuh dan mencadangkan data harian secara berkala.
- **Risiko 3: Penurunan Keterbacaan Layar di Bawah Sinar Matahari Lapangan**
  - *Deskripsi:* Petani kesulitan membaca layar komputer jinjing di area persawahan terbuka.
  - *Mitigasi:* Sistem menegakkan antarmuka kontras tinggi dengan warna latar cerah, font berukuran minimal 16px, dan larangan penggunaan tema gelap.

### 12.2 Asumsi Proyek
- **Asumsi 1:** Komputer target menggunakan sistem operasi Linux turunan Debian (Debian, Ubuntu, Linux Mint) dengan arsitektur x86_64 atau aarch64.
- **Asumsi 2:** Direktori beranda pengguna (`~`) memiliki ruang penyimpanan kosong minimal 500 MB untuk basis data dan cadangan berkas.
- **Asumsi 3:** Pengguna memiliki hak akses dasar untuk menjalankan berkas eksekusi aplikasi lokal.
