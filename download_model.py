import os
import sys
import requests
import zipfile
from pathlib import Path

# Baca token dari environment variable (yang di-set oleh GitHub Actions)
# atau dari file .env (jika dijalankan secara lokal)
def get_token():
    token = os.environ.get("GH_TOKEN")
    if token:
        return token
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.startswith("GH_TOKEN="):
                    return line.strip().split("=", 1)[1]
    return None

def download_release_asset(repo_owner, repo_name, tag, asset_name, dest_path, token):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    # 1. Dapatkan ID asset dari API
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{tag}"
    r = requests.get(api_url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching release info: {r.status_code}")
        sys.exit(1)
        
    assets = r.json().get("assets", [])
    asset_id = None
    actual_name = None
    for a in assets:
        if a["name"].endswith(".pth") or a["name"] == asset_name:
            # Jika mencari model, ambil .pth pertama jika yang dicari tidak persis sama
            if a["name"] == asset_name or asset_name.endswith(".pth"):
                asset_id = a["id"]
                actual_name = a["name"]
                break
    
    if not asset_id:
        print(f"Asset {asset_name} tidak ditemukan di release.")
        sys.exit(1)
        
    # 2. Download asset menggunakan header Accept: application/octet-stream
    print(f"Mengunduh {actual_name} via API...")
    download_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/assets/{asset_id}"
    headers["Accept"] = "application/octet-stream"
    
    with requests.get(download_url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
    print(f"✓ Tersimpan di {dest_path}")
    return actual_name

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python download_model.py <model_name> <index_name> <dest_dir>")
        sys.exit(1)
        
    model_name = sys.argv[1]
    index_name = sys.argv[2]
    dest_dir = sys.argv[3]
    
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    token = get_token()
    
    # Download model
    model_dest = os.path.join(dest_dir, f"{model_name}.pth")
    actual_model_name = download_release_asset("yadngapain-eng", "rvc-voice-changer", "v1.0", f"{model_name}.pth", model_dest, token)
    
    # Download index
    index_dest = os.path.join(dest_dir, index_name)
    download_release_asset("yadngapain-eng", "rvc-voice-changer", "v1.0", index_name, index_dest, token)
    
    # Print nama model asli jika berubah karena fallback
    if actual_model_name != f"{model_name}.pth":
        print(f"::warning::Model yang diunduh berbeda. Menggunakan nama: {actual_model_name.replace('.pth', '')}")
        # Simpan nama model untuk digunakan di script selanjutnya
        with open("model_name.txt", "w") as f:
            f.write(actual_model_name.replace('.pth', ''))
    else:
        with open("model_name.txt", "w") as f:
            f.write(model_name)
