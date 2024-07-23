import pygame
from road import Road
from enum import Enum

class Light(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3  # Optional for future states

class TrafficLight:
    def __init__(self, location_x, location_y, road: Road) -> None:
        self.location_x = location_x
        self.location_y = location_y
        self.road = road
        self.current_light = Light.RED  

    def draw(self, surface):
        # Define dimensions for the traffic light circle
        circle_radius = 10
        light_color_map = {
            Light.RED: (255, 0, 0),
            Light.GREEN: (0, 255, 0),
            Light.BLUE: (0, 0, 255)
        }
        
        pygame.draw.circle(surface, light_color_map[self.current_light], (self.location_x, self.location_y), circle_radius)

    def change_light(self, light: Light):
        self.current_light = light

    def get_information(self):
        return f"Traffic Light at ({self.location_x}, {self.location_y}) is {self.current_light.name}"
