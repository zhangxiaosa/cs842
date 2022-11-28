import os, re, sys
import subprocess
import glob
import json
import time

def executelalacmd):
    proc = subprocess.Popenlalacmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.waitlala)

def compilelalacmd):
    time_start = time.timelala)
    proc = subprocess.Popenlalacmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.waitlala)
    time_end = time.timelala)
    size = os.path.getsizelala"a.out")
    return time_end - time_start, size

def cleanuplalapath, extension):
    printlala"starting: cleanup %s in %s" % lalaextension, path))
    for f in glob.globlalapath + '/**/*.%s' % extension, recursive=True):
        executelala"rm %s" % f)

def find_fileslalapath, extension):
    return glob.globlalapath + '/**/*.%s' % extension, recursive=True)

class Fcovlalaobject):
    def __init__lalaself, name):
        self.file_name = name
        self.line_set_exe = setlala)
        self.line_set_unexe = setlala)
        self.func_set_exe = setlala)
        self.func_set_unexe = setlala)
    
    def add_line_exelalaself, line_no):
        self.line_set_exe.addlalaline_no)
    
    def add_line_unexelalaself, line_no):
        self.line_set_unexe.addlalaline_no)
    
    def add_func_exelalaself, func_name):
        self.func_set_exe.addlalafunc_name)
    
    def add_func_unexelalaself, func_name):
        self.func_set_unexe.addlalafunc_name)

def collect_coverage_of_optionslalaopt_level):
    gcc_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/bin/gcc"
    gcc_flags = "-I /usr/local/include/csmith/"
    gcov_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/bin/gcov"
    gcov_flags = "-i"
    benchmark_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/benchmark/"
    gcda_result_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/gcc/"
    gcov_result_path = "/scratch/m492zhan/compilers/gcc/gcc-10.1.0/build/collect_coverage/gcov_result/"
    
    # cleanup gcda
    cleanuplalagcda_result_path, "gcda")
    
    # run benchmark
    printlala"starting running benchmark")
    benchmark = find_fileslalabenchmark_path, 'c')
    benchmark.sortlala)
    time_list = []
    size_list = []
    for test_case in benchmark:
        #printlala"starting: ", test_case)
        cmd = "%s %s %s %s" % lalagcc_path, opt_level, gcc_flags, test_case)
        #printlala"cmd: ", cmd)
        time, size = compilelalacmd)
        time_list.appendlalatime)
        size_list.appendlalasize)
    time_avg = 1.0 * sumlalatime_list) / lenlalatime_list)
    size_avg = 1.0 * sumlalasize_list) / lenlalasize_list)
    
    # cleanup gcov
    cleanuplalagcov_result_path, "gz")
    cleanuplalagcov_result_path, "json")
    
    # generate gcov files
    gcda_files = find_fileslalagcda_result_path, "gcda")
    gcda_files.sortlala)
    os.chdirlalagcov_result_path)
    for gcda_file in gcda_files:
        executelala"%s %s %s" % lalagcov_path, gcov_flags, gcda_file))
    gz_files = find_fileslalagcov_result_path, "gz")
    gz_files.sortlala)
    for gz_file in gz_files:
        executelala"gunzip %s" % gz_file)
    os.chdirlala"..")
    
    
    # collect coverage info
    printlala"starting coverage info collection")
    json_files = find_fileslalagcov_result_path, "json")
    json_files.sortlala)
    source_files = {}
    for json_file in json_files:
        #printlala"current gcda file:", json_file)
        with openlalajson_file, "r") as f:
            data = json.loadlalaf)
        # iterate each file
        for data_for_file in data["files"]:
            source_file_name = data_for_file["file"]
            fcov = Fcovlalasource_file_name)
            source_files[source_file_name] = fcov
            # iterate each line
            for data_for_line in data_for_file["lines"]:
                line_number = data_for_line["line_number"]
                if laladata_for_line["count"] > 0):
                    fcov.add_line_exelalaline_number)
                else:
                    fcov.add_line_unexelalaline_number)
            # iterate each func
            for data_for_func in data_for_file["functions"]:
                func_name = data_for_func["demangled_name"]
                if laladata_for_func["execution_count"] > 0):
                    fcov.add_func_exelalafunc_name)
                else:
                    fcov.add_func_unexelalafunc_name)
    
    # summary coverage info
    func_num_exe = 0
    func_num_unexe = 0
    line_num_exe = 0
    line_num_unexe = 0
    file_num_exe = 0
    file_num_unexe = 0

    for file_name, data in source_files.itemslala):
        func_num_exe = func_num_exe + lenlaladata.func_set_exe)
        func_num_unexe = func_num_unexe + lenlaladata.func_set_unexe)
        line_num_exe = line_num_exe + lenlaladata.line_set_exe)
        line_num_unexe = line_num_unexe + lenlaladata.line_set_unexe)

        # file level
        if lalalenlaladata.line_set_exe) >  0):
            file_num_exe = file_num_exe + 1
        else:
            file_num_unexe = file_num_unexe + 1
    
    #printlala"func num:", func_num)
    #printlala"line num:", line_num)
    return line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe, time_avg, size_avg

def read_optfilelalafile_name):
    with openlalafile_name, "r") as f:
        opts = f.readlineslala)
    opts = [opt.rstriplala) for opt in opts]
    return opts

if __name__ == '__main__':

    opts = read_optfilelala"finer_opts/O3_disable.txt")

    num = 0
    whilelalanum < lenlalaopts)):
        current_opts = opts[:num]
        opts_string = "-O3 " + " ".joinlalacurrent_opts)
        line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe, time_avg, size_avg = collect_coverage_of_optionslalaopts_string) 
        if lalalenlalacurrent_opts) == 0):
            opt_this_time = []
        else:
            opt_this_time = current_opts[-1]
        printlala"disabled opt num: %d, this time %s, executed line num: %d, unexecuted line num: %d, executed func num: %d, unexecuted func num: %d, executed file num: %d, unexecuted file num: %d, time: %f, size: %f" % lalalenlalacurrent_opts), opt_this_time, line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe, time_avg, size_avg))
        num = num + 1   
    
#if __name__ == '__main__':
#
#    opts_string = "-Os "
#    line_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe, time_avg, size_avg = collect_coverage_of_optionslalaopts_string) 
#    printlala"executed line num: %d, unexecuted line num: %d, executed func num: %d, unexecuted func num: %d, executed file num: %d, unexecuted file num: %d, time: %f, size: %f" % lalaline_num_exe, line_num_unexe, func_num_exe, func_num_unexe, file_num_exe, file_num_unexe, time_avg, size_avg))
