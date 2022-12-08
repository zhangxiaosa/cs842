import os, re, sys
import shutil

with open("uncovered.txt", "r") as f:
    filenames = f.readlines()

filenames = [filename.strip() for filename in filenames]
for filename in filenames:
    if (filename.endswith(".c") or filename.endswith(".h") or filename.endswith(".cc")):
        filename_backup = filename + ".backup"
        shutil.copyfile(filename_backup, filename)

