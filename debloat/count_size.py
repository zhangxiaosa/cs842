import os, re, sys
import hashlib

root = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0-debloat/build/bin"
files = os.listdir(root)
files.sort()

total = 0
for item in files:
    size = os.path.getsize(os.path.join(root, item))
    total = total + size
    
print(total)


