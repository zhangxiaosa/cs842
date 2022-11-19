import os, re, sys
import subprocess
import glob

def execute(cmd):
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #subprocess.Popen(cmd, shell=True)

def cleanup():
    pass

def run_testsuites():
    pass

def collect():
    pass

opt_level = "-O2"
gcc_path = "../bin/gcc/"
gcov_path = "../bin/gcov/"
benchmark_path = "../benchmark/"
coverage_path = "../gcc/"
other_flags = "-I /usr/local/include/csmith/"

benchmark = glob.glob(os.path.join(benchmark_path, '*.c'))

for test_case in benchmark:
    print("starting: ", test_case)
    cmd = "%s %s %s %s" % (gcc_path, opt_level, other_flags, test_case)
    execute(cmd)
