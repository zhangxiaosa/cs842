import os, re, sys
import subprocess
import glob

def execute(cmd):
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #subprocess.Popen(cmd, shell=True)

def cleanup(path):
    print("starting: cleanup")
    for f in glob.glob(path + '/**/*.gcov', recursive=True):
        execute("rm %s" % f)
        print("removed %s" % f)
    for f in glob.glob(path + '/**/*.gcda', recursive=True):
        execute("rm %s" % f)
        print("removed %s" % f)

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

cleanup(coverage_path)

for test_case in benchmark:
    print("starting: ", test_case)
    cmd = "%s %s %s %s" % (gcc_path, opt_level, other_flags, test_case)
    execute(cmd)
