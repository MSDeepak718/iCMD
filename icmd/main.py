import sys
import platform
from importlib.metadata import metadata
from icmd.llm import llm
from icmd.executor import execute
from icmd.safety import is_dangerous
from icmd.utils import clean

def run():
    if len(sys.argv)==2 and sys.argv[1]== "--author":
        meta = metadata("icmd-cli")
        print(meta["Author"])
        return
    
    if len(sys.argv) < 2:
        print("Usage: icmd \"your query\"")
        return
    OS = platform.system()
    query = " ".join(sys.argv[1:])
    command = llm(query, OS)
    cleaned = clean(command)
    if cleaned.lower().startswith("error running model"):
        print(cleaned)
        return
    if not cleaned:
        print("No command was generated")
        return
    if cleaned.lower() == "cannot process this request":
        print("cannot process this request")
        return
    if is_dangerous(cleaned):
        print("Unsafe command to execute")
        return
    print(f"$ {cleaned}")
    result = execute(cleaned)
    if result:
        print(result)
    else:
        print("Command executed successfully but produced no output")
        
if __name__ == "__main__":
    run()
