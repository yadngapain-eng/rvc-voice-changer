import os
import sys
import subprocess
import gdown

_RVC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Retrieval-based-Voice-Conversion-WebUI')
if os.path.isdir(_RVC_DIR) and _RVC_DIR not in sys.path:
    sys.path.insert(0, _RVC_DIR)

def run_cmd(cmd):
    print(f"Menjalankan: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if len(sys.argv) < 2:
    print("Usage: python voice_changer.py <audio_url> [model_name]")
    sys.exit(1)

audio_url  = sys.argv[1]
model_name = sys.argv[2] if len(sys.argv) > 2 else "V2-AISO-HOWATTO"

rvc_dir = "Retrieval-based-Voice-Conversion-WebUI"

# Pastikan folder ada (Workflow YAML yang bertanggung jawab meng-clone & checkout)
if not os.path.isdir(rvc_dir):
    print("Error: Folder RVC tidak ditemukan. Pastikan step Clone di YAML berhasil!")
    sys.exit(1)

print("Mengunduh file audio dari Google Drive...")
input_wav  = os.path.abspath("input.wav")
output_wav = os.path.abspath("output.wav")

result = gdown.download(audio_url, input_wav, quiet=False)
if result is None or not os.path.exists(input_wav):
    print("Gagal mengunduh audio.")
    sys.exit(1)

os.chdir(rvc_dir)

# Cek infer_cli.py
infer_script = "infer_cli.py"
if not os.path.exists(infer_script):
    print("Error: infer_cli.py tidak ditemukan di folder repo RVC!")
    print("Isi folder saat ini:", os.listdir("."))
    sys.exit(1)

model_file = os.path.join("assets", "weights", f"{model_name}.pth")
index_file = os.path.join("assets", "weights", "trained_IVF832_Flat_nprobe_1_v2.index")

if not os.path.exists(model_file):
    print(f"Error: Model {model_file} tidak ditemukan!")
    sys.exit(1)

print(f"Memakai model: {model_name}")

index_path_arg = []
if os.path.exists(index_file):
    index_path_arg = ["--index_path", index_file]

cmd = [
    sys.executable, infer_script,
    "--input_path", input_wav,
    "--opt_path",  output_wav,
    "--model_name", model_name,
    "--f0method", "rmvpe",
    "--f0up_key", "12",
    "--index_rate", "0.75",
    "--device", "cpu"
] + index_path_arg

try:
    run_cmd(cmd)
    print("Konversi Berhasil!")
except Exception as e:
    print(f"Error: {e}")
    print("Fallback ke ffmpeg pitch shift...")
    os.chdir("..")
    run_cmd(["ffmpeg", "-y", "-i", input_wav, "-af", "asetrate=44100*1.4,aresample=44100", output_wav])
    print("Selesai (fallback).")
    sys.exit(0)

os.chdir("..")
print("Selesai.")
