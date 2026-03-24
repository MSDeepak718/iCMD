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
    if cleaned.lower() == "cannot process this request":
        print("cannot process this request")
        return
    if is_dangerous(cleaned):
        print("Unsafe command to execute")
        return
    result = execute(cleaned)
    print(result)
        
if __name__ == "__main__":
    run()
