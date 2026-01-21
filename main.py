import os
import sys
import pygame

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env.environment import Environment
from display.traffic_light import Light
from simulation.traffic_sim import TrafficSimulation
from display.dashboard import Dashboard

# Agents
from agents.dqn_agent import DQNAgent
from agents.q_agent import QLearningAgent
from agents.sarsa_agent import SARSAAgent

def main():
    # Configuration
    SIM_WIDTH = 400
    SIM_HEIGHT = 400
    DASHBOARD_HEIGHT = 250 # Increased dashboard height for 2 graphs or just labels
    TOTAL_WIDTH = SIM_WIDTH * 3
    TOTAL_HEIGHT = SIM_HEIGHT + DASHBOARD_HEIGHT
    FPS = 60

    # Initialize Pygame Main Window
    pygame.init()
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    pygame.display.set_caption("Multi-Model Traffic Light Simulation Check")
    clock = pygame.time.Clock()

    # Define Actions
    actions = [
        (Light.GREEN, Light.RED),
        (Light.RED, Light.GREEN),
        (Light.GREEN, Light.GREEN),
        (Light.RED, Light.RED)
    ]

    # Initialize Simulations for each Model
    models = ['dqn', 'q', 'sarsa']
    sims = []
    
    # Common Parameters
    # State Size: 2 lights * 4 + 2 roads * 1 = 10
    state_size_dqn = 10 
    
    for i, model_name in enumerate(models):
        log_dir = f"logs/{model_name}"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            

        for log_file in ["collisions.csv", "max_wait_durations.csv", "rewards.csv", "data.csv"]:
            full_path = os.path.join(log_dir, log_file)
            if os.path.exists(full_path):
                os.remove(full_path)

        # Environment
        state_encoding = 'dqn' if model_name == 'dqn' else 'tuple'
        if model_name == 'dqn':
            stopping_penalty = 0.05
        elif model_name == 'q':
            stopping_penalty = 0.05
        else: # sarsa
            stopping_penalty = 0.1
            
        env = Environment(
            log_dir=log_dir, 
            crash_penalty=10000, 
            stopping_penalty=stopping_penalty, 
            state_encoding=state_encoding
        )

        # Agent
        if model_name == 'dqn':
            agent = DQNAgent(state_size=state_size_dqn, action_size=len(actions))
        elif model_name == 'q':
            agent = QLearningAgent(actions=range(len(actions)))
        elif model_name == 'sarsa':
            agent = SARSAAgent(actions=range(len(actions)))

        # Simulation
        sim = TrafficSimulation(agent, env, actions, width=SIM_WIDTH, height=SIM_HEIGHT)
        sims.append(sim)

    # Dashboard
    dashboard = Dashboard(0, SIM_HEIGHT, TOTAL_WIDTH, DASHBOARD_HEIGHT, sims, ["DQN", "Q-Learning", "SARSA"])

    print("Starting Multi-Model Simulation...")
    print(f"Window Size: {TOTAL_WIDTH}x{TOTAL_HEIGHT}")

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        

        for sim in sims:
            sim.update(current_time)

        # Drawing
        screen.fill((0, 0, 0))


        for i, sim in enumerate(sims):
            # Create a subsurface or just draw to main screen with offset?


            subscreen = screen.subsurface(pygame.Rect(i * SIM_WIDTH, 0, SIM_WIDTH, SIM_HEIGHT))
            sim.draw(subscreen)
            

            pygame.draw.rect(screen, (0, 0, 0), (i * SIM_WIDTH, 0, SIM_WIDTH, SIM_HEIGHT), 2)

        # Draw Dashboard
        dashboard.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
