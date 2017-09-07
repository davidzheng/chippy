import os

class CPU():
    def __init__(self):
        self.memory = [None] * 4096
        self.registers = [None] * 16
        self.address = [None] * 16
        self.stack = [None] * 16
        self.key = [None] * 16
        self.display_pixels = [[0 for _ in range(64)] for _ in range(32)] 
        self.pc = 0x200
        self.sp = 0
        self.delay_timer = 0
        self.sound_timer = 0
    
    def load_rom(self, rom_name):
        print("Loading %s..." % (rom_name))
        os.chdir('..')
        os.chdir('roms')
        try:
            rom = open(rom_name, "rb")
        except IOError:
            print("Rom does not exist, please enter a valid rom file.")
            sys.exit()
        else:
            rom_bytes = rom.read()
            if len(rom_bytes) > (4096 - 512):
                print("Rom file is too large, please choose a valid rom file.")
            #print(len(rom_string))
            for byte in range(0, len(rom_bytes)):
                self.memory[byte + 512] = rom_bytes[byte]

            #print(rom_bytes[0] << 8 | rom_bytes[1])
            print("Done loading %s!" %(rom_name))
            rom.close()




