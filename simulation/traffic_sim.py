import pygame
import sys
from display.car_spawner import CarSpawner
from display.road import Road, Direction
from display.traffic_light import TrafficLight, Light
from display.car import Car

class TrafficSimulation:
    def __init__(self, agent, env, actions, width=1200, height=800, fps=60):
        self.agent = agent
        self.env = env
        self.actions_map = actions
        self.width = width
        self.height = height
        self.fps = fps
        
        self.screen = None
        self.clock = None
        
        # Simulation Assets
        self.roads = []
        self.traffic_lights = []
        self.all_cars = []
        self.car_spawners = []
        
        self.gray = (60, 60, 60)
        self.light_gray = (211, 211, 211)
        self.red = (255, 0, 0)
        self.green = (100, 200, 70)

        self._init_pygame()
        self._init_assets()
        
        # Reset Env
        self.state = self.env.reset(self.all_cars, self.traffic_lights, self.roads)
        self.hashable_state = self.env.get_hashable_state(self.state)

    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

    def _init_assets(self):
        road_width = 50
        spawn_interval = 100
        
        # Roads
        horizontal_road = Road(0, self.height // 2 - road_width, self.width, self.height // 2 + road_width, self.gray, main_road=True)
        horizontal_road_small = Road(self.width // 2 - 100, self.height // 2 - road_width, self.width // 2 - road_width, self.height // 2 + road_width, self.green, main_road=False)

        horizontal_road_2 = Road(0, self.height // 3 - road_width, self.width, self.height // 3 + road_width, self.gray, main_road=True)
        horizontal_road_small_2 = Road(self.width // 3 - 100, self.height // 3 - road_width, self.width // 2 - road_width, self.height // 2 + road_width, self.green, main_road=False)

        vertical_road = Road(self.width // 2 - road_width, 0, self.width // 2 + road_width, self.height, self.gray, main_road=True)
        vertical_road_small = Road(self.width // 2 - road_width, self.height // 2 - 100, self.width // 2 + road_width, self.height // 2 - road_width, self.green, main_road=False)
        
        self.roads = [horizontal_road, vertical_road, horizontal_road_small, vertical_road_small, horizontal_road_2, horizontal_road_small_2]

        # Spawners
        car_spawner1 = CarSpawner((0, 0, self.height // 2), self.red, (50, 30), spawn_interval, (1, 0))
        car_spawner2 = CarSpawner((self.width // 2, self.width // 2, 0), self.red, (50, 30), spawn_interval, (0, 1))
        self.car_spawners = [car_spawner1, car_spawner2]

        # Traffic Lights
        traffic_light_horizontal = TrafficLight(self.width // 2 - 50, self.height // 2, horizontal_road_small)
        traffic_light_vertical = TrafficLight(self.width // 2, self.height // 2 - 50, vertical_road_small)
        # Note: Previous dqn script had traffic_light_horizontal_2 but didn't put it in the list [traffic_lights] for some reason in one version?
        # Let's check dqn script again. It has 2 lights in the list.
        # "traffic_lights = [traffic_light_horizontal, traffic_light_vertical]"
        # But it defines traffic_light_horizontal_2.
        # Wait, the roads list has horizontal_road_2.
        # If I look at the old code:
        # traffic_light_horizontal_2 = TrafficLight(WIDTH// 2 - 50, HEIGHT // 3, horizontal_road_small_2)
        # traffic_lights = [traffic_light_horizontal, traffic_light_vertical]
        # It seems the second horizontal light was defined but NOT used in the logic?
        # That sounds like a bug or incomplete feature in the original code. 
        # But for now I should replicate existing behavior strictly or fix it if obvious.
        # User said "inheritance and code traceability should be a lot better".
        # I'll stick to what was running.
        
        self.traffic_lights = [traffic_light_horizontal, traffic_light_vertical]
        self.all_cars = []

    def draw(self):
        self.screen.fill(self.light_gray)
        for road in filter(lambda road: road.main_road, self.roads):
            road.draw(self.screen)
        for traffic_light in self.traffic_lights:
            traffic_light.draw(self.screen)
        for car in self.all_cars:
            car.draw(self.screen)
        pygame.display.flip()

    def run(self):
        last_action_time = pygame.time.get_ticks()
        action_interval = 200
        action_index = 0
        
        while True:
            current_time = pygame.time.get_ticks()
            self.all_cars = list(filter(lambda car: car.x < self.width and car.y < self.height and car.crashed == False and car.reached_end == False, self.all_cars))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Spawn Cars
            for spawner in self.car_spawners:
                spawner.spawn_car(current_time, self.all_cars)

            # Agent Action
            if current_time - last_action_time >= action_interval:
                action_index = self.agent.act(self.hashable_state)
                last_action_time = current_time
            
            # Map index to action tuple
            action = self.actions_map[action_index]

            # Environment Step
            next_state, reward, done = self.env.step(action, self.all_cars, self.traffic_lights, self.roads)
            hashable_next_state = self.env.get_hashable_state(next_state)

            # Agent Learn
            self.agent.learn(self.hashable_state, action_index, reward, hashable_next_state, done)
            
            self.hashable_state = hashable_next_state
            
            self.draw()
            self.clock.tick(self.fps)
