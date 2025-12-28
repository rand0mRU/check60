import json
import subprocess
import sys
import os
from colorama import Fore, Back, Style

if len(sys.argv) == 1:
    print("check60 utility.\nusage: check60 <name of test>\nFor usage you need file 'check60.json'.\n\nFor init, type 'check60 -i'\nFor init clear 'check60.json' file, type 'check60 -ic'")
    sys.exit(0)

if sys.argv[1] == "--init" or sys.argv[1] == "-i":
    with open("check60.json", "w") as f:
        f.write(r"""{
    "py-example": {
        "compile": "",
        "runs": [
            {
                "start": "python test.py",
                "input": "10\n2\n",
                "output": "5.0\n"
            },
            {
                "start": "python test.py",
                "input": "30\n5\n",
                "output": "6.0\n"
            },
            {
                "start": "python test.py",
                "input": "10\n4\n",
                "output": "2.5\n"
            }
        ]
    },
    "cpp-example": {
        "compile": "clang test.cpp -o test",
        "runs": [
            {
                "start": ".\\test",
                "input": "10\n2\n",
                "output": "5.0\n"
            },
            {
                "start": ".\\test",
                "input": "30\n5\n",
                "output": "6.0\n"
            },
            {
                "start": ".\\test",
                "input": "10\n4\n",
                "output": "2.5\n"
            }
        ]
    }
}""")
    sys.exit(0)

if sys.argv[1] == "--init-clear" or sys.argv[1] == "-ic":
    with open("check60.json", "w") as f:
        f.write(r"""{
    "check": {
        "compile": "",
        "runs": [
            {
                "start": "",
                "input": "",
                "output": ""
            }
        ]
    }
}""")
    sys.exit(0)

try:
    config = json.load(open("check60.json", "r"))
except FileNotFoundError:
    print(Fore.RED + "[check60] config file not found"+Fore.RESET)
    sys.exit(0)

test = sys.argv[1]
allcorrect = True

try:
    compile = os.system(config[test]["compile"])
except KeyError:
    print(Fore.RED + "[check60] KeyError"+Fore.RESET)
    sys.exit(0)

if compile == 0:
    print(Fore.GREEN+"[compile] the file is compiled\n"+Fore.RESET)

    n = 1
    incorrect = 0
    correct = 0
    for j in config[test]["runs"]:
        process = subprocess.Popen(
            j["start"].split(" "),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=j["input"])

        if stdout == j["output"]:
            print(Fore.GREEN+f"[test {n}] result: ok"+Fore.RESET)
            correct += 1
        else:
            print(Fore.RED+f"[test {n}] result: incorrect\n\tactual: {repr(stdout)}\n\texcepted: {repr(j["output"])}"+Fore.RESET)
            allcorrect = False
            incorrect += 1

        if stderr != "":
            print(Fore.RED + f"\n[check60] error in test {n}:{Fore.RESET}\n{stderr}" + Fore.RESET)

        n += 1
    if allcorrect:
        print("\n[check60] test result: ok")
    else:
        print(f"\n[check60] test result:\n\t{Fore.GREEN}correct: {correct}\n\t{Fore.RED}incorrect: {incorrect}{Fore.RESET}")

else: 
    print(Fore.RED+f"[check60] Compilation failed. The process ended with the code {compile}"+Fore.RESET)
    # config[i]