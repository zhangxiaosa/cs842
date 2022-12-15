import os, re, sys
import shutil
import subprocess

def execute(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.wait()


with open("uncovered.txt", "r") as f:
    filenames = f.readlines()

filenames = [filename.strip() for filename in filenames]
for filename in filenames:
    if (filename.endswith(".c") or filename.endswith(".h") or filename.endswith(".cc")):
        if (filename.startswith("#")):
            continue
        print("debloating %s" % filename)
        execute("./debloat %s -- \"true\" \"void bool int\"" % filename)

