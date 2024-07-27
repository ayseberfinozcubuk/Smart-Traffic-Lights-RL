import pygame
from enum import Enum

class Direction(Enum):
    HORIZONTAL = 1
    VERTICAL = 2

class Road:
    def __init__(self, start_x, start_y, end_x, end_y, color) -> None:
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.color = color
        self.direction = Direction.VERTICAL
        if abs(self.start_x - self.end_x) > abs(self.start_y - self.end_y):
            self.direction = Direction.HORIZONTAL
        self.stopping_area = self.calculate_stopping_area()

    def calculate_stopping_area(self):
        if self.direction == Direction.HORIZONTAL:
            stop_end_x = self.start_x + (self.end_x - self.start_x) // 2
            return (self.start_x, self.start_y, stop_end_x, self.end_y)
        else:
            stop_end_y = self.start_y + (self.end_y - self.start_y) // 2
            return (self.start_x, self.start_y, self.end_x, stop_end_y)

    def draw(self, surface):
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        pygame.draw.rect(surface, self.color, pygame.Rect(self.start_x, self.start_y, width, height))

    def draw_stopping_area(self, surface, color):
        width = abs(self.stopping_area[2] - self.stopping_area[0])
        height = abs(self.stopping_area[3] - self.stopping_area[1])
        pygame.draw.rect(surface, color, pygame.Rect(self.stopping_area[0], self.stopping_area[1], width, height))

    def is_inside(self, x, y):
        return (self.start_x <= x <= self.end_x) and (self.start_y <= y <= self.end_y)
    
    def count_cars_in_area(self, all_cars):
        count = 0
        for car in all_cars:
            car_center_x = car.x + car.width / 2
            car_center_y = car.y + car.height / 2
            
            if (self.stopping_area[0] <= car_center_x <= self.stopping_area[2]) and (self.stopping_area[1] <= car_center_y <= self.stopping_area[3]):
                count += 1
        return count

    def get_size(self):
        return abs(self.end_x - self.start_x), abs(self.end_y - self.start_y)
