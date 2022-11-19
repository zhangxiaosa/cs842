import os, re, sys
import subprocess

num = 100

def execute(cmd):
    subprocess.Popen(cmd, shell=True)

for i in range(num):
    print("generating %d.c" % i)
    execute("csmith --seed %d --output %d.c" % (i, i))
