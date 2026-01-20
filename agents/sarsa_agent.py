import numpy as np
import random
from .base_agent import BaseAgent

class SARSAAgent(BaseAgent):
    def __init__(self, actions, alpha=0.1, gamma=0.99, epsilon=0.1):
        super().__init__(actions)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}
        self.next_action = None

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def act(self, state):
        # If we already selected an action for this state during the previous learn step (SARSA logic), use it.
        # However, typically SARSA is on-policy:
        # 1. Take action A, observe R, S'
        # 2. Choose A' from S' using policy
        # 3. Update Q(S, A) using R, S', A'
        # 4. Take action A' (in the next step)
        if self.next_action is not None:
            action = self.next_action
            self.next_action = None
            return action

        # Fallback for first step or if logic breaks
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.actions)
        else:
            q_values = [self.get_q_value(state, action) for action in self.actions]
            return np.argmax(q_values)

    def learn(self, state, action, reward, next_state, done):
        # Choose next action A'
        if np.random.rand() < self.epsilon:
            next_action = np.random.choice(self.actions)
        else:
            q_values = [self.get_q_value(next_state, a) for a in self.actions]
            next_action = np.argmax(q_values)
        
        # Store for next act() call
        self.next_action = next_action

        current_q = self.get_q_value(state, action)
        next_q = self.get_q_value(next_state, next_action)
        new_q = current_q + self.alpha * (reward + self.gamma * next_q - current_q)
        self.q_table[(state, action)] = new_q
