import os, re, sys
import subprocess
import glob
import json
import time

def execute(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.wait()

def compile(cmd):
    time_start = time.time()
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.wait()
    time_end = time.time()
    size = os.path.getsize("a.out")
    return time_end - time_start, size

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
    time_list = []
    size_list = []
    for test_case in benchmark:
        #print("starting: ", test_case)
        cmd = "%s %s %s %s" % (gcc_path, opt_level, gcc_flags, test_case)
        #print("cmd: ", cmd)
        time, size = compile(cmd)
        time_list.append(time)
        size_list.append(size)
    time_avg = 1.0 * sum(time_list) / len(time_list)
    size_avg = 1.0 * sum(size_list) / len(size_list)
    
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
                line_number = data_for_line["line_number"]
                if (data_for_line["count"] > 0):
                    fcov.add_line_exe(line_number)
                else:
                    fcov.add_line_unexe(line_number)
            # iterate each func
            for data_for_func in data_for_file["functions"]:
                func_name = data_for_func["demangled_name"]
                if (data_for_func["execution_count"] > 0):
                    fcov.add_func_exe(func_name)
                else:
                    fcov.add_func_unexe(func_name)
    
    # summary coverage info
    func_num_exe = 0
    func_num_unexe = 0
    line_num_exe = 0
    line_num_unexe = 0
    file_exe = []
    file_unexe = []

    for file_name, data in source_files.items():
        func_num_exe = func_num_exe + len(data.func_set_exe)
        func_num_unexe = func_num_unexe + len(data.func_set_unexe)
        line_num_exe = line_num_exe + len(data.line_set_exe)
        line_num_unexe = line_num_unexe + len(data.line_set_unexe)

        # file level
        if (len(data.line_set_exe) >  0):
            file_exe.append(file_name)
        else:
            file_unexe.append(file_name)

    file_exe.sort()
    file_unexe.sort()
    return line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_exe, file_unexe, time_avg, size_avg

def read_optfile(file_name):
    with open(file_name, "r") as f:
        opts = f.readlines()
    opts = [opt.rstrip() for opt in opts]
    return opts

if __name__ == '__main__':

    opts = read_optfile("finer_opts/O3_disable.txt")

    num = 0
    while(num < len(opts)):
        current_opts = opts[:num]
        opts_string = "-O3 " + " ".join(current_opts)
        line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_exe, file_unexe, time_avg, size_avg = collect_coverage_of_options(opts_string) 
        if (len(current_opts) == 0):
            opt_this_time = []
        else:
            opt_this_time = current_opts[-1]
        print("disabled opt num: %d, this time %s, executed line num: %d, unexecuted line num: %d, executed func num: %d, unexecuted func num: %d, executed file num: %d, unexecuted file num: %d, time: %f, size: %f" % (len(current_opts), opt_this_time, line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, len(file_exe), len(file_unexe), time_avg, size_avg))
        with open("covered_files/%d_covered.txt" % len(current_opts), "w") as f:
            for filename in file_exe:
                f.write(filename)
                f.write("\n")
        with open("covered_files/%d_uncovered.txt" % len(current_opts), "w") as f:
            for filename in file_unexe:
                f.write(filename)
                f.write("\n")
        num = num + 1   
    
#if __name__ == '__main__':
#
#    opts_string = "-Os "
#    line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe, time_avg, size_avg = collect_coverage_of_options(opts_string) 
#    print("executed line num: %d, unexecuted line num: %d, executed func num: %d, unexecuted func num: %d, executed file num: %d, unexecuted file num: %d, time: %f, size: %f" % (line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe, time_avg, size_avg))
