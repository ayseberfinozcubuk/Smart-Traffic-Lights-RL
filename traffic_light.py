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
        self.last_light_change_time = pygame.time.get_ticks()

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

    def update_light(self, current_time, light_change_interval):
        if current_time - self.last_light_change_time >= light_change_interval:
            next_light = {
                Light.RED: Light.GREEN,
                Light.GREEN: Light.RED,
            }.get(self.current_light, Light.RED)
            self.change_light(next_light)
            self.last_light_change_time = current_time

    def get_information(self):
        return self.current_light
