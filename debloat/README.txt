tutorial:
https://clang.llvm.org/docs/LibASTMatchersTutorial.html

the path of source code:
/scratch/m492zhan/compilers/llvm/clang-llvm/llvm-project/clang/tools

how to build:
cd /scratch/m492zhan/compilers/llvm/clang-llvm/build
cmake -G Ninja ../llvm-project/llvm/ -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -DLLVM_BUILD_TESTS=ON -DCMAKE_INSTALL_PREFIX=/scratch/m492zhan/compilers/llvm/clang-llvm/build/build
ninja or ninja debloat
