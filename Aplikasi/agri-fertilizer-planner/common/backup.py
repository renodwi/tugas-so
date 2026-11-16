"""
Backup and Restore module for AgriStation Suite.
Follows PRD Section 6 specifications:
- Format: agristation_backup_YYYYMMDD_HHMMSS.tar.gz + .sha256
- PRAGMA integrity_check before backup and after restore extraction
- Pre-restore safety snapshot (agristation.db.pre-restore)
- 30-day retention rotation policy
"""

import os
import tarfile
import hashlib
import sqlite3
import datetime
import shutil
import tempfile
from pathlib import Path
from .db import DB_PATH, BACKUP_DIR, get_connection

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def check_db_integrity(db_file_path):
    """Run PRAGMA integrity_check; and verify result is 'ok'."""
    try:
        conn = sqlite3.connect(str(db_file_path), timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        row = cursor.fetchone()
        conn.close()
        if row and row[0].lower() == 'ok':
            return True, "ok"
        return False, str(row[0]) if row else "Unknown error"
    except Exception as e:
        return False, str(e)

def rotate_old_backups(days=30):
    """Remove backups older than 30 days kalender."""
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=days)
    if not BACKUP_DIR.exists():
        return
    for item in BACKUP_DIR.iterdir():
        if item.is_file() and (item.name.endswith(".tar.gz") or item.name.endswith(".sha256")):
            mtime = datetime.datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                try:
                    item.unlink()
                except Exception:
                    pass

def create_backup():
    """
    Creates an on-demand or scheduled backup.
    Returns (success: bool, message: str, archive_path: Path or None)
    """
    if not DB_PATH.exists():
        return False, "Berkas database tidak ditemukan.", None
    
    # Check integrity first (REQ-BKP-007, REQ-BKP-008)
    ok, err_msg = check_db_integrity(DB_PATH)
    if not ok:
        return False, f"Pemeriksaan integritas database gagal: {err_msg}", None
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"agristation_backup_{timestamp}.tar.gz"
    sha_name = f"agristation_backup_{timestamp}.sha256"
    
    archive_path = BACKUP_DIR / archive_name
    sha_path = BACKUP_DIR / sha_name
    
    # Safely dump/copy sqlite db using sqlite backup API or file copy with checkpoint
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_db = Path(tmpdir) / "agristation.db"
        # Use sqlite3 online backup to ensure clean snapshot even during active WAL
        src = sqlite3.connect(str(DB_PATH), timeout=5.0)
        dst = sqlite3.connect(str(tmp_db))
        src.backup(dst)
        dst.close()
        src.close()
        
        # Verify the backup copy
        ok, err_msg = check_db_integrity(tmp_db)
        if not ok:
            return False, f"Pemeriksaan integritas snapshot cadangan gagal: {err_msg}", None
            
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(tmp_db, arcname="agristation.db")
            
    # Calculate sha256
    sha256_hash = compute_sha256(archive_path)
    with open(sha_path, "w", encoding="utf-8") as f:
        f.write(f"{sha256_hash}  {archive_name}\n")
        
    # Rotate backups older than 30 days
    rotate_old_backups(30)
    
    return True, f"Cadangan berhasil dibuat: {archive_name}", archive_path

def restore_backup(archive_path):
    """
    Executes the 10-step restore flow specified in PRD Section 6.3.
    Returns (success: bool, message: str)
    """
    archive_path = Path(archive_path)
    if not archive_path.exists():
        return False, f"Berkas cadangan {archive_path.name} tidak ditemukan."
    
    # 1 & 2 & 3: Verify sha256
    sha_path = archive_path.with_suffix("").with_suffix(".sha256")
    if not sha_path.exists():
        # Try finding .sha256 with same base
        sha_path = Path(str(archive_path)[:-7] + ".sha256")
        
    if not sha_path.exists():
        return False, f"Berkas tanda tangan kontrol integritas (.sha256) tidak ditemukan."
        
    expected_hash = ""
    with open(sha_path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
        expected_hash = line.split()[0]
        
    actual_hash = compute_sha256(archive_path)
    if actual_hash.lower() != expected_hash.lower():
        return False, f"Verifikasi hash SHA-256 gagal! Berkas mungkin korup atau telah diubah."
        
    # 4 & 5: Create emergency backup of active db
    pre_restore_path = DB_PATH.with_name("agristation.db.pre-restore")
    if DB_PATH.exists():
        try:
            shutil.copy2(DB_PATH, pre_restore_path)
        except Exception as e:
            return False, f"Gagal membuat salinan darurat pre-restore: {e}"
            
    # 6: Extract db from archive to temporary location
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_extract_db = Path(tmpdir) / "agristation.db"
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extract("agristation.db", path=tmpdir)
        except Exception as e:
            if pre_restore_path.exists():
                shutil.copy2(pre_restore_path, DB_PATH)
            return False, f"Gagal mengekstrak berkas arsip: {e}"
            
        # 7: Verify SQLite integrity of extracted database
        ok, err_msg = check_db_integrity(tmp_extract_db)
        if not ok:
            # 9: Revert
            if pre_restore_path.exists():
                shutil.copy2(pre_restore_path, DB_PATH)
            return False, f"Integritas database hasil ekstraksi rusak: {err_msg}"
            
        # 8: Replace active db
        try:
            # Remove existing WAL and SHM if present
            wal = DB_PATH.with_name("agristation.db-wal")
            shm = DB_PATH.with_name("agristation.db-shm")
            if wal.exists():
                wal.unlink()
            if shm.exists():
                shm.unlink()
                
            shutil.copy2(tmp_extract_db, DB_PATH)
            os.chmod(DB_PATH, 0o600)
        except Exception as e:
            if pre_restore_path.exists():
                shutil.copy2(pre_restore_path, DB_PATH)
            return False, f"Gagal mengganti berkas database aktif: {e}"
            
    return True, f"Pemulihan data dari {archive_path.name} berhasil diselesaikan dengan aman."

def list_backups():
    """Return sorted list of existing backups with metadata."""
    if not BACKUP_DIR.exists():
        return []
    results = []
    for f in sorted(BACKUP_DIR.glob("agristation_backup_*.tar.gz"), reverse=True):
        sha = f.with_name(f.name[:-7] + ".sha256")
        has_sha = sha.exists()
        size_kb = round(f.stat().st_size / 1024, 1)
        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m/%Y %H:%M:%S")
        results.append({
            "path": str(f),
            "filename": f.name,
            "size_kb": size_kb,
            "mtime": mtime,
            "has_sha": has_sha
        })
    return results
