import random
from car import Car

class CarSpawner:
    def __init__(self, spawn_area, car_color, car_size, spawn_interval, direction):
        self.spawn_area = spawn_area
        self.car_color = car_color
        self.car_size = car_size
        self.spawn_interval = spawn_interval
        self.direction = direction
        self.time_since_last_spawn = 0

    def spawn_car(self, current_time, all_cars):
        if current_time - self.time_since_last_spawn >= self.spawn_interval:
            x = random.randint(self.spawn_area[0], self.spawn_area[1])
            y = self.spawn_area[2]
            speed_x = random.randint(Car.MIN_SPEED, Car.MAX_SPEED) * self.direction[0]
            speed_y = random.randint(Car.MIN_SPEED, Car.MAX_SPEED) * self.direction[1]
            car = Car(x, y, *self.car_size, self.car_color, speed_x, speed_y)
            all_cars.append(car)
            self.time_since_last_spawn = current_time
            self.spawn_interval = random.random() * 300 + 100
