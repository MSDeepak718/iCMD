import requests
import subprocess

MODEL = "qwen2.5-coder"
OLLAMA_URL = 'http://localhost:11434'

def ensure_ollama():
    try:
        requests.get(OLLAMA_URL)
        res = requests.get(f"{OLLAMA_URL}/api/tags").json()
        models = [m["name"] for m in res.get("models", [])]
    
        if not any(model == MODEL or model.startswith(f"{MODEL}:") for model in models):
            subprocess.run(
                ["ollama", "pull", MODEL],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
    except Exception:
        print("Ollama is not installed or running.")
        print("Install from: https://ollama.com")
        exit()
    

def llm(input, OS):
    ensure_ollama()
    PROMPT = f"""
        You are an expert terminal command generator.

        Your task:
        Convert the user query into a SAFE and VALID {OS} terminal command.

        Rules:
            - Output ONLY the command (no explanations, no comments, no extra text)
            - The command must be valid for {OS}
            - If multiple commands are needed, combine them using appropriate operators
            - If the request is unsafe, output exactly: Cannot process this request

        Strict Safety Rules (DO NOT VIOLATE):
            - No file/folder deletion (rm, del, rmdir, etc.)
            - No system-level access (sudo, root, system32, etc.)
            - No modification of system files
            - No destructive operations

        OS-specific behavior:
            - Windows → Use CMD/PowerShell compatible commands
            - Linux/macOS → Use bash/zsh commands

        Examples:

        OS: Linux
        Query: list all files
        Output: ls

        OS: Windows
        Query: list all files
        Output: dir

        OS: Linux
        Query: show current directory
        Output: pwd

        OS: Windows
        Query: show current directory
        Output: cd

        Now generate the command for:

        Query: {input}
    """
    
    data = {
        "model": MODEL,
        "prompt": PROMPT,
        "stream": False
    }
    
    response = requests.post(f"{OLLAMA_URL}/api/generate", json=data)
    response.raise_for_status()
    return response.json()["response"]
