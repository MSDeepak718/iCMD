import os
import re
import sys
import stat
import platform
import zipfile
import tarfile
import subprocess
import urllib.request
from huggingface_hub import hf_hub_download

MODEL_REPO = "MSDeepak718/qwen-icmd"
MODEL_FILE = "qwen-icmd-f16.gguf"
LLAMA_VERSION = "b9095"

CACHE_DIR = os.path.expanduser("~/.icmd_model")
MODEL_PATH = os.path.join(CACHE_DIR, MODEL_FILE)

def get_llama_bin_path():
    ext = ".exe" if platform.system().lower() == "windows" else ""
    return os.path.join(CACHE_DIR, "bin", f"llama-cli{ext}")

LLAMA_BIN = get_llama_bin_path()

def ensure_llama_cli():
    if os.path.exists(LLAMA_BIN):
        return

    sys_name = platform.system().lower()
    machine = platform.machine().lower()

    if sys_name == "windows":
        asset_os = "win-cpu"
        arch = "arm64" if "arm" in machine else "x64"
        archive_ext = ".zip"
    elif sys_name == "darwin":
        asset_os = "macos"
        arch = "arm64" if "arm" in machine else "x64"
        archive_ext = ".tar.gz"
    else:
        asset_os = "ubuntu"
        arch = "arm64" if "arm" in machine or "aarch" in machine else "x64"
        archive_ext = ".tar.gz"

    asset_name = f"llama-{LLAMA_VERSION}-bin-{asset_os}-{arch}{archive_ext}"
    url = f"https://github.com/ggerganov/llama.cpp/releases/download/{LLAMA_VERSION}/{asset_name}"
    
    print(f"Downloading llama-cli {LLAMA_VERSION} for {sys_name} {arch}...")
    archive_path = os.path.join(CACHE_DIR, asset_name)
    
    try:
        urllib.request.urlretrieve(url, archive_path)
    except Exception as e:
        print(f"Failed to download from {url}: {e}")
        print("Please download the binary manually or check your internet connection.")
        sys.exit(1)
        
    print("Extracting llama-cli...")
    extract_dir = os.path.join(CACHE_DIR, "bin")
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        if archive_ext == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        else:
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                for member in tar_ref.getmembers():
                    parts = member.name.split('/', 1)
                    if len(parts) > 1:
                        member.name = parts[1]
                        tar_ref.extract(member, extract_dir)
    except Exception as e:
        print(f"Failed to extract {archive_path}: {e}")
        sys.exit(1)
        
    if os.path.exists(archive_path):
        os.remove(archive_path)
        
    if not os.path.exists(LLAMA_BIN):
        print("Could not find llama-cli in the downloaded archive.")
        sys.exit(1)

    if sys_name != "windows":
        st = os.stat(LLAMA_BIN)
        os.chmod(LLAMA_BIN, st.st_mode | stat.S_IEXEC)

def ensure_model():
    os.makedirs(CACHE_DIR, exist_ok=True)
    ensure_llama_cli()

    if not os.path.exists(MODEL_PATH):
        print("Downloading iCMD model from Hugging Face")

        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=MODEL_FILE,
            local_dir=CACHE_DIR
        )

def extract_command(raw_output, user_input):
    text = raw_output.replace("\r", "")
    prompt_markers = [
        f"input: {user_input}\noutput:",
        f"Request: {user_input}\nCommand:",
    ]

    for marker in prompt_markers:
        if marker in text:
            text = text.rsplit(marker, 1)[-1]
            break

    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        lower = line.lower()
        if (
            lower.startswith("loading model")
            or lower.startswith("build")
            or lower.startswith("model")
            or lower.startswith("modalities")
            or lower.startswith("available commands")
            or lower.startswith("exiting")
            or lower.startswith("/exit")
            or lower.startswith("/regen")
            or lower.startswith("/clear")
            or lower.startswith("/read")
            or lower.startswith("/glob")
            or lower.startswith("input:")
            or lower.startswith("output:")
            or lower.startswith("generate exactly one valid")
            or lower.startswith("rules:")
            or lower.startswith("- output only the command")
            or lower.startswith("- no explanation")
            or lower.startswith("- no markdown")
            or lower.startswith(">")
        ):
            continue

        if re.fullmatch(r"[▄█▀ ]+", line):
            continue

        lines.append(line)

    if not lines:
        return ""

    command_line_pattern = re.compile(r"^[A-Za-z0-9._/\-~]+(?:\s+[^[:cntrl:]\n\r]*)?$")

    for line in lines:
        if command_line_pattern.fullmatch(line):
            return line

    return lines[0]


def llm(user_input, OS):
    ensure_model()

    prompt = f"""Generate exactly one valid {OS} terminal command.
Rules:
- Output only the command
- No explanation
- No markdown

input: {user_input}
output:"""
    
    result = subprocess.run(
        [
            LLAMA_BIN,
            "-m", MODEL_PATH,
            "-p", prompt,
            "-n", "20",
            "--temp", "0.0",
            "--no-display-prompt",
            "--simple-io",
            "--single-turn",
            "--no-warmup",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    if result.returncode != 0:
        return f"Error running model: {result.stderr.strip() or result.stdout.strip() or 'unknown error'}"

    return extract_command(result.stdout, user_input)
