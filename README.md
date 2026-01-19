# Smart Traffic Lights RL

This project simulates a traffic intersection controlled by Reinforcement Learning (RL) agents. The goal is to optimize traffic flow, minimize waiting times, and avoid collisions. it includes implementations using **DQN (Deep Q-Network)**, **Q-Learning**, and **SARSA**.

## Project Structure

The codebase is organized into a shared `common` package and algorithm-specific directories:

-   **`common/`**: Contains shared simulation components to eliminate code duplication.
    -   `environment.py`: The main reinforcement learning environment.
    -   `car.py`: Car logic, movement, and collision detection.
    -   `road.py`: Road rendering and logic.
    -   `traffic_light.py`: Traffic light state management and rendering.
    -   `car_spawner.py`: Logic for spawning cars at random intervals.
-   **`dqn/`**: Specific implementation for the Deep Q-Network agent (`dqn_agent.py` and `two_road_dqn.py`).
-   **`q/`**: Specific implementation for the Q-Learning agent (`q_learning_agent.py` and `two_road.py`).
-   **`sarsa/`**: Specific implementation for the SARSA agent (`sarsa_agent.py` and `two_road_sarsa.py`).

## Requirements

Ensure you have Python 3 installed along with the following dependencies:

```bash
pip install pygame numpy torch
```

## How to Run

**Crucial Note**: You must set `PYTHONPATH=.` when running the scripts so that Python can locate the `common` module.

Run the commands from the root directory of the project.

### 1. Deep Q-Network (DQN)
Uses a neural network to approximate Q-values. Best for complex state spaces.

```bash
PYTHONPATH=. python3 dqn/two_road_dqn.py
```

### 2. Q-Learning
A classic off-policy RL algorithm using a Q-table.

```bash
PYTHONPATH=. python3 q/two_road.py
```

### 3. SARSA
An on-policy RL algorithm (State-Action-Reward-State-Action).

```bash
PYTHONPATH=. python3 sarsa/two_road_sarsa.py
```

## Simulation Details

-   **Action Space**: The agent can switch traffic lights to different configurations (Red/Green pairs).
    -   *Warning*: The action space includes an "All Green" state. The agents must learn to avoid this state through training (negative reward for crashes).
-   **Rewards**:
    -   **+10** for every car that successfully exits the simulation.
    -   **-0.05 / -0.1** penalty per tick for cars waiting (to encourage flow).
    -   **-10,000** penalty for collisions (to enforce safety).
-   **Logs**:
    -   Training logs (`rewards.csv`, `collisions.csv`, `data.csv`) are saved in the respective algorithm directories (`dqn/`, `q/`, `sarsa/`).

## Controls

The simulation runs visually using PyGame.
-   Close the window to stop the simulation.
