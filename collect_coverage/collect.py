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

def find_files(path, extension):
    return glob.glob(path + '/**/*.%s' % extension, recursive=True)

class Fcov(object):
    def __init__(self, name):
        self.file_name = name
        self.line_set_exe = set()
        self.line_set_unexe = set()
        self.func_set_exe = set()
        self.func_set_unexe = set()
    
    def add_line_exe(self, line_no):
        self.line_set_exe.add(line_no)
    
    def add_line_unexe(self, line_no):
        self.line_set_unexe.add(line_no)
    
    def add_func_exe(self, func_name):
        self.func_set_exe.add(func_name)
    
    def add_func_unexe(self, func_name):
        self.func_set_unexe.add(func_name)

def collect_coverage_of_options(opt_level):
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
    print("starting running benchmark")
    benchmark = find_files(benchmark_path, 'c')
    benchmark.sort()
    for test_case in benchmark:
        #print("starting: ", test_case)
        cmd = "%s %s %s %s" % (gcc_path, opt_level, gcc_flags, test_case)
        execute(cmd)
    
    # cleanup gcov
    cleanup(gcov_result_path, "gz")
    cleanup(gcov_result_path, "json")
    
    # generate gcov files
    gcda_files = find_files(gcda_result_path, "gcda")
    gcda_files.sort()
    os.chdir(gcov_result_path)
    for gcda_file in gcda_files:
        execute("%s %s %s" % (gcov_path, gcov_flags, gcda_file))
    gz_files = find_files(gcov_result_path, "gz")
    gz_files.sort()
    for gz_file in gz_files:
        execute("gunzip %s" % gz_file)
    os.chdir("..")
    
    
    # collect coverage info
    print("starting coverage info collection")
    json_files = find_files(gcov_result_path, "json")
    json_files.sort()
    source_files = {}
    for json_file in json_files:
        #print("current gcda file:", json_file)
        with open(json_file, "r") as f:
            data = json.load(f)
        # iterate each file
        for data_for_file in data["files"]:
            source_file_name = data_for_file["file"]
            fcov = Fcov(source_file_name)
            source_files[source_file_name] = fcov
            # iterate each line
            for data_for_line in data_for_file["lines"]:
                func_name = data_for_line["line_number"]
                if (data_for_line["count"] > 0):
                    fcov.add_line_exe(func_name)
                else:
                    fcov.add_line_unexe(func_name)
            # iterate each func
            for data_for_func in data_for_file["functions"]:
                func_name = data_for_func["demangled_name"]
                if (data_for_func["blocks_executed"] > 0):
                    fcov.add_func_exe(func_name)
                else:
                    fcov.add_func_unexe(func_name)
            #print("current file:", source_file_name)
            #print("line_exe:", len(fcov.line_set_exe))
            #print("line_unexe:", len(fcov.line_set_unexe))
            #print("func_exe:", len(fcov.func_set_exe))
            #print("func_unexe:", len(fcov.func_set_unexe))
    
    # deduplicate
    print("starting deduplication")
    for file_name, fcov in source_files.items():
        fcov.line_set_unexe = fcov.line_set_unexe - fcov.line_set_exe
        fcov.func_set_unexe = fcov.func_set_unexe - fcov.func_set_exe
    
    # summary coverage info
    func_num_exe = 0
    func_num_unexe = 0
    line_num_exe = 0
    line_num_unexe = 0
    file_num_exe = 0
    file_num_unexe = 0

    for file_name, data in source_files.items():
        func_num_exe = func_num_exe + len(data.func_set_exe)
        func_num_unexe = func_num_unexe + len(data.func_set_unexe)
        line_num_exe = line_num_exe + len(data.line_set_exe)
        line_num_unexe = line_num_unexe + len(data.line_set_unexe)

        # file level
        if (len(data.line_set_exe) >  0):
            file_num_exe = file_num_exe + 1
        else:
            file_num_unexe = file_num_unexe + 1
    
    #print("func num:", func_num)
    #print("line num:", line_num)

    return line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe


opt_level_list = ["-O0", "-O1", "-O2", "-Os", "-O3"]

for opt_level in opt_level_list:
    line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe = collect_coverage_of_options(opt_level) 
    print("opt_level: %s, executed line num: %d, unexecuted line num: %d, executed func num: %d, unexecuted func num: %d, executed file num: %d, unexecuted file num: %d" % (opt_level, line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe))


