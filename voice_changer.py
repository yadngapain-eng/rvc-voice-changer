
import os
import sys
import subprocess
import gdown

def run_cmd(cmd):
    print(f"Menjalankan: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

# Hanya butuh 1 argumen: Link Audio GDrive
audio_url = sys.argv[1]

# --- 1. CEK CACHE RVC ---
rvc_dir = "Retrieval-based-Voice-Conversion-WebUI"
if not os.path.exists(rvc_dir):
    print("Folder RVC belum ada. Meng-clone dari GitHub...")
    run_cmd(["git", "clone", "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git", rvc_dir])
else:
    print("✅ Folder RVC sudah ada di cache. Skip clone.")

os.chdir(rvc_dir)

# --- 2. DOWNLOAD AUDIO DARI GDRIVE ---
print("Mengunduh file audio dari Google Drive...")
gdown.download(audio_url, "../input.wav", quiet=False, fuzzy=True)

# Model sudah diunduh otomatis oleh Workflow GitHub ke assets/weights/female_model.pth
model_path = "female_model.pth"

# --- 3. PROSES KONVERSI ---
print("Memulai konversi suara (CPU Mode)...")
cmd = [
    "python", "infer_cli.py",
    "--input_path", "../input.wav",
    "--opt_path", "../output.wav",
    "--model_name", model_path,
    "--f0method", "rmvpe",
    "--f0up_key", "12" 
]

try:
    run_cmd(cmd)
    print("Konversi Berhasil!")
except Exception as e:
    print(f"Error: {e}")
    print("Mencoba metode fallback (hanya ubah pitch)...")
    run_cmd(["ffmpeg", "-y", "-i", "../input.wav", "-af", "asetrate=44100*1.4,aresample=44100", "../output.wav"])

os.chdir("..")
print("Selesai.")
