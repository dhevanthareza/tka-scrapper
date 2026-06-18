import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "progress.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sekolah_input (
            npsn TEXT PRIMARY KEY,
            sd TEXT,
            alamat TEXT,
            kecamatan TEXT,
            kelurahan TEXT,
            jml INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS siswa (
            nisn TEXT PRIMARY KEY,
            nama TEXT,
            npsn TEXT,
            tanggal_lahir TEXT,
            nik TEXT,
            no_kk TEXT,
            fetched_tka INTEGER DEFAULT 0,
            tka_data TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS error_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step TEXT,
            identifier TEXT,
            page INTEGER,
            error TEXT,
            ts INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_error(step, identifier, page, error):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO error_log (step, identifier, page, error, ts) VALUES (?, ?, ?, ?, ?)",
              (step, identifier, page, str(error), int(time.time())))
    conn.commit()
    conn.close()

def get_errors():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT step, identifier, page, error, ts FROM error_log ORDER BY ts DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def load_input_csv(csv_path):
    import csv
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            c.execute("""
                INSERT OR IGNORE INTO sekolah_input (npsn, sd, alamat, kecamatan, kelurahan, jml)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (row["npsn"], row.get("sd",""), row.get("alamat",""), row.get("kecamatan",""), row.get("kelurahan",""), int(row.get("jml",0) or 0)))
    conn.commit()
    conn.close()

def get_npsn_list():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT npsn, sd, alamat, kecamatan, kelurahan, jml FROM sekolah_input")
    rows = c.fetchall()
    conn.close()
    return rows

def save_siswa(rows):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executemany("INSERT OR IGNORE INTO siswa (nisn, nama, npsn, tanggal_lahir, nik, no_kk) VALUES (?, ?, ?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()

def get_unfetched_tka(batch=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nisn, tanggal_lahir FROM siswa WHERE fetched_tka = 0 LIMIT ?", (batch,))
    rows = c.fetchall()
    conn.close()
    return rows

def save_tka(nisn, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE siswa SET fetched_tka = 1, tka_data = ? WHERE nisn = ?", (json.dumps(data, ensure_ascii=False), nisn))
    conn.commit()
    conn.close()

def _flatten_tka(tka_json):
    import json
    if not tka_json:
        return {}
    try:
        data = json.loads(tka_json)
        items = data.get("data", [])
        if not items:
            return {}
        t = items[0]
        return {
            "tka_ikut_tka": t.get("ikut_tka"),
            "tka_jenjang": t.get("jenjang"),
            "tka_kategori_1": t.get("kategori_1"),
            "tka_kategori_2": t.get("kategori_2"),
            "tka_kategori_3": t.get("kategori_3"),
            "tka_kategori_4": t.get("kategori_4"),
            "tka_kategori_5": t.get("kategori_5"),
            "tka_nilai_1": t.get("nilai_1"),
            "tka_nilai_2": t.get("nilai_2"),
            "tka_nilai_3": t.get("nilai_3"),
            "tka_nilai_4": t.get("nilai_4"),
            "tka_nilai_5": t.get("nilai_5"),
            "tka_nm_mapel_1": t.get("nm_mapel_1"),
            "tka_nm_mapel_2": t.get("nm_mapel_2"),
            "tka_nm_mapel_3": t.get("nm_mapel_3"),
            "tka_nm_mapel_4": t.get("nm_mapel_4"),
            "tka_nm_mapel_5": t.get("nm_mapel_5"),
            "tka_nopes": t.get("nopes"),
            "tka_nm_pes": t.get("nm_pes"),
            "tka_npsn_asal": t.get("npsn_asal"),
            "tka_sek_asal": t.get("sek_asal"),
            "tka_tahun_ajar": t.get("tahun_ajar"),
            "tka_tgl_terbit": t.get("tgl_terbit"),
            "tka_tgl_tes": t.get("tgl_tes"),
            "tka_last_update": t.get("last_update"),
        }
    except Exception:
        return {}

def export_csv(path):
    import csv
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT s.nisn, s.nama, s.npsn, s.nik, s.no_kk, si.sd, si.alamat, si.kecamatan, si.kelurahan, si.jml, s.tanggal_lahir, s.tka_data
        FROM siswa s
        JOIN sekolah_input si ON s.npsn = si.npsn
        WHERE s.fetched_tka = 1
    """)
    rows = c.fetchall()
    conn.close()

    headers = ["nisn","nama_siswa","npsn","nik","no_kk","sd","alamat","kecamatan","kelurahan","jml","tanggal_lahir","SUMBER_NAMA",
               "tka_ikut_tka","tka_jenjang","tka_kategori_1","tka_kategori_2","tka_kategori_3",
               "tka_kategori_4","tka_kategori_5","tka_nilai_1","tka_nilai_2","tka_nilai_3",
               "tka_nilai_4","tka_nilai_5","tka_nm_mapel_1","tka_nm_mapel_2","tka_nm_mapel_3",
               "tka_nm_mapel_4","tka_nm_mapel_5","tka_nopes","tka_nm_pes","tka_npsn_asal",
               "tka_sek_asal","tka_tahun_ajar","tka_tgl_terbit","tka_tgl_tes","tka_last_update"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for nisn, nama, npsn, nik, no_kk, sd, alamat, kecamatan, kelurahan, jml, tgl_lahir, tka_data in rows:
            flattened = _flatten_tka(tka_data)
            base = {
                "nisn": nisn, "nama_siswa": nama, "npsn": npsn,
                "nik": nik, "no_kk": no_kk,
                "sd": sd, "alamat": alamat, "kecamatan": kecamatan,
                "kelurahan": kelurahan, "jml": jml, "tanggal_lahir": tgl_lahir,
                "SUMBER_NAMA": "api"
            }
            base.update(flattened)
            writer.writerow(base)
