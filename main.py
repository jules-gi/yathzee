# TODO: Ajouter un poids (ou probabilité) aux états suivants
# TODO: Docstrings et commentaires


def main():
    pass


if __name__ == '__main__':
    # main()

    from game.components import Turn
    from learning.monte_carlo import predictions, exploring_starts, on_policy_control
    from learning.temporal_differences import td0, sarsa

    turn = Turn(init_policy='uniform')

    n_states = 0
    n_actions = 0
    for state in turn.states:
        n_states += 1
        n_actions += len(state.actions)
    print('Number of states: {}'.format(n_states))
    print('Number of actions: {}'.format(n_actions))

    n_iter = 100000
    gamma = .8
    alpha = .5

    predictions_policy = predictions(turn, gamma=gamma, n_iter=n_iter, first_visit=True)
    exploring_starts_policy = exploring_starts(turn, gamma=gamma, n_iter=n_iter)
    on_policy_control_policy = on_policy_control(turn, gamma=gamma, epsilon=.25, n_iter=n_iter, first_visit=True)
    td0_policy = td0(turn, alpha=alpha, gamma=gamma, n_iter=n_iter)
    sarsa_policy = sarsa(turn, alpha=alpha, gamma=gamma, n_iter=n_iter)

    # breakpoint()
