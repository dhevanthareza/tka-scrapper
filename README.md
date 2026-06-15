# TKA Nominasi Scraper

Scraper untuk mengambil data TKA (Tes Kompetensi Awal) dari API SPL Kemendikdasmen berdasarkan daftar NPSN sekolah.

## Prerequisites

- Python 3.11+
- pip
- API credentials dari SPL Kemendikdasmen (Client ID, Client Secret, API Key)

## Setup

### 1. Clone Repository

```bash
git clone git@github.com:dhevanthareza/tka-scrapper.git
cd tka-scrapper
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau: venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Credentials

Create `config.yaml` in the project root:

```yaml
client_id: "your-client-id"
client_secret: "your-client-secret"
api_key: "your-api-key"
base_url: "https://api.spl.kemendikdasmen.go.id"
```

**Note:** Never commit `config.yaml` to git. It's already in `.gitignore`.

### 5. Prepare Input Data

Place your CSV file in `input/` folder:

```bash
cp your_npsn_list.csv input/ms_sekolah_nominasi_updated.csv
```

**Required CSV columns:**
- `npsn` — Nomor Pokok Sekolah Nasional
- `sd` — Nama sekolah
- `alamat` — Alamat sekolah
- `kecamatan` — Kecamatan
- `kelurahan` — Kelurahan
- `jml` — Jumlah (optional)

## Run

### Start Scraping

```bash
python main.py
```

### What Happens

1. **Load Input** — Read CSV and save to SQLite
2. **Fetch Students** — For each NPSN, fetch all students from API
3. **Fetch TKA** — For each student, fetch TKA data
4. **Export CSV** — Results saved to `output/tka_nominasi.csv`

### Resume Capability

If the scraper crashes, simply run again:

```bash
python main.py
```

It will automatically resume from where it left off.

## Output

**File:** `output/tka_nominasi.csv`

**Columns:**
- From input: `nisn`, `nama_siswa`, `npsn`, `sd`, `alamat`, `kecamatan`, `kelurahan`, `jml`
- From TKA API: `tanggal_lahir`, `tka_ikut_tka`, `tka_jenjang`, `tka_kategori_1-5`, `tka_nilai_1-5`, `tka_nm_mapel_1-5`, `tka_nopes`, `tka_nm_pes`, `tka_npsn_asal`, `tka_sek_asal`, `tka_tahun_ajar`, `tka_tgl_terbit`, `tka_tgl_tes`, `tka_last_update`

## Project Structure

```
tka-scrapper/
├── api_client.py          # SPL API wrapper (auth + endpoints)
├── fetcher.py             # Scrape orchestrator
├── main.py                # Entry point
├── storage.py             # SQLite + CSV export
├── requirements.txt       # Python dependencies
├── config.yaml            # API credentials (not in git)
├── input/
│   └── ms_sekolah_nominasi_updated.csv  # Input data
├── output/
│   └── tka_nominasi.csv   # Output result
└── progress.db            # SQLite database (not in git)
```

## Troubleshooting

### Token Expired

Delete token cache and re-run:

```bash
rm token_cache.json
python main.py
```

### Rate Limit

The scraper already includes:
- 0.5s delay between requests
- 3 retries with exponential backoff
- Auto-refresh token on 401

### Database Locked

Kill any running Python processes and restart:

```bash
pkill -f "python main.py"
python main.py
```

## License

Private — For SPMB Kota Semarang 2026 use only.
