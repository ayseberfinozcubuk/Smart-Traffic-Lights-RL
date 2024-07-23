import pygame
import math

class Car:
    MAX_SPEED = 2  

    def __init__(self, x, y, width, height, color, speed_x, speed_y):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.original_speed_x = speed_x
        self.original_speed_y = speed_y
        
        # Determine the car's direction based on speed
        self.direction = (1 if speed_x > 0 else -1 if speed_x < 0 else 0,
                          1 if speed_y > 0 else -1 if speed_y < 0 else 0)
        
        # Determine rotation angle
        if self.direction == (0, 1) or self.direction == (0, -1):
            self.rotation = 90 if self.direction[1] > 0 else -90
        else:
            self.rotation = 0

    def draw(self, surface):
        car_surface = pygame.Surface((self.width, self.height))
        car_surface.fill(self.color)
        
        # Rotate the car surface if needed
        rotated_surface = pygame.transform.rotate(car_surface, self.rotation)
        rect = rotated_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        
        surface.blit(rotated_surface, rect.topleft)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def check_collision(self, other_car):
        # Simple bounding box collision detection
        return (self.x < other_car.x + other_car.width and
                self.x + self.width > other_car.x and
                self.y < other_car.y + other_car.height and
                self.y + self.height > other_car.y)

    def is_in_proximity(self, other_car, distance):
        # Check if another car is within a certain distance ahead of this car
        if self.speed_x > 0:  # Moving right
            return self.x < other_car.x < self.x + distance and self.y == other_car.y
        elif self.speed_x < 0:  # Moving left
            return self.x - distance < other_car.x < self.x and self.y == other_car.y
        elif self.speed_y > 0:  # Moving down
            return self.y < other_car.y < self.y + distance and self.x == other_car.x
        elif self.speed_y < 0:  # Moving up
            return self.y - distance < other_car.y < self.y and self.x == other_car.x
        return False
