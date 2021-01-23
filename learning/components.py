from numpy.random import random
from random import choices


class ValueFunction:

    def __init__(self):
        self._value_function = 0.

    @property
    def value_function(self):
        return self._value_function

    @value_function.setter
    def value_function(self, value):
        self._value_function = value


class State(ValueFunction):

    def __init__(self, is_terminal=False):
        super().__init__()
        self.is_terminal = is_terminal
        self._actions = ActionsList()  # ActionsList
        self._state = NotImplemented

    def set_actions(self, actions):
        if not isinstance(actions, (list, tuple, Action)):
            raise TypeError(f"'actions' must be one of the types `list()`, `tuple()` or `Action()`: "
                            f"{type(actions)} has been given.")

        if isinstance(actions, Action):
            actions = [actions]

        for action in actions:
            self._actions.append(action)
            # action.populate_prev(self)

    @property
    def id(self):
        return self._state

    @property
    def actions(self):
        return self._actions


class Action(ValueFunction):

    def __init__(self, from_state=None, probability=None):
        super().__init__()
        self._action = NotImplemented
        self._from_state = from_state
        self._probability = probability
        self._to_states = StatesList()   # []

    def __call__(self, use_weights=False):
        if use_weights:
            return choices(self.to_states, self.to_states.weights)[0]
        return choices(self.to_states)[0]

    # def populate_prev(self, state):
    #     """Assign previous state to self._from_state"""
    #     self._from_state = state

    def populate_next(self, policy):
        """Assign next states to self._to_states"""
        # Policy as input, then run policy.next_state(self) ?
        self._to_states = policy.next_states(self)

    @property
    def id(self):
        return self._action

    @property
    def from_state(self):
        return self._from_state

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, value):
        self._probability = value

    @property
    def to_states(self):
        return self._to_states

    @property
    def reward(self):
        raise NotImplementedError


class StatesList(list):

    def __init__(self, *args):
        list.__init__(self, *args)

    @property
    def weights(self):
        return NotImplemented

    @property
    def value_functions(self):
        return [item.value_function for item in self]


class ActionsList(list):

    def __init__(self, *args):
        list.__init__(self, *args)

    def init_probabilities(self, method='uniform'):
        if len(self) == 0:
            return None

        if method == 'random':
            prob = random(len(self))
            prob = list(prob / prob.sum())
        else:
            prob = [1 / len(self)] * len(self)

        for action, p in list(zip(*(self, prob))):
            action.probability = p

    @property
    def probabilities(self):
        return [action.probability for action in self]

    @property
    def value_functions(self):
        return [item.value_function for item in self]


class Policy:

    def __init__(self, init_policy='uniform'):
        self._states = NotImplemented  # List
        self.__states_architecture = NotImplemented  # Custom architecture
        self._init_policy = NotImplemented

        self._check_init_policy(init_policy)

    def __init_states(self):
        """Initialise states."""
        raise NotImplementedError

    # def next_states(self, action):
    #     """Method used to find the next states given an action."""
    #     raise NotImplementedError

    def execute(self):
        """Links each state to their next states."""
        for state in self.states:
            for action in state.actions:
                action.populate_next(self)
            state.actions.init_probabilities(self.init_policy)

    @property
    def states(self):
        """Return all states in a list."""
        raise NotImplementedError  # StatesList

    @property
    def init_policy(self):
        return self._init_policy

    @init_policy.setter
    def init_policy(self, value):
        self._check_init_policy(value)
        self.execute()

    def _check_init_policy(self, value):
        accepted_value = ('random', 'uniform')
        if value not in accepted_value:
            raise ValueError(f"'init_policy' must be one of {accepted_value}: "
                             f"'{value}' has been given.")
        self._init_policy = value
