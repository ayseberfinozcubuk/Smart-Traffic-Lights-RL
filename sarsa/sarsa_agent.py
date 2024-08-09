import numpy as np

class SARSAAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.99, epsilon=0.1):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.actions)
        else:
            q_values = [self.get_q_value(state, action) for action in self.actions]
            return np.argmax(q_values)

    def update(self, state, action, reward, next_state, next_action):
        current_q = self.get_q_value(state, action)
        next_q = self.get_q_value(next_state, next_action)
        new_q = current_q + self.alpha * (reward + self.gamma * next_q - current_q)
        self.q_table[(state, action)] = new_q
