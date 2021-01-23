import numpy as np

from game import components

__all__ = [
    'check_unique_value',
    'check_kind',
    'check_full',
    'check_straight',
    'check_yathzee',
    'check_chance'
]


def check_unique_value(combination):
    array = np.asarray(combination)
    return [components.FinalChoice(from_state=combination,
                                   probability=1.,
                                   keep_combination=combination,
                                   name=f'Count_{value}',
                                   reward=np.sum(array[array == value]))
            for value in range(1, 7)]


def check_kind(combination):
    array = np.asarray(combination)
    _, counts = np.unique(array, return_counts=True)
    return [components.FinalChoice(from_state=combination,
                                   probability=1.,
                                   keep_combination=combination,
                                   name=f'Kind_{kind}',
                                   reward=(np.sum(array) if kind <= max(counts) else 0))
            for kind in (3, 4)]


def check_full(combination):
    array = np.asarray(combination)
    _, counts = np.unique(array, return_counts=True)
    return [components.FinalChoice(from_state=combination,
                                   probability=1.,
                                   keep_combination=combination,
                                   name='Full',
                                   reward=(25 if len(set(combination)) == 2 and min(counts) > 1 else 0))]


def check_straight(combination):
    straights_infos = {
        'straights': [[{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}],
                      [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]],
        'reward': [30, 40],
    }
    returns = [components.FinalChoice(from_state=combination,
                                      probability=1.,
                                      keep_combination=combination,
                                      name=name,
                                      reward=0)
               for name in ('Small_Straight', 'Large_Straight')]

    for i, (straights, reward) in enumerate(list(zip(*straights_infos.values()))):
        for straight in straights:
            if straight.issubset(set(combination)):
                returns[i]._reward = reward

    return returns


def check_yathzee(combination):
    return [components.FinalChoice(from_state=combination,
                                   probability=1.,
                                   keep_combination=combination,
                                   name='Yathzee',
                                   reward=(50 if len(set(combination)) == 1 else 0))]


def check_chance(combination):
    array = np.asarray(combination)
    return [components.FinalChoice(from_state=combination,
                                   probability=1.,
                                   keep_combination=combination,
                                   name='Chance',
                                   reward=np.sum(array))]


if __name__ == '__main__':

    from game.components import Combination
    a = Combination((1, 2, 3, 4, 5), step=0, is_terminal=False)
    b = check_straight(a)

    breakpoint()
