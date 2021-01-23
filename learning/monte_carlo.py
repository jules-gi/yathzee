from copy import deepcopy
import numpy as np

from learning.utils import generate_episode, select_random_state, g


def predictions(policy, gamma=1, n_iter=100, first_visit=True):
    policy = deepcopy(policy)

    returns = {state.id: [] for state in policy.states}
    for it in range(n_iter):
        origin_state = select_random_state(policy.states)
        episode = generate_episode(origin_state)

        known_states = []
        for t, (state, _) in enumerate(episode):
            if state not in known_states:
                known_states.append(state)
            elif first_visit:
                continue

            returns[state.id].append(g(episode, t, gamma))
            state.value_function = np.mean(returns[state.id])

    return policy


def exploring_starts(policy, gamma=1, n_iter=100):
    policy = deepcopy(policy)

    returns = {state.id: {action.id: [] for action in state.actions}
               for state in policy.states}

    for it in range(n_iter):
        origin_state, origin_action = select_random_state(policy.states,
                                                          select_action=True)

        episode = generate_episode(origin_state, origin_action, use_policy=True)
        known_pairs = []
        for t, (state, action) in enumerate(episode):
            if (state, action) in known_pairs:
                continue
            known_pairs.append((state, action))

            returns[state.id][action.id].append(g(episode, t, gamma))
            action.value_function = np.mean(returns[state.id][action.id])

        known_states = []
        for state, _ in episode:
            if state in known_states:
                continue
            known_states.append(state)

            actions = {action.id: action.value_function for action in state.actions}
            best_actions = [key for key, value in actions.items() if value == max(actions.values())]
            for action in state.actions:
                action.probability = 1 / len(best_actions) if action.id in best_actions else 0

    return policy


def on_policy_control(policy, gamma=1., epsilon=.1, n_iter=100, first_visit=True):
    policy = deepcopy(policy)

    # policy.init_policy = init_policy
    returns = {state.id: {action.id: [] for action in state.actions}
               for state in policy.states}

    for it in range(n_iter):
        origin_state = select_random_state(policy.states)

        episode = generate_episode(origin_state, use_policy=True)
        known_pairs = []
        for t, (state, action) in enumerate(episode):
            if first_visit and (state, action) in known_pairs:
                continue
            known_pairs.append((state, action))

            returns[state.id][action.id].append(g(episode, t, gamma))
            action.value_function = np.mean(returns[state.id][action.id])

        known_states = []
        for state, _ in episode:
            if state in known_states:
                continue
            known_states.append(state)

            actions = {action.id: action.value_function for action in state.actions}
            best_actions = [key for key, value in actions.items() if value == max(actions.values())]
            for action in state.actions:
                if action.id in best_actions:
                    action.probability = 1 - epsilon + epsilon / len(actions)
                else:
                    action.probability = epsilon / len(actions)

    return policy
