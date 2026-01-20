# Smart Traffic Lights RL

This project simulates a traffic intersection controlled by Reinforcement Learning (RL) agents. The goal is to optimize traffic flow, minimize waiting times, and avoid collisions. it includes implementations using **DQN (Deep Q-Network)**, **Q-Learning**, and **SARSA**.

## Project Structure

The codebase is organized into modular components:

-   **`agents/`**: Contains RL agent implementations (`BaseAgent`, `dqn_agent`, `q_agent`, `sarsa_agent`).
-   **`simulation/`**: Contains the generic `TrafficSimulation` engine.
-   **`env/`**: Contains the RL environment logic.
-   **`display/`**: Contains visual assets (`Car`, `Road`, `TrafficLight`, `CarSpawner`).
-   **`main.py`**: The single entry point for running all simulations.
-   **`logs/`**: Directory where training data (`rewards.csv`, `collisions.csv`) is saved.

## Requirements

Ensure you have Python 3 installed along with the following dependencies:

```bash
pip install pygame numpy torch
```

## How to Run

Run the simulation from the root directory using `main.py`. You must specify the model you wish to use.

### 1. Deep Q-Network (DQN)
Uses a neural network to approximate Q-values. Best for complex state spaces.

```bash
python3 main.py --model dqn
```

### 2. Q-Learning
A classic off-policy RL algorithm using a Q-table.

```bash
python3 main.py --model q
```

### 3. SARSA
An on-policy RL algorithm (State-Action-Reward-State-Action).

```bash
python3 main.py --model sarsa
```

## Simulation Details

-   **Action Space**: The agent can switch traffic lights to different configurations (Red/Green pairs).
    -   *Warning*: The action space includes an "All Green" state. The agents must learn to avoid this state through training (negative reward for crashes).
-   **Rewards**:
    -   **+10** for every car that successfully exits the simulation.
    -   **-0.05 / -0.1** penalty per tick for cars waiting (to encourage flow).
    -   **-10,000** penalty for collisions (to enforce safety).
-   **Logs**:
    -   Training logs are automatically saved in `logs/<model_name>/`.

## Controls

The simulation runs visually using PyGame.
-   Close the window to stop the simulation.
