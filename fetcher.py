import time
import sys
from api_client import SPLClient
from storage import save_siswa, get_unfetched_tka, save_tka, log_error, get_npsn_list

def fetch_all_siswa():
    client = SPLClient()
    token = client.get_token()
    npsn_list = get_npsn_list()
    total = len(npsn_list)
    print(f"Total NPSN dari input: {total}")
    
    for idx, (npsn, sd, alamat, kecamatan, kelurahan, jml) in enumerate(npsn_list, 1):
        print(f"[{idx}/{total}] Fetch siswa NPSN {npsn} ({sd})...")
        page = 1
        while True:
            try:
                data = client.get_siswa_by_npsn(npsn, page=page, per_page=150)
            except Exception as e:
                log_error("siswa", npsn, page, e)
                print(f"  ERROR fetch siswa NPSN {npsn} page {page}: {e}")
                break
            
            rows = []
            for item in data.get("data", []):
                nisn = item.get("nisn")
                if nisn is None or nisn == "":
                    print(f"  SKIP siswa tanpa NISN: {item.get('nama')}")
                    continue
                rows.append((
                    nisn,
                    item.get("nama"),
                    npsn,
                    item.get("tanggal_lahir"),
                    item.get("nik"),
                    item.get("no_kk")
                ))
            
            if rows:
                save_siswa(rows)
                print(f"  Saved {len(rows)} siswa")
            
            if len(data.get("data", [])) < 150:
                break
            page += 1
            time.sleep(0.1)
        
        time.sleep(0.1)
        print(f"  Done NPSN {npsn}")
    
    print("Done fetching all siswa.")

def fetch_all_tka():
    client = SPLClient()
    token = client.get_token()
    while True:
        batch = get_unfetched_tka(batch=100)
        if not batch:
            print("No more TKA to fetch.")
            break
        
        print(f"Fetching TKA for {len(batch)} siswa...")
        for nisn, tgl_lahir in batch:
            try:
                data = client.get_tka(nisn, tgl_lahir)
            except Exception as e:
                log_error("tka", nisn, 0, e)
                print(f"  ERROR TKA NISN {nisn}: {e}")
                continue
            
            save_tka(nisn, data)
            time.sleep(0.05)
        
        print(f"  Batch done. Continuing...")
    
    print("Done fetching all TKA.")

def run():
    print("=== TKA Nominasi Scraper ===")
    print("Step 1: Fetch siswa per NPSN...")
    fetch_all_siswa()
    print("\nStep 2: Fetch TKA per siswa...")
    fetch_all_tka()
    print("\nAll done!")
