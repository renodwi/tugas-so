"""
Database module for AgriStation Suite.
Manages centralized SQLite database at ~/.local/share/agristation/agristation.db
Enforces WAL mode, foreign keys, UTF-8, atomic transactions, triggers, and permissions.
"""

import os
import sqlite3
import datetime
from pathlib import Path

DB_DIR = Path.home() / ".local" / "share" / "agristation"
DB_PATH = DB_DIR / "agristation.db"
BACKUP_DIR = DB_DIR / "backups"
CONFIG_DIR = Path.home() / ".config" / "agristation"

SCHEMA_SQL = """
-- 1. plots (Daftar Lahan / Blok Sawah)
CREATE TABLE IF NOT EXISTS plots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plot_code TEXT UNIQUE NOT NULL,
    plot_name TEXT NOT NULL,
    area_ha REAL NOT NULL CHECK(area_ha > 0),
    location_desc TEXT NULL,
    soil_type TEXT NULL,
    status TEXT NOT NULL DEFAULT 'Aktif',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. crops (Tanaman dan Jadwal Budidaya)
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plot_id INTEGER NOT NULL REFERENCES plots(id) ON DELETE RESTRICT,
    crop_type TEXT NOT NULL,
    variety TEXT NOT NULL,
    planting_date TEXT NOT NULL,
    est_harvest_date TEXT NOT NULL,
    current_stage TEXT NOT NULL DEFAULT 'Tanam',
    target_yield_ton REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'Sedang Tumbuh',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. fertilizer_logs (Catatan Pemupukan)
CREATE TABLE IF NOT EXISTS fertilizer_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plot_id INTEGER NOT NULL REFERENCES plots(id),
    crop_id INTEGER NOT NULL REFERENCES crops(id),
    application_date TEXT NOT NULL,
    fertilizer_name TEXT NOT NULL,
    quantity_kg REAL NOT NULL CHECK(quantity_kg > 0),
    method TEXT NOT NULL,
    cost_idr REAL NOT NULL CHECK(cost_idr >= 0),
    status TEXT NOT NULL DEFAULT 'Terjadwal',
    notes TEXT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. irrigation_logs (Catatan Pengairan)
CREATE TABLE IF NOT EXISTS irrigation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plot_id INTEGER NOT NULL REFERENCES plots(id),
    equipment_id INTEGER NULL REFERENCES equipment(id),
    irrigation_date TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK(duration_minutes > 0),
    water_source TEXT NOT NULL,
    pump_type TEXT NOT NULL,
    fuel_liters REAL NOT NULL DEFAULT 0.0 CHECK(fuel_liters >= 0),
    notes TEXT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. pest_control_logs (Catatan Pengendalian Hama & PHI)
CREATE TABLE IF NOT EXISTS pest_control_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plot_id INTEGER NOT NULL REFERENCES plots(id),
    crop_id INTEGER NOT NULL REFERENCES crops(id),
    spray_date TEXT NOT NULL,
    target_pest TEXT NOT NULL,
    pesticide_name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    phi_days INTEGER NOT NULL CHECK(phi_days >= 0),
    safe_harvest_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Masa Tunggu',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. equipment (Katalog Alat dan Mesin Pertanian)
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Siap Pakai',
    total_hours REAL NOT NULL DEFAULT 0.0,
    next_service_hours REAL NOT NULL DEFAULT 50.0,
    last_used_date TEXT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. equipment_usage_logs (Riwayat Pemakaian Alsintan)
CREATE TABLE IF NOT EXISTS equipment_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    plot_id INTEGER NOT NULL REFERENCES plots(id),
    usage_date TEXT NOT NULL,
    hours_used REAL NOT NULL CHECK(hours_used > 0),
    operator_name TEXT NOT NULL,
    activity_desc TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. equipment_maintenance_logs (Riwayat Servis Alsintan)
CREATE TABLE IF NOT EXISTS equipment_maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    service_date TEXT NOT NULL,
    service_type TEXT NOT NULL,
    cost_idr REAL NOT NULL CHECK(cost_idr >= 0),
    workshop_technician TEXT NOT NULL,
    notes TEXT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9. harvest_yields (Catatan Panen dan Kualitas Mutu)
CREATE TABLE IF NOT EXISTS harvest_yields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_id INTEGER NOT NULL REFERENCES crops(id),
    plot_id INTEGER NOT NULL REFERENCES plots(id),
    harvest_date TEXT NOT NULL,
    total_yield_ton REAL NOT NULL CHECK(total_yield_ton >= 0),
    productivity_ton_ha REAL NOT NULL CHECK(productivity_ton_ha >= 0),
    grade_a_ton REAL NOT NULL DEFAULT 0.0,
    grade_b_ton REAL NOT NULL DEFAULT 0.0,
    grade_c_ton REAL NOT NULL DEFAULT 0.0,
    target_ton REAL NOT NULL DEFAULT 0.0,
    achievement_pct REAL NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 10. storage_locations (Master Fasilitas Gudang dan Silo)
CREATE TABLE IF NOT EXISTS storage_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    facility_type TEXT NOT NULL,
    capacity_ton REAL NOT NULL CHECK(capacity_ton > 0),
    used_ton REAL NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 11. storage_inventory (Rincian Stok Barang dan Komoditas)
CREATE TABLE IF NOT EXISTS storage_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_location_id INTEGER NOT NULL REFERENCES storage_locations(id),
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity_kg REAL NOT NULL CHECK(quantity_kg >= 0),
    package_count INTEGER NOT NULL DEFAULT 0,
    moisture_pct REAL NULL,
    condition_status TEXT NOT NULL DEFAULT 'Baik',
    last_in_date TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 12. storage_movements (Mutasi Keluar-Masuk Stok)
CREATE TABLE IF NOT EXISTS storage_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_inventory_id INTEGER NOT NULL REFERENCES storage_inventory(id),
    movement_type TEXT NOT NULL,
    quantity_kg REAL NOT NULL CHECK(quantity_kg > 0),
    movement_date TEXT NOT NULL,
    destination_or_source TEXT NOT NULL,
    notes TEXT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 13. finance_transactions (Buku Kas Keuangan)
CREATE TABLE IF NOT EXISTS finance_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT NOT NULL,
    category TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    description TEXT NOT NULL,
    amount_idr REAL NOT NULL CHECK(amount_idr > 0),
    source_module TEXT NOT NULL,
    ref_id INTEGER NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 14. daily_tasks (Daftar Tugas Mandor Harian)
CREATE TABLE IF NOT EXISTS daily_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_date TEXT NOT NULL,
    task_title TEXT NOT NULL,
    category TEXT NOT NULL,
    plot_id INTEGER NOT NULL REFERENCES plots(id),
    is_completed INTEGER NOT NULL DEFAULT 0 CHECK(is_completed IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- TRIGGERS FOR BUSINESS RULES

-- Trigger: When fertilizer completed with cost > 0, auto record to finance_transactions (REQ-APP04-001 & REQ-DB-007)
CREATE TRIGGER IF NOT EXISTS trg_fertilizer_completed_insert
AFTER INSERT ON fertilizer_logs
WHEN NEW.status = 'Selesai' AND NEW.cost_idr > 0
BEGIN
    INSERT INTO finance_transactions (transaction_date, category, transaction_type, description, amount_idr, source_module, ref_id)
    VALUES (NEW.application_date, 'Pupuk & Obat', 'Pengeluaran', 'Biaya Aplikasi Pupuk ' || NEW.fertilizer_name, NEW.cost_idr, 'Agri-Fertilizer Planner', NEW.id);
END;

CREATE TRIGGER IF NOT EXISTS trg_fertilizer_completed_update
AFTER UPDATE OF status ON fertilizer_logs
WHEN OLD.status != 'Selesai' AND NEW.status = 'Selesai' AND NEW.cost_idr > 0
BEGIN
    INSERT INTO finance_transactions (transaction_date, category, transaction_type, description, amount_idr, source_module, ref_id)
    VALUES (NEW.application_date, 'Pupuk & Obat', 'Pengeluaran', 'Biaya Aplikasi Pupuk ' || NEW.fertilizer_name, NEW.cost_idr, 'Agri-Fertilizer Planner', NEW.id);
END;

-- Trigger: When equipment maintenance logged with cost > 0, auto record to finance_transactions & update equipment (REQ-APP08-002, REQ-APP08-003 & REQ-DB-008)
CREATE TRIGGER IF NOT EXISTS trg_equipment_maintenance_insert
AFTER INSERT ON equipment_maintenance_logs
BEGIN
    INSERT INTO finance_transactions (transaction_date, category, transaction_type, description, amount_idr, source_module, ref_id)
    SELECT NEW.service_date, 'BBM & Perawatan', 'Pengeluaran', 'Servis ' || e.name || ' (' || NEW.service_type || ')', NEW.cost_idr, 'Agri-Equipment Log', NEW.id
    FROM equipment e WHERE e.id = NEW.equipment_id AND NEW.cost_idr > 0;
    
    UPDATE equipment
    SET next_service_hours = total_hours + 50.0,
        status = 'Siap Pakai',
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.equipment_id;
END;

-- Trigger: When equipment usage logged, add hours to equipment total_hours & check service threshold (REQ-APP08-001)
CREATE TRIGGER IF NOT EXISTS trg_equipment_usage_insert
AFTER INSERT ON equipment_usage_logs
BEGIN
    UPDATE equipment
    SET total_hours = total_hours + NEW.hours_used,
        last_used_date = NEW.usage_date,
        status = CASE 
            WHEN (total_hours + NEW.hours_used) >= next_service_hours THEN 'Perlu Servis'
            ELSE status
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.equipment_id;
END;

-- Trigger: When irrigation uses equipment, record last_used_date
CREATE TRIGGER IF NOT EXISTS trg_irrigation_equipment_update
AFTER INSERT ON irrigation_logs
WHEN NEW.equipment_id IS NOT NULL
BEGIN
    UPDATE equipment
    SET total_hours = total_hours + (NEW.duration_minutes / 60.0),
        last_used_date = substr(NEW.irrigation_date, 1, 10),
        status = CASE 
            WHEN (total_hours + (NEW.duration_minutes / 60.0)) >= next_service_hours THEN 'Perlu Servis'
            ELSE status
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.equipment_id;
END;

-- Trigger: When storage movement logged, update storage_inventory and storage_locations used_ton (REQ-DB-009)
CREATE TRIGGER IF NOT EXISTS trg_storage_movement_insert
AFTER INSERT ON storage_movements
BEGIN
    -- Update item quantity
    UPDATE storage_inventory
    SET quantity_kg = CASE 
            WHEN NEW.movement_type = 'Masuk' THEN quantity_kg + NEW.quantity_kg
            WHEN NEW.movement_type = 'Keluar' THEN MAX(0, quantity_kg - NEW.quantity_kg)
            ELSE quantity_kg
        END,
        package_count = CASE
            WHEN NEW.movement_type = 'Masuk' THEN package_count + CAST(ROUND(NEW.quantity_kg / 50.0) AS INT)
            WHEN NEW.movement_type = 'Keluar' THEN MAX(0, package_count - CAST(ROUND(NEW.quantity_kg / 50.0) AS INT))
            ELSE package_count
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.storage_inventory_id;

    -- Update location used_ton
    UPDATE storage_locations
    SET used_ton = (
        SELECT ROUND(COALESCE(SUM(quantity_kg), 0) / 1000.0, 2)
        FROM storage_inventory
        WHERE storage_location_id = storage_locations.id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = (SELECT storage_location_id FROM storage_inventory WHERE id = NEW.storage_inventory_id);
END;
"""

