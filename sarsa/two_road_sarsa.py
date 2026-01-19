import pygame
import sys
from common.car_spawner import CarSpawner
from common.road import Road
from common.traffic_light import TrafficLight, Light
from common.environment import Environment
from sarsa_agent import SARSAAgent
import os

if os.path.exists("sarsa/collisions.csv"):
    os.remove("sarsa/collisions.csv")
if os.path.exists("sarsa/max_wait_durations.csv"):
    os.remove("sarsa/max_wait_durations.csv")
if os.path.exists("sarsa/rewards.csv"):
    os.remove("sarsa/rewards.csv")

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

gray = (60, 60, 60)
light_gray = (211, 211, 211)
red = (255, 0, 0)
green = (100, 200, 70)

road_width = 50
spawn_interval = 100

horizontal_road = Road(0, HEIGHT // 2 - road_width, WIDTH, HEIGHT // 2 + road_width, gray, main_road=True)
horizontal_road_small = Road(WIDTH // 2 - 100, HEIGHT // 2 - road_width, WIDTH // 2 - road_width, HEIGHT // 2 + road_width, green, main_road=False)

vertical_road = Road(WIDTH // 2 - road_width, 0, WIDTH // 2 + road_width, HEIGHT, gray, main_road=True)
vertical_road_small = Road(WIDTH // 2 - road_width, HEIGHT // 2 - 100, WIDTH // 2 + road_width, HEIGHT // 2 - road_width, green, main_road=False)

car_spawner1 = CarSpawner((0, 0, HEIGHT // 2), red, (50, 30), spawn_interval, (1, 0))
car_spawner2 = CarSpawner((WIDTH // 2, WIDTH // 2, 0), red, (50, 30), spawn_interval, (0, 1))

traffic_light_horizontal = TrafficLight(WIDTH // 2 - 50, HEIGHT // 2, horizontal_road_small)
traffic_light_vertical = TrafficLight(WIDTH // 2, HEIGHT // 2 - 50, vertical_road_small)

traffic_lights = [traffic_light_horizontal, traffic_light_vertical]
roads = [horizontal_road, vertical_road, horizontal_road_small, vertical_road_small]
all_cars = []

env = Environment(log_dir="sarsa", crash_penalty=10000, stopping_penalty=0.1, state_encoding='tuple')
state = env.reset(all_cars, traffic_lights, roads)
hashable_state = env.get_hashable_state(state)

# Actions listesi, her trafik ışığı için olası durumları belirler.
actions = [
    (Light.GREEN, Light.RED),   # İlk ışık yeşil, ikinci ışık kırmızı
    (Light.RED, Light.GREEN),   # İlk ışık kırmızı, ikinci ışık yeşil
    (Light.GREEN, Light.GREEN), # Her iki ışık da yeşil
    (Light.RED, Light.RED)      # Her iki ışık da kırmızı
]

# SARSA ajanını başlat
agent = SARSAAgent(actions=range(len(actions)))

# İlk durumu seçin ve ilk aksiyonu belirleyin
action_index = agent.choose_action(hashable_state)
action = actions[action_index]

def draw_scene():
    screen.fill(light_gray)
    for road in filter(lambda road: road.main_road, roads):
        road.draw(screen)
    for traffic_light in traffic_lights:
        traffic_light.draw(screen)
    for car in all_cars:
        car.draw(screen)

clock = pygame.time.Clock()

while True:
    current_time = pygame.time.get_ticks()
    all_cars = list(filter(lambda car: car.x < WIDTH and car.y < HEIGHT and car.crashed == False and car.reached_end == False, all_cars))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    car_spawner1.spawn_car(current_time, all_cars)
    car_spawner2.spawn_car(current_time, all_cars)

    # Her adımda bir aksiyon seçilir ve uygulanır
    next_state, reward, done = env.step(action, all_cars, traffic_lights, roads)
    hashable_next_state = env.get_hashable_state(next_state)
    next_action_index = agent.choose_action(hashable_next_state)
    next_action = actions[next_action_index]

    # SARSA ajanını güncelle
    agent.update(hashable_state, action_index, reward, hashable_next_state, next_action_index)
    
    # Durumu ve aksiyonu güncelle
    hashable_state = hashable_next_state
    action_index = next_action_index
    action = next_action

    draw_scene()

    pygame.display.flip()
    
    clock.tick(60)
