import os, re, sys
import subprocess

opt_levels = ['O0','O1', 'O2', 'O3', 'Os']
gcc_path = "../bin/gcc"
opt_dir = "finer_opts"
for opt_level in opt_levels:
    res_bytes = subprocess.Popen(gcc_path + ' -Q --help=optimizers -%s' % opt_level, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res_list = res_bytes.stdout.read().decode('utf-8').split('\n')
    opt_file = open(opt_dir + '/' + opt_level + '.txt', 'w')
    for res in res_list:
        print(res)
        if not '-f' in res or '[disabled]' in res:
            continue
        else:
            opt_file.write(res + '\n')
