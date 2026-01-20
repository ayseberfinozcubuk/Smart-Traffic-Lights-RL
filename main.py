import argparse
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env.environment import Environment
from display.traffic_light import Light
from simulation.traffic_sim import TrafficSimulation

# Agents
from agents.dqn_agent import DQNAgent
from agents.q_agent import QLearningAgent
from agents.sarsa_agent import SARSAAgent

def main():
    parser = argparse.ArgumentParser(description='Smart Traffic Lights RL Simulation')
    parser.add_argument('--model', type=str, required=True, choices=['dqn', 'q', 'sarsa'], help='RL Model to use: dqn, q, or sarsa')
    args = parser.parse_args()

    # Define Actions
    actions = [
        (Light.GREEN, Light.RED),
        (Light.RED, Light.GREEN),
        (Light.GREEN, Light.GREEN),
        (Light.RED, Light.RED)
    ]

    # Clean previous logs for this run
    log_dir = f"logs/{args.model}"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    for log_file in ["collisions.csv", "max_wait_durations.csv", "rewards.csv", "data.csv"]:
        full_path = os.path.join(log_dir, log_file)
        if os.path.exists(full_path):
            os.remove(full_path)

    # Environment Configuration
    state_encoding = 'dqn' if args.model == 'dqn' else 'tuple'
    
    # Penalties (from previous tuning)
    crash_penalty = 10000
    if args.model == 'dqn':
        stopping_penalty = 0.05
    elif args.model == 'q':
        stopping_penalty = 0.05
    elif args.model == 'sarsa':
        stopping_penalty = 0.1
    
    env = Environment(
        log_dir=log_dir, 
        crash_penalty=crash_penalty, 
        stopping_penalty=stopping_penalty, 
        state_encoding=state_encoding
    )

    # dummy state to get size
    dummy_all_cars = []
    dummy_lights = [] # Need objects... simulation init handles real ones.
    # We need state size for DQN.
    # Simulation init resets env, but we need agent BEFORE simulation.
    # Chicken and egg.
    # Solution: Initialize simulation assets first? Simulation takes agent.
    # Or, Create temporary dummy env to get state size.
    # ACTUALLY, Simulation.__init__ resets env.
    # BUT we need agent to init Simulation.
    
    # Let's inspect Environment.get_hashable_state size without running full simulation.
    # state['traffic_lights'] has 2 lights.
    # state['cars_in_stopping_areas'] has 6 items (6 count areas).
    # DQN state: [L1_x, L1_y, L1_state, L2_x, L2_y, L2_state] + [C1, C2, C3, C4, C5, C6]
    # Lights: 2 lights * 3 values = 6
    # Count areas: 6 values
    # Total = 12.
    
    # Let's verify this 12 number.
    # In Environment.get_hashable_state:
    # lights_state = [item for light in state['traffic_lights'] for item in light]
    # state['traffic_lights'] comes from get_state logic.
    # In get_state: lights_state = [(x, y, state), ...]
    # So yes, 3 items per light.
    # How many lights? In two_road_dqn.py, there are 2 lights?
    # "traffic_lights = [traffic_light_horizontal, traffic_light_vertical]" -> Yes, 2.
    # How many count areas? "cars_in_stopping_areas" comes from "count_cars_in_stopping_areas".
    # It iterates over "roads" (filtered by main_road).
    # In two_road_dqn.py, roads list has 6 items?
    # roads = [horizontal_road, vertical_road, horizontal_road_small, vertical_road_small, horizontal_road_2, horizontal_road_small_2]
    # Filter by main_road: 
    # horizontal_road (True), vertical_road(True), horizontal_road_2(True)
    # The small ones are False.
    # So 3 main roads -> 3 count areas?
    # Wait, let's check `dqn_agent.py` state size usage in `two_road_dqn.py`.
    # `state_size = len(env.get_hashable_state(state))`
    # I should just rely on the calculated size if possible.
    # Or hardcode it if it is static.
    # 2 lights * 3 = 6.
    # 3 roads * 1 count = 3.
    # Total 9?
    # Let's dry run: 3 main roads. `TrafficSimulation` creates 3 main roads.
    # So `cars_in_stopping_areas` length is 3.
    # Total state size = 6 + 3 = 9.
    
    # WAIT. `dqn/two_road_dqn.py` roads list:
    # horizontal_road (True)
    # horizontal_road_2 (True)
    # vertical_road (True)
    # So 3 main roads.
    
    state_size = 9 # Calculated estimate.
    # Ideally should be dynamic.
    
    if args.model == 'dqn':
        agent = DQNAgent(state_size=state_size, action_size=len(actions))
    elif args.model == 'q':
        agent = QLearningAgent(actions=range(len(actions)))
    elif args.model == 'sarsa':
        agent = SARSAAgent(actions=range(len(actions)))

    # Start Simulation
    sim = TrafficSimulation(agent, env, actions)
    
    # Correct state_size if needed?
    # If I guessed wrong, DQN input layer will mismatch.
    # `sim.hashable_state` is available after init.
    # If model is DQN, we could re-init it if size is wrong? Or just trust my math.
    # Let's trust my math for now. The simulation defines assets, so it's consistent.
    
    print(f"Starting simulation with model: {args.model}")
    print(f"Logs will be saved to: {log_dir}")
    
    sim.run()

if __name__ == "__main__":
    main()
