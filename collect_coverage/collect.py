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

class Fcov(object):
    def __init__(self, name):
        self.file_name = name
        self.line_num_exe = 0
        self.line_num_unexe = 0
        self.func_set_exe = set()
        self.func_set_unexe = set()

    def add_line_exe(self):
        self.line_num_exe = self.line_num_exe + 1

    def add_line_unexe(self):
        self.line_num_unexe = self.line_num_unexe + 1

    def add_func_exe(self, func_name):
        self.func_set_exe.add(func_name)

    def add_func_unexe(self, func_name):
        self.func_set_unexe.add(func_name)

# collect coverage info
json_files = find_files(gcov_result_path, "json")
source_files = {}
for json_file in json_files:
    with open(json_file, "r") as f:
        data = json.load(f)
    # iterate each file
    for data_for_file in data["files"]:
        source_file_name = data_for_file["file"]
        fcov = Fcov(source_file_name)
        source_files[source_file_name] = fcov
        # iterate each line
        for data_for_line in data_for_file["lines"]:
            if (data_for_line["count"] > 0):
                fcov.add_line_exe()
            else:
                fcov.add_line_unexe()
        # iterate each func
        for data_for_func in data_for_file["functions"]:
            func_name = data_for_func["demangled_name"]
            if (data_for_func["blocks_executed"] > 0):
                fcov.add_func_exe(func_name)
            else:
                fcov.add_func_unexe(func_name)
        print("current file:", source_file_name)
        print("line_exe:", fcov.line_num_exe)
        print("line_unexe:", fcov.line_num_unexe)
        print("func_exe:", fcov.func_set_exe)
        print("func_unexe:", fcov.func_set_unexe)








