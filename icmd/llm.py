import os
import re
import subprocess
from huggingface_hub import hf_hub_download

MODEL_REPO = "MSDeepak718/qwen-icmd"
MODEL_FILE = "qwen-icmd-q4.gguf"

CACHE_DIR = os.path.expanduser("~/.icmd_model")
MODEL_PATH = os.path.join(CACHE_DIR, MODEL_FILE)

# Path to bundled llama binary
LLAMA_BIN = os.path.join(os.path.dirname(__file__), "bin/llama-cli")


def ensure_model():
    os.makedirs(CACHE_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        print("Downloading iCMD model (~400MB)...")

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
