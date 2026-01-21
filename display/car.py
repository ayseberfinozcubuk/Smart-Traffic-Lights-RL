import pygame
import datetime
import csv
import os
from display.traffic_light import Light

class Car:
    MAX_SPEED = 25
    MIN_SPEED = 25

    def __init__(self, x, y, width, height, color, speed_x, speed_y):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.original_width = width
        self.original_height = height
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.original_speed_x = speed_x
        self.original_speed_y = speed_y
        self.crashed = False
        self.reached_end = False
        self.waiting_duration = 0
        

        self.direction = (1 if speed_x > 0 else -1 if speed_x < 0 else 0,
                          1 if speed_y > 0 else -1 if speed_y < 0 else 0)
        
        if self.direction == (0, 1) or self.direction == (0, -1):
            self.rotation = 90 if self.direction[1] > 0 else -90
            self.width, self.height = self.height, self.width
        else:
            self.rotation = 0

    def draw(self, surface):
        car_surface = pygame.Surface((self.original_width, self.original_height))
        car_surface.fill(self.color)
        

        rotated_surface = pygame.transform.rotate(car_surface, self.rotation)
        rect = rotated_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        
        surface.blit(rotated_surface, rect.topleft)



    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def check_collision(self, other_car):

        return (self.x < other_car.x + other_car.width and
                self.x + self.width > other_car.x and
                self.y < other_car.y + other_car.height and
                self.y + self.height > other_car.y)
    
    def check_spawn_point_collision(self, x, y, width, height):
        # Check collision with a safety margin to prevent spawning too close
        margin = 15
        
        # Check if the spawning box (x, y, w, h) intersects with 
        # the existing car's box expanded by margin
        return (x < self.x + self.width + margin and
                x + width > self.x - margin and
                y < self.y + self.height + margin and
                y + height > self.y - margin)

    def is_in_proximity(self, other_car, distance):
        # Check if another car is within a certain distance ahead of this car
        if self.speed_x > 0:  # Moving right
            return self.x < other_car.x < self.x + distance and abs(self.y - other_car.y) < self.height
        elif self.speed_x < 0:  # Moving left
            return self.x - distance < other_car.x < self.x and abs(self.y - other_car.y) < self.height
        elif self.speed_y > 0:  # Moving down
            return self.y < other_car.y < self.y + distance and abs(self.x - other_car.x) < self.width
        elif self.speed_y < 0:  # Moving up
            return self.y - distance < other_car.y < self.y and abs(self.x - other_car.x) < self.width
        return False

    def get_car_in_proximity(self, all_cars, distance):
        closest_car = None
        min_dist = float('inf')
        
        for other_car in all_cars:
            if self != other_car and self.is_in_proximity(other_car, distance) and other_car.direction == self.direction:
                # Calculate distance
                dist = float('inf')
                if self.speed_x > 0:
                    dist = other_car.x - self.x
                elif self.speed_x < 0:
                    dist = self.x - other_car.x
                elif self.speed_y > 0:
                    dist = other_car.y - self.y
                elif self.speed_y < 0:
                    dist = self.y - other_car.y
                
                if dist < min_dist:
                    min_dist = dist
                    closest_car = other_car
                    
        return closest_car

    def stop_if_red_lights(self, traffic_lights):
        for traffic_light in traffic_lights:
            if traffic_light.current_light == Light.RED:
                if traffic_light.road.is_inside(self.x, self.y):
                    self.speed_x = 0
                    self.speed_y = 0
                    self.waiting_duration += 1
                    return
        self.speed_x = self.original_speed_x
        self.speed_y = self.original_speed_y

    def update(self, all_cars, traffic_lights, speed_reduction_distance):


        self.stop_if_red_lights(traffic_lights)

        car_in_proximity = self.get_car_in_proximity(all_cars, speed_reduction_distance)

        # Adjust speeds based on proximity
        if car_in_proximity:
            if car_in_proximity.speed_x < self.speed_x:
                self.speed_x = car_in_proximity.speed_x
            if car_in_proximity.speed_y < self.speed_y:
                self.speed_y = car_in_proximity.speed_y
            if (self.speed_x == 0) and (self.speed_y == 0):
                    self.waiting_duration += 1
        else:
            # No car in proximity, revert to original speed
            self.stop_if_red_lights(traffic_lights)


        for other_car in all_cars:
            if self != other_car and self.check_collision(other_car):
                self.crashed = True
                other_car.crashed = True



        self.move()
