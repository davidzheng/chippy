import sys
from cpu import CPU

if __name__ == '__main__':
    chip8 = CPU() 
    chip8.load_rom(sys.argv[1])


