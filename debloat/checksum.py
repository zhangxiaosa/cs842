import os, re, sys
import hashlib

root = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0-debloat/build/bin"
files = os.listdir(root)
files.sort()

checksum = b"666"
for item in files:
    with open(os.path.join(root, item), "rb") as f:
        content = f.read()
        current_checksum = hashlib.md5(content).hexdigest().encode()
        checksum = checksum + current_checksum
    

overall_checksum = hashlib.md5(checksum).hexdigest().encode()
print(overall_checksum)
print(checksum)


