import pygame

class ChippyScreen():
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

