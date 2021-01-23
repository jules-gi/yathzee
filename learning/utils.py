from random import choices


def g(episode, t, gamma):
    """
    Compute the complete return of a state in a episode.

    :param episode: The given episode
    :param t: The step where the state is in the episode
    :param gamma: Reward reducer parameter

    :return: The complete return of the state in the episode
    """
    output = 0
    for i, (_, action) in enumerate(episode[t:]):
        output += (gamma ** i) * action.reward
    return output


def generate_episode(origin_state, origin_action=None, use_policy=False, max_step=1000):
    """
    Generate an episode.

    :param origin_state: Starting state of the episode
    :param origin_action: First action to choose (optional)
    :param use_policy: Use policy to choose the actions
    :param max_step: Maximal number of step in the episode

    :return: A list of tuple (state, action)
    """

    if origin_action is not None:
        episode = [(origin_action.from_state, origin_action)]
        current_state = choices(origin_action.to_states)[0]
        t = 1
    else:
        episode = []
        current_state = origin_state
        t = 0

    while t < max_step and not current_state.is_terminal:
        actions = current_state.actions
        if use_policy:
            action = choices(actions, weights=actions.probabilities)[0]
        else:
            action = choices(actions)[0]

        episode.append((current_state, action))
        current_state = choices(action.to_states)[0]

    return episode


def select_random_state(states, select_action=False, use_policy=False):
    """
    Randomly select a non-terminal state among a list of state.

    :param states: List of states
    :param select_action: If True, choose a random action given the selected state.
    :param use_policy: If True and `select_random_action=True`, use the policy distribution to select the action

    :return: A state, or a tuple (state, action) if `select_random_action=True`
    """
    if select_action:
        while True:
            state = choices(states)[0]
            if state.is_terminal:
                continue
            action = select_random_action(state, use_policy=use_policy)
            if action.probability > 0.:
                return state, action

    # Else, select only random state
    return choices(states)[0]


def select_random_action(state, use_policy=False):
    """
    Randomly select a action from a given state.

    :param state: The state from which choose an action
    :param use_policy: Use the policy distribution to select the action

    :return: An action
    """
    if state.is_terminal:
        return None

    if use_policy:
        return choices(state.actions, weights=state.actions.probabilities)[0]
    return choices(state.actions)[0]
