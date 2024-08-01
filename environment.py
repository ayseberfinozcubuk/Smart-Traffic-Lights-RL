import pygame
import numpy as np
import csv

class Environment:
    def __init__(self):
        self.data = []
        self.state = None
        self.speed_reduction_distance = 100
        self.light_change_interval = 5000

    def reset(self, all_cars, traffic_lights, roads):
        self.data = []
        self.state = self.get_state(all_cars, traffic_lights, roads)
        return self.state

    def get_state(self, all_cars, traffic_lights, roads):
        cars_state = [(car.x, car.y, car.speed_x, car.speed_y, car.crashed) for car in all_cars]
        lights_state = [(light.location_x, light.location_y, light.current_light) for light in traffic_lights]
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
        for i, light in enumerate(traffic_lights):
            light.change_light(action[i])

    def calculate_reward(self, state):
        reward = 0
        reward += sum(state['cars_at_end_areas']) 
        reward -= sum(state['cars_in_stopping_areas']) 
        for car in state['cars']:
            if car[4]:
                reward -= 1
        return reward

    def is_done(self, state):
        for car in state['cars']:
            if car[4]:
                return True
        return False

    def count_cars_in_stopping_areas(self, all_cars, roads):
        counts = []
        for road in filter(lambda r: r.main_road, roads):
            count = road.count_cars(all_cars)
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
        self.save_data_to_csv('data.csv')

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
        cars_state = tuple(tuple(car) for car in state['cars'])
        lights_state = tuple(tuple(light) for light in state['traffic_lights'])
        cars_in_stopping_areas = tuple(state['cars_in_stopping_areas'])
        cars_at_end_areas = tuple(state['cars_at_end_areas'])
        return (cars_state, lights_state, cars_in_stopping_areas, cars_at_end_areas)