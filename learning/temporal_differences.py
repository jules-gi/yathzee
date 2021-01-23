from copy import deepcopy

from learning.utils import select_random_state, select_random_action


def td0(policy, alpha=.1, gamma=1, n_iter=100):
    policy = deepcopy(policy)
    for state in policy.states:
        state.value_function = 0

    for it in range(n_iter):
        state = select_random_state(policy.states)

        while not state.is_terminal:
            action = select_random_action(state, use_policy=True)
            next_state = action(use_weights=True)
            state.value_function += alpha * (action.reward +
                                             gamma * next_state.value_function -
                                             state.value_function)
            state = next_state

    return policy


def sarsa(policy, alpha=.1, gamma=1, n_iter=100):
    policy = deepcopy(policy)
    for state in policy.states:
        if state.is_terminal:
            state.value_function = 0

    for it in range(n_iter):
        state, action = select_random_state(policy.states, select_action=True, use_policy=True)

        while not state.is_terminal:
            next_state = action(use_weights=True)
            if next_state.is_terminal:
                next_action = None
                next_q = 0
            else:
                next_action = select_random_action(next_state, use_policy=True)
                next_q = next_action.value_function

            action.value_function += alpha * (action.reward +
                                              gamma * next_q -
                                              action.value_function)
            state = next_state
            action = next_action

    return policy
