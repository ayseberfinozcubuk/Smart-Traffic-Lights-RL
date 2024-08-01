import pygame
import sys
from car_spawner import CarSpawner
from road import Road
from traffic_light import TrafficLight, Light
from environment import Environment

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

gray = (60, 60, 60)
light_gray = (211, 211, 211)
red = (255, 0, 0)
green = (100, 200, 70)
abc = (150, 80, 50)

road_width = 50

horizontal_road = Road(0, HEIGHT // 2 - road_width, WIDTH, HEIGHT // 2 + road_width, gray, main_road=True)
horizontal_road_small = Road(WIDTH// 2 - 100, HEIGHT // 2 - road_width, WIDTH// 2 - road_width, HEIGHT // 2 + road_width, green, main_road=False)
vertical_road = Road(WIDTH// 2 - road_width, 0, WIDTH// 2 + road_width, HEIGHT, gray, main_road=True)
vertical_road_small = Road(WIDTH// 2 - road_width, HEIGHT // 2 - 100, WIDTH// 2 + road_width, HEIGHT // 2 - road_width, green, main_road=False)

car_spawner1 = CarSpawner((0, 0, HEIGHT // 2), red, (50, 30), 2000, (1, 0))
car_spawner2 = CarSpawner((WIDTH// 2, WIDTH// 2, 0), red, (50, 30), 2000, (0, 1))

traffic_light_horizontal = TrafficLight(WIDTH// 2 - 50, HEIGHT // 2, horizontal_road_small)
traffic_light_vertical = TrafficLight(WIDTH// 2, HEIGHT // 2 - 50, vertical_road_small)

traffic_lights = [traffic_light_horizontal, traffic_light_vertical]
roads = [horizontal_road, vertical_road, horizontal_road_small, vertical_road_small]
all_cars = []

env = Environment()
state = env.reset(all_cars, traffic_lights, roads)

def draw_scene():
    screen.fill(light_gray)
    for road in roads:
        road.draw(screen)
        road.draw_end_area(screen, abc)
    for traffic_light in traffic_lights:
        traffic_light.draw(screen)
    for car in all_cars:
        car.draw(screen)

clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

light_change_interval = 5000

while True:
    current_time = pygame.time.get_ticks()
    all_cars = list(filter(lambda car: car.x < WIDTH and car.y < HEIGHT and car.crashed == False and car.reached_end == False, all_cars))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    car_spawner1.spawn_car(current_time, all_cars)
    car_spawner2.spawn_car(current_time, all_cars)

    next_state, reward, done = env.step([Light.RED, Light.GREEN], all_cars, traffic_lights, roads)
    
    print(reward)

    state = next_state

    draw_scene()

    pygame.display.flip()
    
    clock.tick(60)
