import sys
import pygame

class Display():
    """
    Emulates the display of a Chip-8 system. The orignal implementation is a monochrome display
    and has a width of 64 pixels and a height of 32 pixels. The upper left corner is considered 
    the (0,0) coordinate and the bottom left is considered the (63, 31) coordinate. Sprites are 
    8x5 pixels on the display. 
    """
    def __init__(self, width = 64, height = 32, scale = 10):
        """ 
        Sets the proper dimensions for Chip-8 screen. Scale is the value width and height are 
        multiplied by since 64x32 pixels is small on modern systems.
        """
        self.width = width
        self.height = height
        self.scale = scale
        self.display = None
        self.colors = [
            (0, 0, 0, 255),
            (250, 250, 250, 255)
        ]

    """
    Initializes the display based on the given scale. Adds a title to the display and colors the 
    display to the default color of a Chip-8 program.
    """
    def init_display(self):
        true_width = self.width * self.scale
        true_height = self.height * self.scale
        self.display = pygame.display.set_mode((true_width, true_height))
        pygame.display.set_caption("Chippy: Chip-8 Emulator")
        self.clear_display()
        self.update_display()

    """
    Updates the full display Surface of pygame to the screen
    """
    def update_display(self):
        pygame.display.flip()

    def clear_display(self):
        self.display.fill(self.colors[0])

    def check_pixel(self, x_coord, y_coord):
        x = x_coord * self.scale
        y = y_coord * self.scale
        if self.display.get_at((x, y)) == self.colors[0]:
            return 0
        else:
            return 1

    def set_pixel(self, x_coord, y_coord, color):
        x = x_coord * self.scale
        y = y_coord * self.scale
        print(str(x) + " " + str(y))
        pygame.draw.rect(self.display, self.colors[color],(x, y, self.scale, self.scale)) 
