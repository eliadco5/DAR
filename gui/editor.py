# Action list editor (delete, reorder)

class ActionEditor:
    def __init__(self):
        self.actions = []

    def set_actions(self, actions):
        self.actions = list(actions)

    def get_actions(self):
        return self.actions.copy()

    def delete_action(self, index):
        if 0 <= index < len(self.actions):
            del self.actions[index]

    def move_action_up(self, index):
        if 1 <= index < len(self.actions):
            self.actions[index - 1], self.actions[index] = self.actions[index], self.actions[index - 1]

    def move_action_down(self, index):
        if 0 <= index < len(self.actions) - 1:
            self.actions[index + 1], self.actions[index] = self.actions[index], self.actions[index + 1] 