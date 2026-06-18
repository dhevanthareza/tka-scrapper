import csv
import json
import sys
import time
from pathlib import Path

from api_client import SPLClient

INPUT_CSV = Path(__file__).parent / "input" / "only_in_rapor.csv"
OUTPUT_CSV = Path(__file__).parent / "output" / "tka_by_nisn.csv"
ERROR_LOG = Path(__file__).parent / "output" / "error_nisn.csv"


def _flatten_tka(tka_data):
    if not tka_data:
        return {}
    items = tka_data.get("data", [])
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


def main():
    if not INPUT_CSV.exists():
        print(f"Input file not found: {INPUT_CSV}")
        sys.exit(1)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Read input
    rows = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    total = len(rows)
    print(f"Total siswa dari CSV: {total}")

    # Prepare output
    headers = [
        "nisn", "nama_siswa", "npsn", "sd", "alamat", "kecamatan", "kelurahan", "jml", "tanggal_lahir", "SUMBER_NAMA",
        "tka_ikut_tka", "tka_jenjang", "tka_kategori_1", "tka_kategori_2", "tka_kategori_3",
        "tka_kategori_4", "tka_kategori_5", "tka_nilai_1", "tka_nilai_2", "tka_nilai_3",
        "tka_nilai_4", "tka_nilai_5", "tka_nm_mapel_1", "tka_nm_mapel_2", "tka_nm_mapel_3",
        "tka_nm_mapel_4", "tka_nm_mapel_5", "tka_nopes", "tka_nm_pes", "tka_npsn_asal",
        "tka_sek_asal", "tka_tahun_ajar", "tka_tgl_terbit", "tka_tgl_tes", "tka_last_update"
    ]

    out_f = open(OUTPUT_CSV, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(out_f, fieldnames=headers)
    writer.writeheader()

    err_f = open(ERROR_LOG, "w", newline="", encoding="utf-8")
    err_writer = csv.DictWriter(err_f, fieldnames=["nisn", "nama", "dob", "error"])
    err_writer.writeheader()

    client = SPLClient()
    client.get_token()

    sukses = 0
    gagal = 0

    for idx, row in enumerate(rows, 1):
        nisn = row.get("NISN", "").strip()
        dob = row.get("DOB", "").strip()
        nama = row.get("NAMA", "").strip()

        print(f"[{idx}/{total}] NISN {nisn} ({nama})...", end=" ")

        try:
            data = client.get_tka(nisn, dob)
        except Exception as e:
            print(f"GAGAL: {e}")
            err_writer.writerow({"nisn": nisn, "nama": nama, "dob": dob, "error": str(e)})
            err_f.flush()
            gagal += 1
            continue

        flattened = _flatten_tka(data)
        api_nama = flattened.get("tka_nm_pes", "")
        if api_nama:
            nama_final = api_nama
            sumber = "api"
        else:
            nama_final = nama
            sumber = "input"

        base = {
            "nisn": nisn,
            "nama_siswa": nama_final,
            "npsn": row.get("NPSN", ""),
            "sd": row.get("SD", ""),
            "alamat": "",
            "kecamatan": row.get("KECAMATAN", ""),
            "kelurahan": "",
            "jml": "",
            "tanggal_lahir": dob,
            "SUMBER_NAMA": sumber,
        }
        base.update(flattened)
        writer.writerow(base)
        out_f.flush()

        sukses += 1
        print("OK")

        time.sleep(0.3)

    out_f.close()
    err_f.close()

    print(f"\n=== REPORT ===")
    print(f"Total   : {total}")
    print(f"Sukses  : {sukses}")
    print(f"Gagal   : {gagal}")
    print(f"Output  : {OUTPUT_CSV}")
    print(f"Error   : {ERROR_LOG}")


if __name__ == "__main__":
    main()
