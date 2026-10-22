import os
import sys
import subprocess
import gdown

_RVC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'Retrieval-based-Voice-Conversion-WebUI')
if os.path.isdir(_RVC_DIR) and _RVC_DIR not in sys.path:
    sys.path.insert(0, _RVC_DIR)


def run_cmd(cmd):
    print(f"Menjalankan: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if len(sys.argv) < 2:
    print("Usage: python voice_changer.py <audio_url> [model_name]")
    sys.exit(1)

audio_url  = sys.argv[1]
model_name = sys.argv[2] if len(sys.argv) > 2 else "f0G40k"

rvc_dir = "Retrieval-based-Voice-Conversion-WebUI"
if not os.path.isdir(rvc_dir):
    print("Folder RVC belum ada. Clone...")
    run_cmd(["git", "clone",
             "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git",
             rvc_dir])
else:
    print("Folder RVC sudah ada. Skip clone.")

print("Mengunduh file audio dari Google Drive...")
input_wav  = os.path.abspath("input.wav")
output_wav = os.path.abspath("output.wav")

result = gdown.download(audio_url, input_wav, quiet=False)
if result is None or not os.path.exists(input_wav):
    print("Gagal mengunduh audio.")
    sys.exit(1)
print(f"Audio: {input_wav}")

os.chdir(rvc_dir)

model_file = os.path.join("assets", "weights", f"{model_name}.pth")
if not os.path.exists(model_file):
    print(f"PERINGATAN: {model_file} tidak ada. Fallback ke f0G40k...")
    model_name = "f0G40k"
    model_file = os.path.join("assets", "weights", "f0G40k.pth")
    if not os.path.exists(model_file):
        print("Fallback gagal, coba ffmpeg pitch shift...")
        os.chdir("..")
        run_cmd(["ffmpeg", "-y", "-i", input_wav,
                 "-af", "asetrate=44100*1.4,aresample=44100", output_wav])
        sys.exit(0)

print(f"Memakai model: {model_name}")

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
    print("Fallback ke ffmpeg pitch shift...")
    run_cmd(["ffmpeg", "-y", "-i", input_wav,
             "-af", "asetrate=44100*1.4,aresample=44100", output_wav])
finally:
    os.chdir("..")

print("Selesai.")
