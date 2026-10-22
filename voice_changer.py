
import os
import sys
import subprocess
import gdown

# Ambil argumen dari GitHub Actions
audio_url = sys.argv[1]
model_url = sys.argv[2] if len(sys.argv) > 2 else ""

print("Mengunduh file audio dari Google Drive...")
gdown.download(audio_url, "input.wav", quiet=False, fuzzy=True)

print("Mengunduh Model Suara (jika ada)...")
model_path = ""
if model_url:
    gdown.download(model_url, "model.pth", quiet=False, fuzzy=True)
    model_path = "model.pth"
else:
    print("Tidak ada model yang diunduh. Menggunakan model default.")

# Clone RVC
print("Menyiapkan RVC...")
if not os.path.exists("Retrieval-based-Voice-Conversion-WebUI"):
    subprocess.run(["git", "clone", "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git"])
os.chdir("Retrieval-based-Voice-Conversion-WebUI")

# Install dependencies (Menggunakan CPU)
subprocess.run(["pip", "install", "-r", "requirements.txt"])
subprocess.run(["pip", "install", "torch", "torchaudio", "faiss-cpu"])

# Pindahkan model ke folder yang benar
if model_path:
    os.makedirs("assets/weights", exist_ok=True)
    os.rename(f"../{model_path}", "assets/weights/model.pth")

print("Memulai konversi suara (CPU Mode)...")
# Perintah inferensi RVC
cmd = [
    "python", "infer_cli.py",
    "--input_path", "../input.wav",
    "--opt_path", "../output.wav",
    "--model_name", "model.pth" if model_path else "default.pth",
    "--f0method", "rmvpe",
    "--f0up_key", "12" # Naikkan 12 semitone (pria ke wanita)
]

try:
    subprocess.run(cmd, check=True)
    print("Konversi Berhasil!")
except Exception as e:
    print(f"Error: {e}")
    # Jika model gagal, coba tanpa model spesifik (hanya ubah pitch)
    print("Mencoba metode fallback (hanya ubah pitch)...")
    subprocess.run(["ffmpeg", "-i", "../input.wav", "-af", "asetrate=44100*1.5,aresample=44100", "../output.wav"])

# Kembali ke folder utama
os.chdir("..")
print("Selesai.")
