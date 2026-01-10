import subprocess, time, sys, os, yaml
from colorama import Fore, Back, Style
from cf_problem_get import *
from yaml_helper import *

config_file = ".check60.yaml"

if len(sys.argv) == 1:
    print("check60 utility.\nusage: check60 <test name>\nFor usage you need file '.check60.yaml'.\n\nUse 'check60 -w' or 'check60 --web' for copy examples from Codeforces using extension for Chrome\nUse 'check60 -c <link>' or 'check60 --copy <link>' for copy examples from problem on codeforces\nUse flag '-se' if you need to continue check when check60 find an error\nFor init file '.check60.yaml', type 'check60 -i'\nFor init clear '.check60.yaml' file, type 'check60 -ic'\n\nFor read old config files ('check60.json'), use flag '-j' or '--json'")
    sys.exit(0)

if sys.argv[1] == "--init" or sys.argv[1] == "-i":
    with open(config_file, "w") as f:
        data = {
            "py-example": {
                "compile": "",
                "runs": [
                    {
                        "start": "python test.py",
                        "input": yaml_string("10\n2\n", style="|"),
                        "output": yaml_string("5.0\n", style="|"),
                        "timeout": 1000
                    },
                    {
                        "start": "python test.py",
                        "input": yaml_string("30\n5\n", style="|"),
                        "output": yaml_string("6.0\n", style="|"),
                        "timeout": 1000
                    },
                    {
                        "start": "python test.py",
                        "input": yaml_string("10\n4\n", style="|"),
                        "output": yaml_string("2.5\n", style="|"),
                        "timeout": 1000
                    }
                ]
            },
            "cpp-example": {
                "compile": "clang test.cpp -o test",
                "runs": [
                    {
                        "start": ".\\test",
                        "input": yaml_string("10\n2\n", style="|"),
                        "output": yaml_string("5.0\n", style="|"),
                        "timeout": 1000
                    },
                    {
                        "start": ".\\test",
                        "input": yaml_string("30\n5\n", style="|"),
                        "output": yaml_string("6.0\n", style="|"),
                        "timeout": 1000
                    },
                    {
                        "start": ".\\test",
                        "input": yaml_string("10\n4\n", style="|"),
                        "output": yaml_string("2.5\n", style="|"),
                        "timeout": 1000
                    }
                ]
            }
        }
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    sys.exit(0)

if sys.argv[1] == "--init-clear" or sys.argv[1] == "-ic":
    with open(config_file, "w") as f:
        data = {
            "check": {
                "compile": "",
                "runs": [
                    {
                        "start": "",
                        "input": "",
                        "output": "",
                        "timeout": 1000
                    }
                ]
            }
        }
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    sys.exit(0)

if "--json" in sys.argv or "-j" in sys.argv:
    config_file = "check60.json"

if sys.argv[1] == "-c" or sys.argv[1] == "--copy":
    link = sys.argv[2]
    contest, problem = get_contest_problem_fr_link(link)
    name = contest + "-" + problem
    print("[check60] try to get examples, now will open Chrome / Chromium window...")
    data = get_examples_undetected(link=link)
    if len(data) == 0:
        print(Fore.RED + "[check60] couldn't get the data" + Fore.RESET)
        sys.exit(1)
    new_test(name, data, config_test)
    print(Fore.GREEN + f"[check60] test is written as '{name}'" + Fore.RESET)
    sys.exit(0)


if sys.argv[1] == "-w" or sys.argv[1] == "--web":
    try:
        get_from_extension(config_file)
    except KeyboardInterrupt:
        print(Fore.GREEN + "[check60] done" + Fore.RESET)
    sys.exit(0)

try:
    config = yaml.safe_load(open(config_file, "r"))
except FileNotFoundError:
    print(Fore.RED + "[check60] config file not found"+Fore.RESET)
    sys.exit(1)

exitOnError = "-se" not in sys.argv

test = sys.argv[1]
allcorrect = True

if test not in config:
    print(Fore.RED + f"[check60] key not found: {test}"+Fore.RESET)
    sys.exit(1)

try:
    compile = os.system(config[test]["compile"])
except KeyError:
    print(Fore.RED + f"[check60] key not found: {test}['compile']"+Fore.RESET)

    sys.exit(1)

if compile == 0:
    print(Fore.GREEN+"[compile] the file is compiled\n"+Fore.RESET)

    n = 0
    incorrect = 0
    correct = 0
    for j in config[test]["runs"]:
        n += 1
        res_time = 0
        return_code = 0
        stdout = ""; stderr = ""
        startedAt = time.time()
        try:
            process = subprocess.Popen(
                j["start"].split(" "),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except FileNotFoundError:
            print(Fore.RED + f"[check60] failed to complete '{j["start"]}': file not found" + Fore.RESET)
            sys.exit(1)
        try:
            if j["timeout"] != 0:
                stdout, stderr = process.communicate(input=j["input"], timeout=float(j["timeout"] / 1000))
            else:
                stdout, stderr = process.communicate(input=j["input"])
            res_time = (time.time() - startedAt) * 1000
        except subprocess.TimeoutExpired:
            print(Fore.RED + f"[test {n}] timeout expired: {j["timeout"]} ms" + Fore.RESET)
            allcorrect = False
            incorrect += 1
            continue

        if stdout == j["output"]:
            print(Fore.GREEN + f"[test {n}] result: ok. time: {res_time:.2f} ms" + Fore.RESET)
            correct += 1
        else:
            print(Fore.RED + f"[test {n}] result: incorrect\n\tactual: {repr(stdout)}\n\texcepted: {repr(j["output"])}" + Fore.RESET)
            allcorrect = False
            incorrect += 1

        if stderr != "":
            print(Fore.RED + f"\n[check60] error in test {n}:{Fore.RESET}\n{stderr}" + Fore.RESET)
            if exitOnError: 
                break

    if allcorrect:
        print("\n[check60] test result: ok")
    else:
        print(f"\n[check60] test result:\n\t{Fore.GREEN}correct: {correct}\n\t{Fore.RED}incorrect: {incorrect}{Fore.RESET}")
        sys.exit(1)

else: 
    print(Fore.RED+f"[check60] Compilation failed. The process ended with the code {compile}"+Fore.RESET)
    sys.exit(1)
    # config[i]