def ensure_directories():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(DB_DIR, 0o700)
        os.chmod(BACKUP_DIR, 0o700)
    except Exception:
        pass

def get_connection():
    ensure_directories()
    conn = sqlite3.connect(str(DB_PATH), timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.row_factory = sqlite3.Row
    
    # Enforce file permission 0600 (REQ-NFR-004)
    if DB_PATH.exists():
        try:
            os.chmod(DB_PATH, 0o600)
        except Exception:
            pass
            
    return conn

def init_db(force_seed=False):
    ensure_directories()
    is_new = not DB_PATH.exists() or DB_PATH.stat().st_size == 0
    conn = get_connection()
    with conn:
        conn.executescript(SCHEMA_SQL)
    
    # Check if database has plots; if not, populate seed data
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM plots")
    count = cursor.fetchone()[0]
    if count == 0 or force_seed:
        seed_data(conn)
    conn.close()

def seed_data(conn):
    """Seed realistic Indonesian agricultural data."""
    with conn:
        # Temporarily disable foreign keys to cleanly reset tables if re-seeding
        conn.execute("PRAGMA foreign_keys=OFF;")
        for tbl in [
            "daily_tasks", "finance_transactions", "storage_movements",
            "storage_inventory", "storage_locations", "harvest_yields",
            "equipment_maintenance_logs", "equipment_usage_logs",
            "equipment", "pest_control_logs", "irrigation_logs",
            "fertilizer_logs", "crops", "plots"
        ]:
            try:
                conn.execute(f"DELETE FROM {tbl};")
                conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{tbl}';")
            except Exception:
                pass
        conn.execute("PRAGMA foreign_keys=ON;")

        # 1. Plots
        plots_data = [
            ("BLK-A1", "Blok A1 - Sawah Utara", 1.2, "Kec. Sukamaju, Sisi Irigasi Primer", "Lempung Berliat", "Aktif"),
            ("BLK-A2", "Blok A2 - Sawah Selatan", 0.8, "Kec. Sukamaju, Dekat Embung Desa", "Aluvial", "Aktif"),
            ("BLK-B1", "Blok B1 - Kebun Jagung Barat", 1.5, "Desa Mekarsari, Dataran Kering", "Regosol Pasiran", "Aktif"),
            ("BLK-B2", "Blok B2 - Sawah Timur", 1.0, "Desa Mekarsari, Daerah Bendung Baru", "Lempung Aluvial", "Aktif"),
            ("BLK-C1", "Blok C1 - Lahan Horti Lereng", 0.6, "Perbukitan Hijau, Dekat Sumur Bor", "Andosol", "Persiapan"),
            ("BLK-C2", "Blok C2 - Petak Kedelai", 0.9, "Desa Mekarsari, Blok Timur", "Lempung", "Istirahat")
        ]
        conn.executemany("""
            INSERT INTO plots (plot_code, plot_name, area_ha, location_desc, soil_type, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, plots_data)

        # 2. Crops
        # Today reference: 2026-11-16
        crops_data = [
            (1, "Padi", "Ciherang", "2026-08-15", "2026-11-21", "Siap Panen", 7.8, "Sedang Tumbuh"),
            (2, "Padi", "Inpari 32", "2026-09-01", "2026-12-10", "Bunga", 5.2, "Sedang Tumbuh"),
            (3, "Jagung", "Bisi 18", "2026-09-10", "2026-12-25", "Vegetatif", 9.5, "Sedang Tumbuh"),
            (4, "Padi", "Ciherang", "2026-08-20", "2026-11-28", "Siap Panen", 6.5, "Sedang Tumbuh")
        ]
        conn.executemany("""
            INSERT INTO crops (plot_id, crop_type, variety, planting_date, est_harvest_date, current_stage, target_yield_ton, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, crops_data)

        # 3. Equipment
        eq_data = [
            ("TRK-01", "Traktor Roda 2 Quick G1000", "Traktor", "Siap Pakai", 142.0, 150.0, "2026-11-14"),
            ("TRK-02", "Traktor Roda 4 Yanmar EF393T", "Traktor", "Siap Pakai", 310.5, 350.0, "2026-11-10"),
            ("PMP-01", "Pompa Air Diesel 3 Inch Kubota", "Pompa Air", "Siap Pakai", 88.0, 100.0, "2026-11-15"),
            ("PMP-02", "Pompa Celup Listrik 2 HP", "Pompa Air", "Siap Pakai", 45.0, 100.0, "2026-11-12"),
            ("SPR-01", "Sprayer Elektrik CBA 16L", "Sprayer", "Siap Pakai", 35.0, 50.0, "2026-11-11"),
            ("SPR-02", "Sprayer Mesin Tasco TF-820", "Sprayer", "Perlu Servis", 98.0, 95.0, "2026-11-08")
        ]
        conn.executemany("""
            INSERT INTO equipment (equipment_code, name, category, status, total_hours, next_service_hours, last_used_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, eq_data)

        # 4. Storage Locations
        loc_data = [
            ("GD-01", "Gudang Komoditas Utama", "Gudang Komoditas", 20.0, 14.5),
            ("GD-02", "Gudang Benih & Saprotan", "Gudang Benih", 5.0, 1.8),
            ("SL-01", "Silo Pengering Gabah", "Silo", 10.0, 8.8)
        ]
        conn.executemany("""
            INSERT INTO storage_locations (code, name, facility_type, capacity_ton, used_ton)
            VALUES (?, ?, ?, ?, ?)
        """, loc_data)

        # 5. Storage Inventory
        inv_data = [
            (1, "Gabah Kering Panen (GKP) - Ciherang", "Hasil Panen", 8500.0, 170, 13.2, "Baik", "2026-11-05"),
            (1, "Jagung Pipil Kering - Bisi 18", "Hasil Panen", 6000.0, 120, 12.8, "Baik", "2026-10-28"),
            (2, "Benih Padi Inpari 32 (Sertifikat)", "Benih", 800.0, 160, 11.5, "Baik", "2026-11-02"),
            (2, "Pupuk NPK Phonska 15-15-15", "Pupuk", 1000.0, 20, 0.0, "Baik", "2026-11-10"),
            (3, "Gabah Basah Masuk Dryer", "Hasil Panen", 8800.0, 176, 17.5, "Lembab", "2026-11-14")
        ]
        conn.executemany("""
            INSERT INTO storage_inventory (storage_location_id, item_name, category, quantity_kg, package_count, moisture_pct, condition_status, last_in_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, inv_data)

        # 6. Daily Tasks
        tasks_data = [
            ("2026-11-16", "Pengecekan saluran pembuangan air menjelang panen", "Pengairan", 1, 0),
            ("2026-11-16", "Pemupukan susulan kedua NPK Phonska", "Pemupukan", 3, 1),
            ("2026-11-16", "Inspeksi hama wereng batang coklat di pematang", "Semprot", 2, 0),
            ("2026-11-16", "Pembersihan saringan hisap pompa diesel", "Pengairan", 1, 1),
            ("2026-11-17", "Persiapan terpal jemur & karung gabah", "Panen", 1, 0)
        ]
        conn.executemany("""
            INSERT INTO daily_tasks (task_date, task_title, category, plot_id, is_completed)
            VALUES (?, ?, ?, ?, ?)
        """, tasks_data)

        # 7. Fertilizer Logs
        fert_data = [
            (1, 1, "2026-08-25", "Urea Pusri", 100.0, "Tabur", 650000.0, "Selesai", "Aplikasi dasar umur 10 HST"),
            (1, 1, "2026-09-15", "NPK Phonska", 150.0, "Tabur", 975000.0, "Selesai", "Pemupukan kedua umur 30 HST"),
            (3, 3, "2026-10-05", "Urea Pusri", 200.0, "Tabur", 1300000.0, "Selesai", "Fase vegetatif jagung"),
            (2, 2, "2026-11-19", "Pupuk Daun Gandasil B", 15.0, "Semprot Daun", 350000.0, "Terjadwal", "Pengisian bulir padi"),
            (3, 3, "2026-11-25", "NPK Mutiara", 100.0, "Kocor", 1100000.0, "Terjadwal", "Pemupukan fase generatif")
        ]
        conn.executemany("""
            INSERT INTO fertilizer_logs (plot_id, crop_id, application_date, fertilizer_name, quantity_kg, method, cost_idr, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, fert_data)

        # 8. Irrigation Logs
        irr_data = [
            (1, 3, "2026-11-15 06:30", 195, "Sumur Bor", "Diesel 3 Inch", 4.0, "Pengisian air jelang panen"),
            (2, 4, "2026-11-14 07:00", 120, "Irigasi Teknis", "Pompa Listrik", 0.0, "Debit air saluran sekunder stabil"),
            (3, 3, "2026-11-12 14:00", 240, "Sungai", "Diesel 3 Inch", 5.5, "Penyiraman kebun jagung sore"),
            (4, 3, "2026-11-10 08:00", 180, "Embung", "Diesel 3 Inch", 3.8, "Penggenangan sawah timur"),
            (1, None, "2026-11-05 06:00", 150, "Irigasi Teknis", "Gravitasi", 0.0, "Aliran pintu air utama")
        ]
        conn.executemany("""
            INSERT INTO irrigation_logs (plot_id, equipment_id, irrigation_date, duration_minutes, water_source, pump_type, fuel_liters, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, irr_data)

        # 9. Pest Control Logs (with PHI)
        # safe_harvest_date = spray_date + phi_days
        pest_data = [
            (1, 1, "2026-10-25", "Wereng Batang Coklat", "Insektisida Virtako 300SC", "1.5 ml/Liter", 14, "2026-11-08", "Aman Dipanen"),
            (2, 2, "2026-11-08", "Ulat Penggulung Daun", "Insektisida Prevathon 50SC", "2.0 ml/Liter", 14, "2026-11-22", "Masa Tunggu"),
            (3, 3, "2026-11-02", "Ulat Grayak (FAW)", "Insektisida Ampligo", "1.0 ml/Liter", 7, "2026-11-09", "Aman Dipanen"),
            (4, 4, "2026-11-11", "Jamur Blas Daun", "Fungisida Amistartop", "1.0 ml/Liter", 14, "2026-11-25", "Masa Tunggu")
        ]
        conn.executemany("""
            INSERT INTO pest_control_logs (plot_id, crop_id, spray_date, target_pest, pesticide_name, dosage, phi_days, safe_harvest_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pest_data)

        # 10. Equipment Usage & Maintenance
        usage_data = [
            (1, 1, "2026-11-14", 4.5, "Bpk. Slamet", "Pembajakan lahan rotasi"),
            (3, 1, "2026-11-15", 3.25, "Bpk. Warsito", "Pengairan blok sawah utara"),
            (2, 3, "2026-11-10", 6.0, "Bpk. Slamet", "Pengolahan bedengan jagung")
        ]
        conn.executemany("""
            INSERT INTO equipment_usage_logs (equipment_id, plot_id, usage_date, hours_used, operator_name, activity_desc)
            VALUES (?, ?, ?, ?, ?, ?)
        """, usage_data)

        maint_data = [
            (1, "2026-10-20", "Ganti Oli Mesin & Filter", 250000.0, "Bengkel Tani Jaya", "Oli Pertamina Meditran SX 5L"),
            (3, "2026-10-25", "Ganti Impeller & Sil Pompa", 380000.0, "Teknisi Mandiri Joko", "Penggantian sil mekanikal"),
            (6, "2026-11-08", "Ganti Karburator & Selang", 450000.0, "Bengkel Tani Jaya", "Penyumbatan endapan bensin")
        ]
        conn.executemany("""
            INSERT INTO equipment_maintenance_logs (equipment_id, service_date, service_type, cost_idr, workshop_technician, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, maint_data)

        # 11. Harvest Yields (Historical seasons)
        harvest_data = [
            (1, 1, "2026-04-20", 7.6, 6.33, 5.8, 1.4, 0.4, 7.2, 105.5),
            (2, 2, "2026-05-15", 5.4, 6.75, 4.2, 0.9, 0.3, 5.0, 108.0),
            (3, 3, "2026-06-10", 9.2, 6.13, 7.1, 1.6, 0.5, 9.0, 102.2),
            (4, 4, "2026-04-28", 6.2, 6.20, 4.8, 1.1, 0.3, 6.0, 103.3)
        ]
        conn.executemany("""
            INSERT INTO harvest_yields (crop_id, plot_id, harvest_date, total_yield_ton, productivity_ton_ha, grade_a_ton, grade_b_ton, grade_c_ton, target_ton, achievement_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, harvest_data)

        # 12. Storage Movements
        mov_data = [
            (1, "Masuk", 8500.0, "2026-11-05", "Panen Blok A1 Musim Lalu", "Gabah kering bersih"),
            (2, "Masuk", 6000.0, "2026-10-28", "Panen Blok B1", "Kadar air 12.8%"),
            (1, "Keluar", 2000.0, "2026-11-12", "Pabrik Beras Sari Rejeki", "Penjualan beras premium"),
            (4, "Keluar", 250.0, "2026-11-14", "Aplikasi Blok B1", "Pengambilan pupuk Phonska")
        ]
        conn.executemany("""
            INSERT INTO storage_movements (storage_inventory_id, movement_type, quantity_kg, movement_date, destination_or_source, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, mov_data)

        # 13. Finance Transactions
        fin_data = [
            ("2026-10-20", "BBM & Perawatan", "Pengeluaran", "Ganti Oli Traktor Quick G1000", 250000.0, "Agri-Equipment Log", 1),
            ("2026-10-25", "BBM & Perawatan", "Pengeluaran", "Servis Impeller Pompa Diesel", 380000.0, "Agri-Equipment Log", 2),
            ("2026-11-01", "Upah Tenaga", "Pengeluaran", "Upah Penyiangan & Matun Blok A1 (4 Orang)", 1200000.0, "Agri-Finance Ledger", None),
            ("2026-11-05", "Pupuk & Obat", "Pengeluaran", "Pembelian Pupuk Urea & NPK Phonska", 2925000.0, "Agri-Fertilizer Planner", 1),
            ("2026-11-10", "BBM & Perawatan", "Pengeluaran", "Pembelian Solar Industri 50 Liter", 680000.0, "Agri-Irrigation Tracker", None),
            ("2026-11-12", "Penjualan Panen", "Pemasukan", "Penjualan GKP 2.000 Kg ke Pabrik Sari Rejeki", 13600000.0, "Agri-Storage Manager", None),
            ("2026-11-14", "Penjualan Panen", "Pemasukan", "Penjualan Jagung Pipil 3.000 Kg ke Pengepul", 16500000.0, "Agri-Finance Ledger", None),
            ("2026-11-15", "Upah Tenaga", "Pengeluaran", "Upah Operator Traktor Olah Tanah", 600000.0, "Agri-Finance Ledger", None)
        ]
        conn.executemany("""
            INSERT INTO finance_transactions (transaction_date, category, transaction_type, description, amount_idr, source_module, ref_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, fin_data)

    print("Initial seed data inserted successfully.")
