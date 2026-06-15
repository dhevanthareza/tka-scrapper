import sys
from pathlib import Path
from storage import init_db, load_input_csv, export_csv
from fetcher import run

INPUT_CSV = Path(__file__).parent / "input" / "ms_sekolah_nominasi_updated.csv"
OUTPUT_CSV = Path(__file__).parent / "output" / "tka_nominasi.csv"

def main():
    print("Initializing database...")
    init_db()
    
    if not INPUT_CSV.exists():
        print(f"Input file not found: {INPUT_CSV}")
        sys.exit(1)
    
    print("Loading input CSV...")
    load_input_csv(INPUT_CSV)
    
    print("Starting scrape...")
    run()
    
    print("Exporting to CSV...")
    export_csv(OUTPUT_CSV)
    print(f"Output saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
