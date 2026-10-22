import os
import sys
import subprocess
import gdown

# Pastikan folder RVC bisa di-import
_RVC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'Retrieval-based-Voice-Conversion-WebUI')
if os.path.isdir(_RVC_DIR) and _RVC_DIR not in sys.path:
    sys.path.insert(0, _RVC_DIR)


def run_cmd(cmd):
    print(f"Menjalankan: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if len(sys.argv) < 2:
    print("Usage: python voice_changer.py <audio_url>")
    sys.exit(1)

audio_url = sys.argv[1]
rvc_dir = "Retrieval-based-Voice-Conversion-WebUI"

# --- 1. CEK FOLDER RVC ---
if not os.path.isdir(rvc_dir):
    print("Folder RVC belum ada. Meng-clone dari GitHub...")
    run_cmd(["git", "clone",
             "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git",
             rvc_dir])
else:
    print("Folder RVC sudah ada. Skip clone.")

# --- 2. DOWNLOAD AUDIO DARI GDRIVE ---
print("Mengunduh file audio dari Google Drive...")
# Simpan input di root repo (bukan di dalam rvc_dir)
input_wav = os.path.abspath("input.wav")
output_wav = os.path.abspath("output.wav")

# gdown 6.x tidak punya 'fuzzy'; deteksi otomatis URL GDrive
result = gdown.download(audio_url, input_wav, quiet=False)
if result is None or not os.path.exists(input_wav):
    print("Gagal mengunduh audio dari Google Drive.")
    sys.exit(1)
print(f"Audio tersimpan di: {input_wav}")

# --- 3. PROSES KONVERSI ---
os.chdir(rvc_dir)

# Path model relatif ke rvc_dir
model_name = "female_model"  # tanpa .pth, RVC mencari di assets/weights/
model_file = os.path.join("assets", "weights", f"{model_name}.pth")
if not os.path.exists(model_file):
    print(f"PERINGATAN: model {model_file} tidak ada!")
    print("File .pth mungkin 404 saat diunduh. Cek GitHub Release.")
    sys.exit(1)

print("Memulai konversi suara (CPU Mode)...")
cmd = [
    sys.executable, "infer_cli.py",
    "--input_path", input_wav,
    "--opt_path",  output_wav,
    "--model_name", model_name,
    "--f0method", "rmvpe",
    "--f0up_key", "12",
]

try:
    run_cmd(cmd)
    print("Konversi Berhasil!")
except Exception as e:
    print(f"Error: {e}")
    print("Fallback: ubah pitch dengan ffmpeg...")
    run_cmd(["ffmpeg", "-y", "-i", input_wav,
             "-af", "asetrate=44100*1.4,aresample=44100",
             output_wav])
finally:
    os.chdir("..")

print("Selesai.")
