# This script will toggle the comment/uncommenting aspect for dealing
# with __file__ AttributeError arising in case of a few modules in
# `torch/_dynamo/skipfiles.py` (within shark.venv)

from distutils.sysconfig import get_python_lib
import fileinput
from pathlib import Path

path_to_skipfiles = Path(get_python_lib() + "/torch/_dynamo/skipfiles.py")

modules_to_comment = ["abc,", "os,", "posixpath,", "_collections_abc,"]
startMonitoring = 0
for line in fileinput.input(path_to_skipfiles, inplace=True):
    if "SKIP_DIRS = " in line:
        startMonitoring = 1
        print(line, end="")
    elif startMonitoring in [1, 2]:
        if "]" in line:
            startMonitoring += 1
            print(line, end="")
        else:
            flag = True
            for module in modules_to_comment:
                if module in line:
                    if not line.startswith("#"):
                        print(f"#{line}", end="")
                    else:
                        print(f"{line[1:]}", end="")
                    flag = False
                    break
            if flag:
                print(line, end="")
    else:
        print(line, end="")
