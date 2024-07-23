# road.py

import pygame

class Road:
    def __init__(self, start_x, start_y, end_x, end_y, color) -> None:
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.color = color

    def draw(self, surface):
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        
        pygame.draw.rect(surface, self.color, pygame.Rect(self.start_x, self.start_y, width, height))

    def is_inside(self, x, y):
        # Check if a point (x, y) is within the rectangle representing the road
        return (self.start_x <= x <= self.end_x) and (self.start_y <= y <= self.end_y)
