import pygame
import sys
from car_spawner import CarSpawner
from road import Road
from traffic_light import TrafficLight, Light
from environment import Environment
from q_learning_agent import QLearningAgent
import os

if os.path.exists("q/collisions.csv"):
    os.remove("q/collisions.csv")
if os.path.exists("q/max_wait_durations.csv"):
    os.remove("q/max_wait_durations.csv")
if os.path.exists("q/rewards.csv"):
    os.remove("q/rewards.csv")

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

gray = (60, 60, 60)
light_gray = (211, 211, 211)
red = (255, 0, 0)
green = (100, 200, 70)
abc = (150, 80, 50)

road_width = 50
spawn_interval = 100

horizontal_road = Road(0, HEIGHT // 2 - road_width, WIDTH, HEIGHT // 2 + road_width, gray, main_road=True)
horizontal_road_small = Road(WIDTH// 2 - 100, HEIGHT // 2 - road_width, WIDTH// 2 - road_width, HEIGHT // 2 + road_width, green, main_road=False)

horizontal_road_2 = Road(0, HEIGHT // 3 - road_width, WIDTH, HEIGHT // 3 + road_width, gray, main_road=True)
horizontal_road_small_2 = Road(WIDTH// 3 - 100, HEIGHT // 3 - road_width, WIDTH// 2 - road_width, HEIGHT // 2 + road_width, green, main_road=False)

vertical_road = Road(WIDTH// 2 - road_width, 0, WIDTH// 2 + road_width, HEIGHT, gray, main_road=True)
vertical_road_small = Road(WIDTH// 2 - road_width, HEIGHT // 2 - 100, WIDTH// 2 + road_width, HEIGHT // 2 - road_width, green, main_road=False)

car_spawner1 = CarSpawner((0, 0, HEIGHT // 2), red, (50, 30), spawn_interval, (1, 0))
car_spawner2 = CarSpawner((WIDTH// 2, WIDTH// 2, 0), red, (50, 30), spawn_interval, (0, 1))
# car_spawner3 = CarSpawner((0, 0, HEIGHT // 3), red, (50, 30), 200, (1, 0))

traffic_light_horizontal = TrafficLight(WIDTH// 2 - 50, HEIGHT // 2, horizontal_road_small)
traffic_light_horizontal_2 = TrafficLight(WIDTH// 2 - 50, HEIGHT // 3, horizontal_road_small_2)
traffic_light_vertical = TrafficLight(WIDTH// 2, HEIGHT // 2 - 50, vertical_road_small)

traffic_lights = [traffic_light_horizontal, traffic_light_vertical]
roads = [horizontal_road, vertical_road, horizontal_road_small, vertical_road_small, horizontal_road_2, horizontal_road_small_2]
all_cars = []

env = Environment()
state = env.reset(all_cars, traffic_lights, roads)
hashable_state = env.get_hashable_state(state)

# Define possible actions (index corresponding to each light's state)
actions = [(Light.GREEN, Light.RED), (Light.RED, Light.GREEN), (Light.GREEN, Light.GREEN), (Light.RED, Light.RED)]

# Initialize the Q-learning agent
agent = QLearningAgent(actions=range(len(actions)))

def draw_scene():
    screen.fill(light_gray)
    for road in filter(lambda road: road.main_road, roads):
        road.draw(screen)
    for traffic_light in traffic_lights:
        traffic_light.draw(screen)
    for car in all_cars:
        car.draw(screen)

clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

# Initialize the timer for action selection
last_action_time = start_time
action_interval = 200  # Interval for action selection in milliseconds (0.1 seconds)
action_index = 0 
while True:
    current_time = pygame.time.get_ticks()
    all_cars = list(filter(lambda car: car.x < WIDTH and car.y < HEIGHT and car.crashed == False and car.reached_end == False, all_cars))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    car_spawner1.spawn_car(current_time, all_cars)
    car_spawner2.spawn_car(current_time, all_cars)

    # Determine if it's time to choose a new action
    if current_time - last_action_time >= action_interval:
        action_index = agent.choose_action(hashable_state)
        action = actions[action_index]
        last_action_time = current_time
    else:
        action = actions[action_index]

    next_state, reward, done = env.step(action, all_cars, traffic_lights, roads)
    hashable_next_state = env.get_hashable_state(next_state)

    agent.update(hashable_state, action_index, reward, hashable_next_state)
    hashable_state = hashable_next_state

    draw_scene()

    pygame.display.flip()
    
    clock.tick(60)