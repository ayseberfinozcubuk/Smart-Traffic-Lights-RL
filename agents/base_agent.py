class BaseAgent:
    def __init__(self, actions):
        self.actions = actions

    def act(self, state):
        raise NotImplementedError

    def learn(self, state, action, reward, next_state, done):
        """
        Update the internal model/policy based on the experience.
        """
        raise NotImplementedError
