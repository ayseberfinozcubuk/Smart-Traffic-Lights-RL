import pygame
import sys
from display.car_spawner import CarSpawner
from display.road import Road, Direction
from display.traffic_light import TrafficLight, Light
from display.car import Car

class TrafficSimulation:
    def __init__(self, agent, env, actions, width=400, height=600):
        self.agent = agent
        self.env = env
        self.actions_map = actions
        self.width = width
        self.height = height
        

        self.roads = []
        self.traffic_lights = []
        self.all_cars = []
        self.car_spawners = []
        
        self.gray = (60, 60, 60)
        self.light_gray = (211, 211, 211)
        self.red = (255, 0, 0)
        self.green = (100, 200, 70)

        self._init_assets()
        

        self.state = self.env.reset(self.all_cars, self.traffic_lights, self.roads)
        self.hashable_state = self.env.get_hashable_state(self.state)

        # Simulation State
        self.last_action_time = 0
        self.action_interval = 200
        self.action_index = 0
        

        self.collision_count = 0
        # waiting_time_history stores cumulative average waiting time per frame
        self.waiting_time_history = []
        # collision_history stores cumulative collision count per frame
        self.collision_history = []
        
        # Cumulative/Global stats tracking
        self.completed_cars_wait_sum = 0
        self.completed_cars_count = 0

    def _init_assets(self):
        road_width = 25
        spawn_interval = 100
        
        # Roads

        horizontal_road = Road(0, self.height // 2 - road_width, self.width, self.height // 2 + road_width, self.gray, main_road=True)
        horizontal_road_small = Road(self.width // 2 - 100, self.height // 2 - road_width, self.width // 2 - road_width, self.height // 2 + road_width, self.green, main_road=False)

        # Removed the upper horizontal road (horizontal_road_2) as requested


        vertical_road = Road(self.width // 2 - road_width, 0, self.width // 2 + road_width, self.height, self.gray, main_road=True)
        vertical_road_small = Road(self.width // 2 - road_width, self.height // 2 - 100, self.width // 2 + road_width, self.height // 2 - road_width, self.green, main_road=False)
        
        self.roads = [horizontal_road, vertical_road, horizontal_road_small, vertical_road_small]

        # Spawners
        # Car Size: (40, 20). 20 fits into road_width=25.
        car_spawner1 = CarSpawner((0, 0, self.height // 2), self.red, (40, 20), spawn_interval, (1, 0))
        car_spawner2 = CarSpawner((self.width // 2, self.width // 2, 0), self.red, (40, 20), spawn_interval, (0, 1))
        self.car_spawners = [car_spawner1, car_spawner2]


        traffic_light_horizontal = TrafficLight(self.width // 2 - road_width, self.height // 2, horizontal_road_small)
        traffic_light_vertical = TrafficLight(self.width // 2, self.height // 2 - road_width, vertical_road_small)
        self.traffic_lights = [traffic_light_horizontal, traffic_light_vertical]
        self.all_cars = []

    def draw(self, surface):
        surface.fill(self.light_gray)
        for road in filter(lambda road: road.main_road, self.roads):
            road.draw(surface)
        for traffic_light in self.traffic_lights:
            traffic_light.draw(surface)
        for car in self.all_cars:
            car.draw(surface)

    def update(self, current_time):
        # Filter Cars (Remove finished/crashed) and update cumulative stats
        active_cars = []
        for car in self.all_cars:
            if car.x < self.width and car.y < self.height and not car.crashed and not car.reached_end:
                active_cars.append(car)
            else:
                # Car removed (crashed or reached end or out of bounds)
                # Count its waiting time towards history
                self.completed_cars_wait_sum += car.waiting_duration
                self.completed_cars_count += 1
        
        self.all_cars = active_cars


        for spawner in self.car_spawners:
            spawner.spawn_car(current_time, self.all_cars)

        # Agent Action
        if current_time - self.last_action_time >= self.action_interval:
            self.action_index = self.agent.act(self.hashable_state)
            self.last_action_time = current_time
        

        action = self.actions_map[self.action_index]

        # Environment Step
        next_state, reward, done = self.env.step(action, self.all_cars, self.traffic_lights, self.roads)
        hashable_next_state = self.env.get_hashable_state(next_state)


        self.agent.learn(self.hashable_state, self.action_index, reward, hashable_next_state, done)
        
        self.hashable_state = hashable_next_state

        # Update Statistics
        # Count new crashes (cars that are crashed but not yet removed)
        new_crashes = len([car for car in self.all_cars if car.crashed])
        self.collision_count += new_crashes 
        # Note: Crashed cars will be removed at the beginning of the NEXT update call.

        # Calculate Cumulative Average Waiting Time
        current_active_wait_sum = sum(car.waiting_duration for car in self.all_cars)
        total_wait_sum = self.completed_cars_wait_sum + current_active_wait_sum
        total_cars_count = self.completed_cars_count + len(self.all_cars)
        
        if total_cars_count > 0:
            avg_wait = total_wait_sum / total_cars_count
        else:
            avg_wait = 0
            
        self.waiting_time_history.append(avg_wait)
            
        # Collision History
        self.collision_history.append(self.collision_count)
    
        # No history truncation (sliding window) as requested
