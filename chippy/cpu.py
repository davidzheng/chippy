class CPU():
    def __init__(self):
        self.memory = [None] * 4096
        self.registers = [None] * 16
        self.address = [None] * 16
        self.stack = [None] * 16
        self.key = [None] * 16
        self.display_pixels = [[0 for _ in range(65)] for _ in range(33)] 
        self.pc = 0x200
        self.sp = 0
        self.delay_timer = 0
        self.sound_timer = 0
