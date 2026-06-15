import requests
import yaml
import json
import time
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"
TOKEN_PATH = Path(__file__).parent / "token_cache.json"

def retry_request(fn, max_retries=3, delay=2):
    last_error = None
    for attempt in range(max_retries):
        try:
            return fn()
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < max_retries - 1:
                print(f"    Retry {attempt + 1}/{max_retries} after {delay}s... ({e})")
                time.sleep(delay)
                delay *= 2
            else:
                raise last_error

class SPLClient:
    def __init__(self):
        with open(CONFIG_PATH) as f:
            cfg = yaml.safe_load(f)
        self.client_id = cfg["client_id"]
        self.client_secret = cfg["client_secret"]
        self.api_key = cfg["api_key"]
        self.base_url = cfg["base_url"].rstrip("/")
        self._token = None
        self._load_token()

    def _load_token(self):
        if TOKEN_PATH.exists():
            data = json.loads(TOKEN_PATH.read_text())
            self._token = data.get("access_token")

    def _save_token(self, token):
        self._token = token
        TOKEN_PATH.write_text(json.dumps({"access_token": token, "ts": time.time()}))

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "X-Client-Id": self.client_id,
            "X-Client-Secret": self.client_secret,
        }

    def get_token(self):
        url = f"{self.base_url}/spl/service/token"
        payload = {"client_id": self.client_id, "client_secret": self.client_secret}
        r = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        r.raise_for_status()
        token = r.json()["data"]["access_token"]
        self._save_token(token)
        return token

    def _get(self, path, params=None):
        url = f"{self.base_url}{path}"
        p = params or {}
        p["api_key"] = self.api_key
        
        def do_request():
            r = requests.get(url, params=p, headers=self._headers(), timeout=30)
            if r.status_code == 401:
                self.get_token()
                r = requests.get(url, params=p, headers=self._headers(), timeout=30)
            r.raise_for_status()
            return r.json()
        
        return retry_request(do_request)

    def get_wilayah(self):
        return self._get("/layanan/peserta-didik/spmb/referensi-wilayah")

    def get_sekolah(self, kode_wilayah, page=1, per_page=100):
        return self._get("/layanan/peserta-didik/spmb/sekolah-by-wilayah", {
            "kode_wilayah": kode_wilayah,
            "page": page,
            "per_page": per_page,
        })

    def get_siswa_by_npsn(self, npsn, page=1, per_page=100):
        return self._get("/layanan/peserta-didik/spmb/peserta-didik-by-npsn", {
            "npsn": npsn,
            "page": page,
            "per_page": per_page,
        })

    def get_tka(self, nisn, tanggal_lahir):
        return self._get("/layanan/peserta-didik/spmb/peserta-didik-tka", {
            "nisn": nisn,
            "tanggal_lahir": tanggal_lahir,
        })
