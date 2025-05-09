import unittest
from gui.editor import ActionEditor

class TestActionEditor(unittest.TestCase):
    def setUp(self):
        self.editor = ActionEditor()
        self.sample_actions = [
            {'type': 'mouse', 'event': 'down'},
            {'type': 'mouse', 'event': 'up'},
            {'type': 'keyboard', 'event': 'down'},
        ]
        self.editor.set_actions(self.sample_actions)

    def test_set_and_get_actions(self):
        actions = self.editor.get_actions()
        self.assertEqual(actions, self.sample_actions)

    def test_delete_action(self):
        self.editor.delete_action(1)
        actions = self.editor.get_actions()
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[1]['type'], 'keyboard')

    def test_move_action_up(self):
        self.editor.move_action_up(2)
        actions = self.editor.get_actions()
        self.assertEqual(actions[1]['type'], 'keyboard')
        self.assertEqual(actions[2]['type'], 'mouse')

    def test_move_action_down(self):
        self.editor.move_action_down(0)
        actions = self.editor.get_actions()
        self.assertEqual(actions[0]['type'], 'mouse')
        self.assertEqual(actions[1]['type'], 'mouse')

if __name__ == '__main__':
    unittest.main() 