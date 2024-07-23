# car_spawner.py

import random
from car import Car

all_cars = []

class CarSpawner:
    def __init__(self, spawn_area, car_color, car_size, spawn_interval, direction, width, height):
        self.spawn_area = spawn_area
        self.car_color = car_color
        self.car_size = car_size
        self.spawn_interval = spawn_interval
        self.direction = direction
        self.width = width
        self.height = height
        self.time_since_last_spawn = 0
        self.speed_reduction_distance = 100

    def spawn_car(self, current_time):
        if current_time - self.time_since_last_spawn >= self.spawn_interval:
            x = random.randint(self.spawn_area[0], self.spawn_area[1])
            y = self.spawn_area[2]
            speed_x = random.randint(1, Car.MAX_SPEED) * self.direction[0]
            speed_y = random.randint(1, Car.MAX_SPEED) * self.direction[1]
            car = Car(x, y, *self.car_size, self.car_color, speed_x, speed_y)
            all_cars.append(car)
            self.time_since_last_spawn = current_time

    def update(self):
        for car in all_cars:
            car.move()

        # Check for collisions
        for i, car in enumerate(all_cars):
            for other_car in all_cars[i + 1:]:
                if car.check_collision(other_car):
                    print(f"Collision detected between cars at ({car.x}, {car.y}) and ({other_car.x}, {other_car.y})")

        for car in all_cars:
            is_any_car_in_proximity = False
            for other_car in all_cars:
                if car != other_car and car.is_in_proximity(other_car, self.speed_reduction_distance):
                    car.speed_x = min(car.speed_x, 1)
                    car.speed_y = min(car.speed_y, 1)
                    is_any_car_in_proximity = True
            if not is_any_car_in_proximity:
                car.speed_x = car.original_speed_x
                car.speed_y = car.original_speed_y

        # Remove cars that move off the screen
        all_cars[:] = [car for car in all_cars if 0 <= car.x <= self.width and 0 <= car.y <= self.height]

    def draw(self, surface):
        for car in all_cars:
            car.draw(surface)

    
