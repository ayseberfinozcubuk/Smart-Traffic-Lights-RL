import datetime
import pygame
import numpy as np
import csv
import os

class Environment:

    dif_penalty_for_wait = True
    episode = 0
    episode_reward = 0
    


    def __init__(self, log_dir='.', crash_penalty=1000, stopping_penalty=0.05, state_encoding='tuple', min_switch_time=5000):
        self.data = []
        self.state = None
        self.speed_reduction_distance = 100
        self.light_change_interval = 5000
        self.min_switch_time = min_switch_time
        self.log_dir = log_dir
        self.crash_penalty = crash_penalty
        self.stopping_penalty = stopping_penalty
        self.state_encoding = state_encoding

    def reset(self, all_cars, traffic_lights, roads):
        self.data = []
        self.state = self.get_state(all_cars, traffic_lights, roads)
        return self.state

    def get_state(self, all_cars, traffic_lights, roads):
        cars_state = [(car.x, car.y, car.speed_x, car.speed_y, car.crashed) for car in all_cars]
        
        current_time = pygame.time.get_ticks()
        lights_state = []
        for light in traffic_lights:
            state_val = (light.current_light.value if hasattr(light.current_light, 'value') else light.current_light)
            time_since_change = (current_time - light.last_light_change_time) / 1000.0 # In seconds
            lights_state.append((light.location_x, light.location_y, state_val, time_since_change))
            
        cars_in_stopping_areas = self.count_cars_in_stopping_areas(all_cars, roads)
        cars_at_end_areas = self.count_cars_at_end_areas(all_cars, roads)

        return {
            'cars': cars_state, 
            'traffic_lights': lights_state, 
            'cars_in_stopping_areas': cars_in_stopping_areas,
            'cars_at_end_areas': cars_at_end_areas
        }

    def step(self, action, all_cars, traffic_lights, roads):
        self.apply_action(action, traffic_lights)

        for car in all_cars:

            car.update(all_cars, traffic_lights, self.speed_reduction_distance)

        new_state = self.get_state(all_cars, traffic_lights, roads)
        reward = self.calculate_reward(new_state)
        done = self.is_done(new_state)

        self.record_data(new_state)

        return new_state, reward, done

    def apply_action(self, action, traffic_lights):
        current_time = pygame.time.get_ticks()
        for i, light in enumerate(traffic_lights):

            if light.current_light != action[i]:
                if current_time - light.last_light_change_time >= self.min_switch_time:
                    light.change_light(action[i])
                    light.last_light_change_time = current_time

    def calculate_reward(self, state):
        reward = 0
        reward += sum(state['cars_at_end_areas']) * 10
        reward -= sum(state['cars_in_stopping_areas']) * self.stopping_penalty
        
        # Penalize crashes
        for car in state['cars']:
            if car[4]:  # If crashed
                reward -= self.crash_penalty

        
        light_states = [light[2] for light in state['traffic_lights']]
        
        green_lights = light_states.count(2) 
        

        
        # This penalty is applied EVERY TICK (approx 60 times/sec) while the state is unsafe.
        if green_lights >= 2:
            reward -= 500 
        
        Environment.episode += 1
        Environment.episode_reward += reward
        if (Environment.episode == 50):
            with open(os.path.join(self.log_dir, 'rewards.csv'), 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'reward']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if csvfile.tell() == 0:  # Write header if file is empty
                    writer.writeheader()

                writer.writerow({
                    'timestamp': datetime.datetime.now(),
                    'reward': Environment.episode_reward
                })
            Environment.episode = 0
            Environment.episode_reward = 0
        return reward

    def is_done(self, state):
        for car in state['cars']:
            if car[4]:
                return True
        return False

    def count_cars_in_stopping_areas(self, all_cars, roads):
        counts = []
        for road in filter(lambda r: r.main_road, roads):
            count = road.count_cars(all_cars, calculate_waiting_durations=Environment.dif_penalty_for_wait)
            counts.append(count)
        return counts

    def count_cars_at_end_areas(self, all_cars, roads):
        counts = []
        for road in filter(lambda r: r.main_road, roads):
            count = road.count_cars_at_end(all_cars)
            counts.append(count)
        return counts

    def record_data(self, state):
        self.data.append(state)
        self.save_data_to_csv(os.path.join(self.log_dir, 'data.csv'))

    def save_data_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'traffic_light_index', 
                'traffic_light_x', 
                'traffic_light_y', 
                'traffic_light_state',
                'cars_in_stopping_areas',
                'cars_at_end_areas'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for state in self.data:
                for i, light in enumerate(state['traffic_lights']):
                    writer.writerow({
                        'traffic_light_index': i,
                        'traffic_light_x': light[0],
                        'traffic_light_y': light[1],
                        'traffic_light_state': light[2],
                        'cars_in_stopping_areas': state['cars_in_stopping_areas'][i],
                        'cars_at_end_areas': state['cars_at_end_areas'][i]
                    })

    def clear_data(self):
        self.data = []
      
    def get_hashable_state(self, state):
        cars_in_stopping_areas = state['cars_in_stopping_areas']
        
        if self.state_encoding == 'dqn':

            lights_state = [item for light in state['traffic_lights'] for item in light]
            return lights_state + cars_in_stopping_areas
        else:

            lights_state = []
            for light in state['traffic_lights']:
                # light is (x, y, s, time)
                x, y, s, t = light
                t_discretized = min(int(t), 60)
                lights_state.append((x, y, s, t_discretized))
                
            lights_state = tuple(lights_state)
            cars_in_stopping_areas = tuple(cars_in_stopping_areas)
            
            return (cars_in_stopping_areas, lights_state)
