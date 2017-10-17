import os
import random

class CPU(object):
    """
    The Chip-8 has 4KB of RAM from 0x000 to 0xFFF. The original interpreter is stored in memory 
    from 0x000 to 0x1FF so most programs will start at 0x200. The Chip-8 has 16 8-bit registers
    and a 16-bit register that stores memory addresses. There are also 2 8-bit registers that 
    are the delay and sound timers. The stack can hold 16 16-bit values. The Chip-8 had a 16-bit
    keypad from 0~9 and A~F.
    """
    def __init__(self, display):
        """
        Initializes all the needed components of the Chip-8 CPU to their proper values
        """
        self.memory = [0] * 4096  
        self.registers = [0] * 16
        self.address = [0] * 16
        self.stack = [0] * 16
        self.keys = [0] * 16
        self.display_pixels = [[0 for _ in range(64)] for _ in range(32)] 
        self.pc = 0x200
        self.sp = 0
        self.register_I = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.display = display
        self.draw = False 
        
        self.font_set = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4 
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5 
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6 
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7 
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8 
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A 
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B 
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
            ]

        for x in range(0, len(self.font_set)):
            self.memory[x] = self.font_set[x]

    def testing(self):
        for num in range (0, len(self.registers)):
            print("V" + str(num) + ": " +  str(self.registers[num]))
        print("I: " + str(self.register_I))
        print("pc: " + str(self.pc))
        print("sp: " + str(self.sp))
        print("dt: " + str(self.delay_timer))
        print("st: " + str(self.sound_timer))
    def load_rom(self, rom_name):
        """
        Checks if the user entered rom name exists in the proper directory. If the rom exists
        and is a valid Chip-8 rom, it is stored into the proper addresses in the CPU memory.
        """
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
            # First 512 bytes are used by the Chip-8 font set.
            if len(rom_bytes) > (4096 - 512):
                print("Rom file is too large, please choose a valid rom file.")
            #print(len(rom_string))
            # Loads rom into memory starting from the address after the first 512 addresses
            for byte in range(0, len(rom_bytes)):
                self.memory[byte + self.pc] = rom_bytes[byte]
            print("Done loading %s!" %(rom_name))
            rom.close()

    def timer_decrement(self):
        if self.delay_timer != 0:
            self.delay_timer -= 1
        if self.sound_timer != 0:
            self.sound_timer -= 1

    def get_opcode(self):
        """      
        Combines bytes in adjacent memory addresses to create a 2 byte long opcode. Left shifts the 
        first byte by 8 bits and performs a bitwise OR operation to change the created mask into
        the values of the second byte.
        """
        first_byte = self.memory[self.pc]
        second_byte = self.memory[self.pc + 1]
        opcode = (first_byte << 8 | second_byte)
        return opcode

    def perform_opcode(self, opcode):
        """
        Decodes the given opcode by identifying the first hexidecimal value. If required, the last 
        hexidecimal value is also identified and the decoded opcode is performed. The pc is then
        advanced based on the opcode.
        """
        # Identify first hex to determine which opcode nibble to perform
        first_hex = opcode & 0xF000
        if first_hex == 0x0000:
            last_hex = opcode & 0x000F
            # Opcode 00E0: clear screen
            if last_hex == 0x0000:
                self.display.clear_display()
                self.draw = True
                self.pc += 2 
            # Opcode 00EE: returns from subroutine
            elif last_hex == 0x000E: 
                #self.sp -= 1
                self.pc = self.stack[self.sp]
                self.sp -= 1
                self.pc += 2

        # Opcode 1NNN: Jump to address NNN        
        elif first_hex == 0x1000:
            # Get last 3 hex values
            address = opcode & 0x0FFF
            self.pc = address

        # TODO check implementation
        # Opcode 2NNN: Call subroutine at NNN
        # Adds current pc to stack and increments sp 
        elif first_hex == 0x2000:
            address = opcode & 0x0FFF
            self.stack[self.sp] = self.pc
            self.sp += 1
            self.pc = address
        # Opcode 3XKK: Skips next instruction if value stored in register X = KK
        elif first_hex == 0x3000:
            if (self.registers[(opcode & 0x0F00) >> 8] == (opcode & 0x00FF)):
                self.pc += 4
            else:
                self.pc += 2
        
        # Opcode 4XKK: Skips next instruction if value stored in register X != KK
        elif first_hex == 0x4000:
            if (self.registers[(opcode & 0x0F00) >> 8] != (opcode & 0x00FF)):
                self.pc += 4
            else:
                self.pc += 2

        # Opcode 5XY0: Skips next instruction if value stored in register X = value in register Y    
        elif first_hex == 0x5000:
            if (self.registers[(opcode & 0x0F00) >> 8] == self.registers[(opcode & 0x00F0) >> 4]):
                self.pc += 4
            else:
                self.pc += 2

        # Opcode 6XKK: Load KK into register X 
        elif first_hex == 0x6000:
            value = opcode & 0x00FF
            self.registers[(opcode & 0x0F00) >> 8] = value
            self.pc += 2

        # Opcode 7XKK: Adds KK to the value in register X and stores it in register X
        elif first_hex == 0x7000:
            self.registers[(opcode & 0x0F00) >> 8] += (opcode & 0x00FF)
            self.pc += 2

        elif first_hex == 0x8000:
            last_hex = opcode & 0x000F
            # Opcode 8XY0: Set value of register X to the value of register Y
            if last_hex == 0x000:
                self.registers[(opcode & 0x0F00) >> 8] = self.registers[(opcode & 0x00F0) >> 4]
                self.pc += 2
            # Opcode 8XY1: Set value of register X to (value of register X OR value of register Y)
            elif last_hex == 0x001:
                self.registers[(opcode & 0x0F00) >> 8] |= self.registers[(opcode & 0x00F0) >> 4]
                self.pc += 2 
            # Opcode 8XY2: Set value of register X to (value of register X AND value of register Y)
            elif last_hex == 0x002:
                self.registers[(opcode & 0x0F00) >> 8] &= self.registers[(opcode & 0x00F0) >> 4]
                self.pc += 2
            # Opcode 8XY3: Set value of register X to (value of register X XOR value of register Y)
            elif last_hex == 0x003:
                self.registers[(opcode & 0x0F00) >> 8] ^= self.registers[(opcode & 0x00F0) >> 4]
                self.pc += 2
            # Opcode 8XY4: Set value of register X to (value of register X ADD value of register Y) and set carry
            elif last_hex == 0x004:
                value_sum  = self.registers[(opcode & 0x0F00) >> 8] + self.registers[(opcode & 0x00F0) >> 4]
                # Only keeps the lowest 8 bits if the sum is greater than 0xFF and sets the carry register to 1
                if value_sum > 0xFF:
                    self.registers[0xF] = 1
                    self.registers[(opcode & 0x0F00) >> 8] = (value_sum & 0x00FF)
                else:
                    self.registers[0xF] =0
                    self.registers[(opcode & 0x0F00) >> 8] = value_sum
                self.pc += 2
            # Opcode 8XY5: Set value of register X to (value of register X SUB value of register Y)
            elif last_hex == 0x005:
                # Sets carry register to 0 if there is a borrow else set to 1
                if (self.registers[(opcode & 0x0F00) >> 8] > self.registers[(opcode & 0x00F0) >> 4]):
                    self.registers[0xF] = 1
                else: 
                    self.registers[0xF] = 0
                self.registers[(opcode & 0x0F00) >> 8] -= self.registers[(opcode & 0x00F0) >> 4]
                self.pc += 2
            # Opcode 8XY6: Right shift the value of register X by 1
            elif last_hex == 0x006:
                # Keeps the least significant bit of the value of register X in register F
                self.registers[0xF] = (self.registers[(opcode & 0x0F00) >> 8] & 0x0001)
                self.registers[(opcode & 0x0F00) >> 8] = (self.registers[(opcode & 0x0F00) >> 8] >> 1)
                self.pc += 2
            # Opcode 8XY7: Set value of register X to (value of register Y SUB value of register X)
            elif last_hex == 0x007:
                # Sets carry register to 0 if there is a borrow else set to 1
                if (self.registers[(opcode & 0x0F00) >> 8] < self.registers[(opcode & 0x00F0) >> 4]):
                    self.registers[0xF] = 1
                else:
                    self.registers[0xF] = 0
                self.registers[(opcode & 0x0F00) >> 8] = self.registers[(opcode & 0x00F0) >> 4] - self.registers[(opcode & 0x0F00) >> 8]
                self.pc += 2
            # Opcode 8XYE: Left shift the value of register X by 1
            elif last_hex == 0x00E:
                # Keeps the most significant bit of the value of register X in register F
                self.registers[0xF] = (self.registers[(opcode & 0x0F00) >> 8] >> 7)
                self.registers[(opcode & 0x0F00) >> 8] = (self.registers[(opcode & 0x0F00) >> 8] << 1)
                self.pc += 2

        # Opcode 9XY0: Skip next instruction if value of register X != value of register Y
        elif first_hex == 0x9000:
            if self.registers[(opcode & 0x0F00) >> 8] != self.registers[(opcode & 0x00F0) >> 4]:
                self.pc += 4
            else:
                self.pc += 2

        # Opcode ANNN: Set value of register I to NNN
        elif first_hex == 0xA000:
            self.register_I = (opcode & 0x0FFF)
            self.pc += 2

        # Opcode BNNN: Jump to location NNN + value of register 0
        elif first_hex == 0xB000:
            self.pc = (opcode & 0x0FFF) + self.registers[0]

        # Opcode CXKK: Sets the value of register X to (random byte AND KK)
        elif first_hex == 0xC000:
            random_byte = randint(0, 255) 
            self.registers[(opcode & 0x0F00) >> 8] = (random_byte & (opcode & 0x00FF))
            self.pc += 2

        # Opcode DXYN: Display an N-byte sprite starting at memory location I at (value of register X, value of register Y)
        # Set value of register F to 1 if collision else set it to 0
        elif first_hex == 0xD000:
            n = opcode & 0x000F
            x = opcode & 0x0F00 >> 8
            y = opcode & 0x00F0 >> 4
            start_location = self.register_I
            self.registers[0x000F] = 0
            
            for y_val in range(n):
                sprite_byte = self.memory[self.register_I + y_val]
                sprite_byte = bin(sprite_byte)[2:]
                sprite_byte = sprite_byte.zfill(8)
                y_coord = y + y_val
                y_coord_adjusted = y_coord % self.display.height
                
                for x_val in range(8):
                    x_coord = x + x_val
                    x_coord_adjusted = x_coord % self.display.width
                    pixel_color = int(sprite_byte[x_val])
                    current_pixel = self.display.check_pixel(x_coord_adjusted, y_coord_adjusted)
                    if pixel_color == 1 and current_pixel == 1:
                        self.registers[0x000F] == 1
                        pixel_color = 0
                    elif pixel_color == 0 and current_pixel == 1:
                        pixel_color == 1
                    self.display.set_pixel(x_coord_adjusted, y_coord_adjusted, pixel_color)
                
            self.draw = True 
            self.pc += 2
         
        elif first_hex == 0xE000:
            last_hex = opcode & 0x000F
            # TODO implement pygame keys
            # Opcode EX9E: Skips the next instruction if key with the value of register X is pressed
            if last_hex == 0x000E:
                if self.keys[(opcode & 0x0F00) >> 8] != 0:
                    self.pc += 4
                else:
                    self.pc += 2
            # Opcode EXA1: Skips the next instruction if key with the value of register X is not pressed
            if last_hex == 0x0001:
                if self.keys[(opcode & 0x0F00) >> 8] == 0:
                    self.pc += 4
                else:
                    self.pc +=2
        
        elif first_hex == 0xF000:
            last_hex = opcode & 0x000F
            # Opcode FX07: Set the value of register X to the value of the delay timer
            if last_hex == 0x0007:
                self.registers[(opcode & 0x0F00) >> 8] = self.delay_timer
                self.pc += 2
            # TODO implement pygame keys
            # Opcode FX0A: Wait for a key press and stores the value of the pressed key into register X
            if last_hex == 0x000A:
                key_was_pressed = False
                while key_was_pressed is not True:
                    for key in range(0, len(self.keys)):
                        if key is not 0:
                            self.registers[(opcode & 0x0F00) >> 8] = key
                            key_was_pressed = True
                self.pc += 2
            # Opcode FX15: Set the value of the delay timer to the value of register X
            if last_hex == 0x0005:
                self.delay_timer = self.registers[(opcode & 0x0F00) >> 8] 
                self.pc += 2
            # Opcode FX18: Set the value of the sound timer to the value of register X
            if last_hex == 0x0008:
                self.sound_timer = self.registers[(opcode & 0x0F00) >> 8]
                self.pc += 2
            # Opcode FX1E: Set the value of register I to (value of register I + value of register X)
            if last_hex == 0x000E:
                self.register_I += self.registers[(opcode & 0x0F00) >> 8]
                self.pc += 2
            # Opcode FX29: Set value of register I to the location of sprite for the digit of the value of register X
            # Sprites are 5 bytes long so the value of register X must be multiplied by 5
            if last_hex == 0x0009:
                self.register_I = self.registers[(opcode & 0x0F00) >> 8] * 0x000F
                self.pc += 2
            # Opcode FX33: Store the binary-coded decimal representation of the value of register X in memory locations I, I+1, and I+2
            if last_hex == 0x0003:
                value = self.registers[(opcode & 0x0F00) >> 8] 
                difference = 2
                while difference >= 0:
                    self.memory[self.register_I + difference] = value % 10
                    value = value // 10
                    difference -= 1
                self.pc += 2
            # Opcode Fx55: Store the values of register 0 through X in memory starting in location of the value of register I
            if last_hex == 0x0005:
                location = 0
                end = (opcode & 0x0F00) >> 8
                while location <= end:
                    self.memory[self.register_I + location] = self.registers[location]
                    location += 1
                self.pc += 2
            # Opcode FX65: Load the registers 0 through X with values starting from the address of the value of register I
            if last_hex == 0x0006:
                location = 0
                end = (opcode & 0x0F00) >> 8
                while location <= end:
                    self.registers[location] = self.memory[self.regsiter_I + location]
                    location += 1
                self.pc += 2
        else:
            print("Invalid opcode, chippy will now quit")
            quit()

    def perform_cycle(self):
        current_opcode = self.get_opcode()
        print(hex(current_opcode))
        self.testing()
        self.perform_opcode(current_opcode)
        if self.draw == True:
            self.display.update_display()
            self.draw = False
    
