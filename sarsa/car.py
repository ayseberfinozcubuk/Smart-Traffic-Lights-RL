import pygame
from traffic_light import Light
import datetime
import csv

class Car:
    MAX_SPEED = 25
    MIN_SPEED = 25
    collision_counter = 0
    max_wait_duration = -1

    # Initialize collision counter

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
        self.crashed = False
        self.reached_end = False
        self.waiting_duration = 0

        
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

        # Render collision counter
        font = pygame.font.Font(None, 36)
        text_collisions = font.render(f'Collisions: {Car.collision_counter}', True, (255, 255, 255))
        surface.blit(text_collisions, (10, 10))

        # Render max wait duration
        # text_max_wait = font.render(f'Max Wait Duration: {Car.max_wait_duration}', True, (255, 255, 255))
        # surface.blit(text_max_wait, (10, 50))

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def check_collision(self, other_car):
        # Simple bounding box collision detection
        return (self.x < other_car.x + other_car.width and
                self.x + self.width > other_car.x and
                self.y < other_car.y + other_car.height and
                self.y + self.height > other_car.y)
    
    def check_spawn_point_collision(self, x, y, width, height):
        # Simple bounding box collision detection
        return (x < self.x + self.width and
                x + width > self.x and
                y < self.y + self.height and
                y + height > self.y)

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
        for other_car in all_cars:
            if self != other_car and self.is_in_proximity(other_car, distance) and other_car.direction == self.direction:
                return other_car
        return None

    def stop_if_red_lights(self, traffic_lights):
        for traffic_light in traffic_lights:
            if traffic_light.current_light == Light.RED:
                if traffic_light.road.is_inside(self.x, self.y):
                    self.speed_x = 0
                    self.speed_y = 0
                    self.waiting_duration += 1
                    return  # Stop checking other lights if one is red and the car is affected
        self.speed_x = self.original_speed_x
        self.speed_y = self.original_speed_y
        self.waiting_duration = 0

    
    def update(self, all_cars, traffic_lights, speed_reduction_distance):

        # Check for traffic lights
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

        # Check for collisions with other cars
        for other_car in all_cars:
            if self != other_car and self.check_collision(other_car):
                self.crashed = True
                other_car.crashed = True
                Car.collision_counter += 1
                Car.save_collision(datetime.datetime.now(), self.x, self.y, other_car.x, other_car.y)
                print(f"Collision detected between cars at ({self.x}, {self.y}) and ({other_car.x}, {other_car.y})")
        Car.save_max_wait_duration(datetime.datetime.now(), all_cars)

        # Move the car
        self.move()

    @staticmethod
    def save_collision(timestamp, car1_x, car1_y, car2_x, car2_y):
        with open('sarsa/collisions.csv', 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'car1_x', 'car1_y', 'car2_x', 'car2_y']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if csvfile.tell() == 0:  # Write header if file is empty
                writer.writeheader()

            writer.writerow({
                'timestamp': timestamp,
                'car1_x': car1_x,
                'car1_y': car1_y,
                'car2_x': car2_x,
                'car2_y': car2_y
            })

    @staticmethod
    def save_max_wait_duration(timestamp, all_cars):
        max_duration = 0
        for car in all_cars:
            if (max_duration < car.waiting_duration):
                max_duration = car.waiting_duration

        if (Car.max_wait_duration != max_duration):
            Car.max_wait_duration = max_duration

            with open('sarsa/max_wait_durations.csv', 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'max_waiting_duration']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if csvfile.tell() == 0:  # Write header if file is empty
                    writer.writeheader()

                writer.writerow({
                    'timestamp': timestamp,
                    'max_waiting_duration': max_duration
                })