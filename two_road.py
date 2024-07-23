import pygame
import sys
from car_spawner import CarSpawner
from road import Road
from traffic_light import TrafficLight, Light

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

gray = (60, 60, 60)
light_gray = (211, 211, 211)
red = (255, 0, 0)
green = (100, 200, 70)

road_width = 50

vertical_road = Road(0, height // 2 - road_width, width, height // 2 + road_width, gray)
vertical_road_small = Road(width // 2 - 100, height // 2 - road_width, width // 2 - road_width, height // 2 + road_width, green)
horizontal_road = Road(width // 2 - road_width, 0, width // 2 + road_width, height, gray)
top_left_grass = Road(0, 0, width // 2 - road_width, height // 2 - road_width, green)
top_right_grass = Road(width // 2 + road_width, 0, width, height // 2 - road_width, green)
bottom_left_grass = Road(0, height // 2 + road_width, width // 2 - road_width, height, green)
bottom_right_grass = Road(width // 2 + road_width, height // 2 + road_width, width, height, green)

car_spawner1 = CarSpawner((0, 0, height // 2), red, (50, 30), 2000, (1, 0), speed_reduction_distance=100)
car_spawner2 = CarSpawner((width // 2, width // 2, 0), red, (50, 30), 2000, (0, 1), speed_reduction_distance=100)

traffic_light = TrafficLight(width // 2 - 50, height // 2, vertical_road_small)

traffic_lights = [traffic_light]
all_cars = []

# Function to draw the roads and cars
def draw_scene():
    screen.fill(light_gray)
    vertical_road.draw(screen)
    horizontal_road.draw(screen)
    vertical_road_small.draw(screen)
    top_left_grass.draw(screen)
    top_right_grass.draw(screen)
    bottom_left_grass.draw(screen)
    bottom_right_grass.draw(screen)
    traffic_light.draw(screen)
    for car in all_cars:
        car.draw(screen)

# Main game loop
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

# Time tracking for light change
light_change_interval = 5000  # 5000 ms = 5 seconds
last_light_change_time = pygame.time.get_ticks()

while True:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Update car spawners
    car_spawner1.spawn_car(current_time, all_cars)
    car_spawner2.spawn_car(current_time, all_cars)

    for car in all_cars:
        car.update(all_cars, traffic_lights, car_spawner1.speed_reduction_distance)
    
    if current_time - last_light_change_time >= light_change_interval:
        # Change the light state
        next_light = {
            Light.RED: Light.GREEN,
            Light.GREEN: Light.RED,
        }.get(traffic_light.current_light, Light.RED)
        traffic_light.change_light(next_light)
        last_light_change_time = current_time
    
    draw_scene()
    
    pygame.display.flip()
    
    clock.tick(60)
