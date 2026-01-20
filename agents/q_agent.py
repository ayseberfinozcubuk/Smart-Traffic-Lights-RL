import numpy as np
import random
from .base_agent import BaseAgent

class QLearningAgent(BaseAgent):
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        super().__init__(actions)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}

    def get_q_value(self, state, action):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.actions))
        return self.q_table[state][action]

    def act(self, state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.actions))

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(range(len(self.actions)))  # Exploration
        else:
            return np.argmax(self.q_table[state])  # Exploitation

    def learn(self, state, action, reward, next_state, done):
        best_next_action = np.argmax(self.q_table.get(next_state, np.zeros(len(self.actions))))
        td_target = reward + self.gamma * self.get_q_value(next_state, best_next_action)
        td_error = td_target - self.get_q_value(state, action)
        self.q_table[state][action] += self.alpha * td_error
