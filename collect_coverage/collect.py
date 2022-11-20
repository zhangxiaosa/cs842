import os, re, sys
import subprocess
import glob
import json

def execute(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #proc = subprocess.Popen(cmd, shell=True)
    proc.wait()

def cleanup(path, extension):
    print("starting: cleanup %s in %s" % (extension, path))
    for f in glob.glob(path + '/**/*.%s' % extension, recursive=True):
        execute("rm %s" % f)
        print("removed %s" % f)

def find_files(path, extension):
    return glob.glob(path + '/**/*.%s' % extension, recursive=True)


opt_level = "-O2"
gcc_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/bin/gcc"
gcc_flags = "-I /usr/local/include/csmith/"
gcov_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/bin/gcov"
gcov_flags = "-i"
benchmark_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/benchmark/"
gcda_result_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/gcc/"
gcov_result_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/collect_coverage/gcov_result/"


# cleanup gcda
cleanup(gcda_result_path, "gcda")

# run benchmark
benchmark = find_files(benchmark_path, 'c')
for test_case in benchmark:
    print("starting: ", test_case)
    cmd = "%s %s %s %s" % (gcc_path, opt_level, gcc_flags, test_case)
    execute(cmd)

# cleanup gcov
cleanup(gcov_result_path, "gz")
cleanup(gcov_result_path, "json")

# generate gcov files
gcda_files = find_files(gcda_result_path, "gcda")
os.chdir(gcov_result_path)
for gcda_file in gcda_files:
    execute("%s %s %s" % (gcov_path, gcov_flags, gcda_file))
gz_files = find_files(gcov_result_path, "gz")
for gz_file in gz_files:
    execute("gunzip %s" % gz_file)
os.chdir("..")

# collect coverage info
json_files = find_files(gcov_result_path, "json")
line_number = 0
for json_file in json_files:
    with open(json_file, "r") as f:
        data = json.load(f)
    for data_for_file in data["files"]:
        for data_for_line in data_for_file["lines"]:
            if (data_for_line["count"] > 0):
                line_number = line_number + 1

print(line_number)








