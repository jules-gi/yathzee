import numpy as np

from game import components, rewards

CHECK_REWARDS = [
    rewards.check_unique_value,
    rewards.check_kind,
    rewards.check_full,
    rewards.check_straight,
    rewards.check_yathzee,
    rewards.check_chance
]
# TODO
ROLL_PROBABILITIES = {}


def roll_dice(n):
    return list(np.random.choice([1, 2, 3, 4, 5, 6], n))


def get_combinations(n_dice, step, min_value=1, max_value=6,
                     is_terminal=False, return_list=False,
                     dice_id=0, store=None, combination=None):
    """
    Returns all possible combinations by rolling a given number of dice.

    :param n_dice: The number of dice to roll
    :param step: The current step of the turn
    :param min_value: The minimum value of the rolled dice
    :param max_value: The maximum value of the rolled dice
    :param is_terminal: If all Combination states are terminal or not (if `return_list=False`)
    :param return_list: If True return a list of tuple(), otherwise return a dictionary of Combination()
    :param dice_id: Recursive parameter, the id of the rolled dice
    :param store: Recursive parameter, the dict (or list) to store the combinations
    :param combination: Recursive parameter, the current combination explored

    :return: A dict of Combination() states (if `return_list=False`), otherwise a list of tuple()
    """

    if store is None:
        store = [] if return_list else {}

    if combination is None:
        combination = [None] * (n_dice - dice_id)

    # Stopping criterion
    if dice_id == n_dice - 1:
        for value in range(min_value, max_value + 1):
            combination[dice_id] = value
            if return_list:
                store.append(list(combination))
            else:
                combination_state = components.Combination(combination, step, is_terminal)
                if step < 4:
                    actions = get_choices(combination_state)
                    combination_state.set_actions(actions)
                store[value] = combination_state
        return store

    # Recursive calls
    for value in range(min_value, max_value + 1):
        if not return_list:
            store[value] = {}
        combination[dice_id] = value
        get_combinations(n_dice, step, value, max_value, is_terminal, return_list,
                         dice_id + 1, (store if return_list else store[value]),
                         combination)

    return store


def get_keep_combinations(combination, n_keep,
                          keep_id=0, store=None,
                          keep_combination=None):
    """
    Returns all possible combinations from a given set of preserved dice.

    :param combination: The combination of dice
    :param n_keep: Number of dice to keep
    :param keep_id: Recursive parameter, the id of the dice in the preserved combination
    :param store: Recursive parameter, the list to store the combinations
    :param keep_combination: Recursive parameter, the current combination explored

    :return: A list of tuple()
    """
    if n_keep == 0:
        return [tuple()]

    if store is None:
        store = []

    if keep_combination is None:
        keep_combination = [None] * n_keep

    # Stopping criterion
    if keep_id == n_keep - 1:
        for value in combination[keep_id:]:
            keep_combination[keep_id] = value
            store.append(tuple(keep_combination))
        return list(set(store))

    # Recursive calls
    for extra_id, value in enumerate(combination[keep_id:]):
        keep_combination[keep_id] = value
        get_keep_combinations(combination[extra_id:], n_keep, keep_id + 1, store, keep_combination)

    return list(set(store))


# def get_combinations_distribution(n_keep, keep_id=0, store=None):
#     pass


def get_choices(combination):
    """
    Returns all possible choices (actions) to be made for a given combination (state).

    :param combination: The given combination (type Combination())

    :return: A list of Choice()
    """
    if not isinstance(combination, components.Combination):
        raise TypeError(f"'combination' must be of the type `Combination()`: "
                        f"{type(combination)} has been given.")

    if combination.step == 0:
        return [components.Choice(from_state=combination, probability=1.)]

    if combination.step == 3:
        return get_final_choices(combination)

    choices = []
    for n_keep in range(len(combination) + 1):
        keep_combinations = get_keep_combinations(combination, n_keep)

        # One choice (action) per preserved combination
        for keep in keep_combinations:
            choices.append(
                components.Choice(keep_combination=keep, from_state=combination, probability=1.)
            )

    return choices


def get_final_choices(combination):
    """
    Return all possible final choices to be made.

    :param combination: The given combination (type Combination())

    :return: A list of FinalChoice()
    """

    final_choices = []
    for check in CHECK_REWARDS:
        final_choices += check(combination)

    return final_choices
