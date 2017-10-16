import sys
import pygame
from cpu import CPU
from display import Display
if __name__ == '__main__':
    chip8_display = Display()
    chip8_display.init_display()
    chip8 = CPU(chip8_display) 
    chip8.load_rom(sys.argv[1])
    running = True
    while(running):
        chip8.perform_cycle()
        if chip8.memory[chip8.pc] == None:
           sys.exit()

