import os, re, sys
import subprocess
import glob

def execute(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.wait()
    #subprocess.Popen(cmd, shell=True)

def cleanup(path, extension):
    print("starting: cleanup %s in %s" % (extension, path))
    for f in glob.glob(path + '/**/*.%s' % extension, recursive=True):
        execute("rm %s" % f)
        print("removed %s" % f)

def find_files(path, extension):
    return glob.glob(path + '/**/*.%s' % extension, recursive=True)


opt_level = "-O2"
gcc_path = "../bin/gcc"
gcc_flags = "-I /usr/local/include/csmith/"
gcov_path = "../bin/gcov"
gcov_flags = "-i"
benchmark_path = "../benchmark/"
gcda_result_path = "../gcc/"
gcov_result_path = "./gcov_result/"


# cleanup gcda
cleanup(gcda_result_path, "gcda")

# run benchmark
benchmark = find_files(benchmark_path, 'c')
for test_case in benchmark:
    print("starting: ", test_case)
    cmd = "%s %s %s %s" % (gcc_path, opt_level, gcc_flags, test_case)
    execute(cmd)

# cleanup gcov
cleanup(gcov_result_path, "gcov")

# generate gcov files
gcda_files = find_files(gcda_result_path, "gcda")
os.chdir(gcov_result_path)
for gcda_file in gcda_files:
    execute("%s %s %s" % (gcov_path, gcov_flags, gcda_file))
os.chdir("..")

