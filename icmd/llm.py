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
    

def llm(input):
    ensure_ollama()
    PROMPT = f"""
        You are a advanced linux terminal assistant.
        For every user query you will return corresponding linux bash command as response.
        You only return commands and should not explain using comments.

        Examples:
        query: "list me all the files"
        reponse: "ls"

        query: "print the working directory"
        response: "pwd"
        
        (MUST!!!) Ensure the command does not involve any critical system operations
        - Deleting a file/folder
        - Accessing root user
        - Accessing important system files, etc.
        If so return "Cannot process this request" as response
        
        Now return bash command for this query with out any quotes:
        '{input}'
    """

    data = {
        "model": MODEL,
        "prompt": PROMPT,
        "stream": False
    }
    
    response = requests.post(f"{OLLAMA_URL}/api/generate", json=data)
    response.raise_for_status()
    return response.json()["response"]
