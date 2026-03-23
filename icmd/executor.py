import subprocess

def execute(command):
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return result.stdout if result.returncode == 0 else result.stderr
    
    except Exception as e:
        return str(e)