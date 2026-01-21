# Smart Traffic Lights RL

This project simulates a traffic intersection controlled by Reinforcement Learning (RL) agents. The goal is to optimize traffic flow, minimize waiting times, and avoid collisions using **DQN (Deep Q-Network)**, **Q-Learning**, and **SARSA**.

## Technical Architecture

The system models the intersection as an RL environment where an agent learns to control traffic lights to maximize the cumulative reward.

### State Space

The state representation varies depending on the model:

*   **DQN (Deep Q-Network)**: A continuous vector of size **10** containing:
    *   **Traffic Lights (8 values)**: For each of the 2 lights, we track: `[x_position, y_position, state, time_since_last_change]`.
    *   **Road Queues (2 values)**: The number of cars waiting in the stopping area for each of the 2 main roads.

*   **Q-Learning & SARSA**: A discrete tuple comprising:
    *   **Queue Counts**: Tuple of car counts in stopping areas.
    *   **Light States**: Tuple of `(x, y, state, discretized_time)`. Time is discretized to seconds (capped at 60s) to keep the state space finite.

### Action Space

The agent controls the traffic lights by selecting one of **4** possible configurations at each step:
1.  **Horizontal Green / Vertical Red** (Safe flow for horizontal traffic)
2.  **Horizontal Red / Vertical Green** (Safe flow for vertical traffic)
3.  **All Green** (Unsafe - Agent must learn to avoid this)
4.  **All Red** (Safe but inefficient)

### Reward Function

The reward function guides the agent towards safe and efficient behavior:
*   **+10**: For every car that successfully exits the simulation.
*   **-0.05 / -0.1**: Penalty per tick for every car waiting (encourages flow).
*   **-10,000**: Penalty for a collision (strictly enforces safety).
*   **-500**: Continuous penalty **per tick** for choosing "All Green" (punishes the duration of unsafe states).

### Models & Hyperparameters

#### 1. Deep Q-Network (DQN)
Approximates Q-values using a Neural Network. Best for complex, continuous state spaces.
*   **Network Architecture**: 
    *   Input Layer (10 nodes)
    *   Hidden Layer 1 (64 nodes, ReLU)
    *   Hidden Layer 2 (64 nodes, ReLU)
    *   Output Layer (4 nodes, Linear)
*   **Hyperparameters**:
    *   `Gamma` (Discount Factor): 0.99
    *   `Learning Rate`: 0.001 (Adam Optimizer)
    *   `Epsilon Decay`: 0.99 (Min: 0.1)
    *   `Batch Size`: 64
    *   `Target Update`: Every 10 steps

#### 2. Q-Learning
A classic off-policy algorithm that maintains a Q-Table mapping `(State, Action) -> Value`.
*   **Hyperparameters**:
    *   `Alpha` (Learning Rate): 0.1
    *   `Gamma`: 0.9
    *   `Epsilon`: 0.1
*   **Logic**: Updates Q-values based on the maximum possible future reward (`max Q(s', a')`).

#### 3. SARSA
An on-policy algorithm (State-Action-Reward-State-Action).
*   **Hyperparameters**:
    *   `Alpha`: 0.1
    *   `Gamma`: 0.99
    *   `Epsilon`: 0.1
*   **Logic**: Updates Q-values based on the *actual* action taken by the policy in the next state (`Q(s', a')`), making it more conservative than Q-learning.

## Project Structure

*   **`agents/`**: RL implementations (`DQNAgent`, `QLearningAgent`, `SARSAAgent`).
*   **`env/`**: Environment logic (`environment.py`) handling state transitions and rewards.
*   **`simulation/`**: The core simulation engine (`traffic_sim.py`) managing the game loop.
*   **`display/`**: Visual assets and rendering (`Car`, `Road`, `TrafficLight`).
*   **`logs/`**: Training data storage.

## Requirements

*   Python 3.x
*   `pygame`
*   `numpy`
*   `torch`

```bash
pip install pygame numpy torch
```

## How to Run

Execute the `main.py` script from the root directory. This will launch a dashboard running **DQN**, **Q-Learning**, and **SARSA** simulations simultaneously for comparison.

```bash
python main.py
# or python3 main.py (depending on your system)
```
