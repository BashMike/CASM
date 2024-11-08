python casm.py code.casm
rm ./casm_machine
g++ -Wno-format -o casm_machine main.cpp
./casm_machine
