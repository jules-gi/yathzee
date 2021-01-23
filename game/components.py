from abc import ABC

from learning.components import State, StatesList, Action, Policy
from game.utils import get_combinations, get_choices
# from game import utils


# Les states correspondent aux combinaisons de 5 dés possibles
#   aux 3 étapes de mes lancés
# Les actions correspondent aux dés que je vais sélectionner
#   en fonction de ceux que je possède
# TODO: Faire fonctionner l'application Turn()


class Combination(tuple, State):

    def __new__(cls, combination, step, is_terminal):
        return tuple.__new__(Combination, combination)

    def __init__(self, combination, step, is_terminal):
        super().__init__(is_terminal)
        self._state = tuple((step, tuple(combination)))
        self._step = step

    def __getnewargs__(self):
        return self._state[1], self._step, self.is_terminal

    def __str__(self):
        return f'({", ".join([str(dice) for dice in self])})'

    def __repr__(self):
        return f'{{step: {self._step}, combination: ({", ".join([repr(dice) for dice in self])})}}'

    @property
    def step(self):
        return self._step


class CombinationList(StatesList, ABC):

    def __init__(self, combinations, n_keep):
        list.__init__(combinations)
        # self._distribution = get_combinations_distribution(n_keep)
        self._weights = []
        self._update_weights()

    def append(self, item):
        super(CombinationList, self).append(item)
        self._update_weights()

    def _update_weights(self):
        if len(self) > 0:
            self._weights = [1 / len(self)] * len(self)

    @property
    def weights(self):
        return self._weights


class Choice(Action, ABC):

    # Les actions que je peux faire:
    #   - Garder 0 dé, relancer 5  (6**5 successeurs)
    #   - Garder 1 dé, relancer 4  (6**4 successeurs)
    #   - Garder 2 dés, relancer 3  (6**3 successeurs)
    #   - Garder 3 dés, relancer 2  (6**2 successeurs)
    #   - Garder 4 dés, relancer 1  (6**1 successeurs)

    def __init__(self, keep_combination=None, **kwargs):
        super().__init__(**kwargs)

        if keep_combination is None:
            keep_combination = list()

        self._keep_combination = list(keep_combination)
        self._n_keep = len(keep_combination)
        self._action = tuple((self._n_keep, tuple(self._keep_combination)))
        self._to_states = CombinationList([], n_keep=self._n_keep)

    def __repr__(self):
        return f'{{n_keep: {self.n_keep}, keep_combination: ' \
               f'({", ".join([repr(dice) for dice in self.keep_combination])})}}'

    def populate_next(self, policy):

        if not self.from_state.is_terminal:

            if self._n_keep == 5:
                combination = policy.get_states(step=3)
                for value in self._keep_combination:
                    combination = combination[value]
                self._to_states.append(combination)
            else:
                next_step = self.from_state.step + 1

                completed_combinations = get_combinations(5 - self.n_keep, next_step, return_list=True)
                # completed_combinations = utils.get_combinations(5 - self.n_keep, next_step, return_list=True)
                for completed in completed_combinations:
                    searched_combination = sorted(self.keep_combination + completed)
                    combination = policy.get_states(step=next_step)
                    for value in searched_combination:
                        combination = combination[value]
                    self._to_states.append(combination)

            # TODO: temporaire
            self.to_states._distribution = [1 / len(self.to_states)] * len(self.to_states)

    @property
    def n_keep(self):
        return self._n_keep

    @property
    def keep_combination(self):
        return self._keep_combination

    @property
    def reward(self):
        return 0


class FinalChoice(Choice, ABC):

    def __init__(self, name, reward, **kwargs):
        super().__init__(**kwargs)
        self._action = self._action + tuple((name,))
        self._name = name
        self._reward = reward

    def __repr__(self):
        return f'{{pattern: {self._name}, keep_combination: ' \
               f'({", ".join([repr(dice) for dice in self.keep_combination])}), ' \
               f'reward: {self._reward}}}'

    def populate_next(self, policy):
        combination = policy.get_states(step=4)
        if not isinstance(combination, Combination):
            for value in self.keep_combination:
                combination = combination[value]
        self._to_states.append(combination)

    @property
    def name(self):
        return self._name

    @property
    def reward(self):
        return self._reward


class Turn(Policy):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._step = 0
        self._selected_dices = []
        self._selection = False

        self.__init_states()
        self.execute()

    def __init_states(self):

        init_state = Combination([], step=0, is_terminal=False)
        init_state.set_actions(get_choices(init_state))
        # init_state.set_actions(utils.get_choices(init_state))

        self.__states_architecture = dict([(0, init_state)])
        for step in range(1, 4):
            self.__states_architecture[step] = get_combinations(n_dice=5, step=step, is_terminal=False)
        self.__states_architecture[4] = Combination([], step=4, is_terminal=True)

        self._states = self._dive_in_dict_states(self.__states_architecture)

    @property
    def states(self):
        return self._states

    def get_states(self, step):
        return self.__states_architecture[step]

    def _dive_in_dict_states(self, states, store=None):
        if store is None:
            store = []

        for k, v in states.items():
            if isinstance(v, Combination):
                store.append(v)
            else:
                self._dive_in_dict_states(v, store)
        return store

    # def roll(self):
    #     if self._selection:
    #         raise ValueError('You must validate the selection of the dice '
    #                          'before a new roll.')
    #     if self._step >= 3:
    #         raise ValueError('You cannot roll more than 3 times.')
    #     self.combination = self._selected_dices + roll_dice(5 - len(self._selected_dices))
    #     self._selection = True
    #     self._step += 1

    # def valid_selection(self, selection=None):
    #     if selection is None:
    #         selection = []
    #     elif isinstance(selection, int):
    #         selection = [selection]
    #
    #     for select in selection:
    #         self._selected_dices.append(self.combination[select])
    #     self._selection = False

    # @property
    # def selected_dices(self):
    #     return self._selected_dices
    #
    # def restore(self):
    #     self._step = 0
    #     self._selection = False
    #     self._selected_dices = []
