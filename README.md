<!-- title: Mise en place d'un environnement -->

Reference: [Richard S. Sutton and Andrew G. Barto, Reinforcement Learning, second edition: An Introduction](https://web.stanford.edu/class/psych209/Readings/SuttonBartoIPRLBook2ndEd.pdf)

# What dices to choose when playing Yathzee? A reinforcement learning approach

As an introduction to reinforcement learning, the final project of my master's course was to set up an environment to teach to an AI (called "agent") how to play a turn of Yathzee (or Yam's). For this, I used Python! If you are not familiar with the Yathzee, [Wikipedia](https://en.wikipedia.org/wiki/Yahtzee) explain the rules and variants quite well.

My contributions are implementation of some reinforcement learning base [components](learning/components.py) like states, actions and policy, then using and translate them to the [Yathzee environment](game/components.py) like combinations of dice to express states, the choice of which dice to keep as actions, the set of three steps to roll dice stages as a policy, and finally implement some algorithms of reinforcment learning like [Monte Carlo](learning/monte_carlo.py) or [Temporal Differences](learning/temporal_differences.py) methods.

The only bug I need to fix is to take into account the probability of rolling a given combination of dice.


## How looks the environment?

To get started, just call `Turn()`. The Yathzee problem is discribed with 758 different states and 12 013 actions linking the states between them.

```python
from game.components import Turn

turn = Turn()

n_states = 0
n_actions = 0
for state in turn.states:
    n_states += 1
    n_actions += len(state.actions)


print('Number of states: {}'.format(n_states))

>>> Number of states: 758

print('Number of actions: {}'.format(n_actions))

>>> Number of actions: 12013
```

Each state and action got their respective value function as attribute, and the transition probability is stored as action attribute:
```python

state = turn.states[150]
action = state.actions[5]

print(state.value_function)

>>> 0

print(action.value_function, action.probability)

>>> 0, 0.041666
```


### The states

There are 3 kind of states:
- The initial state, where no dice is selected;
```python
# First roll
init_state = turn.states[0]

print(repr(init_state))

>>> {step: 0, combination: ()}

print(init_state.actions)  # print the list of resulting actions

>>> [{n_keep: 0, keep_combination: ()}]
```

- The transition states, corresponding to the 252 possible combinations on each roll of the dice. Below two different states: the first where the agent have to choose which dice to keep and roll again the others, the second one where the agent cannot roll the dice anymore and it have to choose a pattern to win points;
```python
# Second roll
state = turn.states[150]

print(repr(state))

>>> {step: 1, combination: (2, 2, 3, 5, 6)}

print(state.actions)  # print the list of resulting actions

>>> [
    {n_keep: 0, keep_combination: ()},
    {n_keep: 1, keep_combination: (6)},
    {n_keep: 1, keep_combination: (2)},
    {n_keep: 1, keep_combination: (3)},
    {n_keep: 1, keep_combination: (5)},
    {n_keep: 2, keep_combination: (2, 3)},
    {n_keep: 2, keep_combination: (2, 6)},
    {n_keep: 2, keep_combination: (3, 6)},
    {n_keep: 2, keep_combination: (5, 6)},
    {n_keep: 2, keep_combination: (2, 2)},
    {n_keep: 2, keep_combination: (2, 5)},
    {n_keep: 2, keep_combination: (3, 5)},
    {n_keep: 3, keep_combination: (2, 2, 3)},
    {n_keep: 3, keep_combination: (2, 2, 6)},
    {n_keep: 3, keep_combination: (2, 3, 6)},
    {n_keep: 3, keep_combination: (3, 5, 6)},
    {n_keep: 3, keep_combination: (2, 2, 5)},
    {n_keep: 3, keep_combination: (2, 3, 5)},
    {n_keep: 3, keep_combination: (2, 5, 6)},
    {n_keep: 4, keep_combination: (2, 2, 5, 6)},
    {n_keep: 4, keep_combination: (2, 2, 3, 5)},
    {n_keep: 4, keep_combination: (2, 2, 3, 6)},
    {n_keep: 4, keep_combination: (2, 3, 5, 6)},
    {n_keep: 5, keep_combination: (2, 2, 3, 5, 6)}
]

# Choice of the pattern
state = turn.states[-150]

print(repr(state))

>>> {step: 3, combination: (1, 3, 4, 4, 6)}

print(state.actions)  # print the list of resulting actions

>>> [
    {pattern: Count_1, keep_combination: (1, 3, 4, 4, 6), reward: 1},
    {pattern: Count_2, keep_combination: (1, 3, 4, 4, 6), reward: 0},
    {pattern: Count_3, keep_combination: (1, 3, 4, 4, 6), reward: 3},
    {pattern: Count_4, keep_combination: (1, 3, 4, 4, 6), reward: 8},
    {pattern: Count_5, keep_combination: (1, 3, 4, 4, 6), reward: 0},
    {pattern: Count_6, keep_combination: (1, 3, 4, 4, 6), reward: 6},
    {pattern: Kind_3, keep_combination: (1, 3, 4, 4, 6), reward: 0},
    {pattern: Kind_4, keep_combination: (1, 3, 4, 4, 6), reward: 0},
    {pattern: Full, keep_combination: (1, 3, 4, 4, 6), reward: 0},
    {pattern: Small_Straight, keep_combination: (1, 3, 4, 4, 6), reward: 0},
    {pattern: Large_Straight, keep_combination: (1, 3, 4, 4, 6), reward: 0},
    {pattern: Yathzee, keep_combination: (1, 3, 4, 4, 6), reward: 0},
    {pattern: Chance, keep_combination: (1, 3, 4, 4, 6), reward: 18}
]
```

- The final state, corresponding to the end of the turn, no action is associated. The agent reach this one after choosing a pattern;
```python
terminal_state = turn.states[-1]

print(repr(terminal_state))

>>> {step: 4, combination: ()}

print(terminal_state.actions)

>>> []
```

### The actions

An action represent the selection of certain dice after having thrown them. Depending on this choice, the agent can reach several different states, linked to the value of dice not kept after having thrown them again. For example, when an agent select four dice, it can reach six different states based on the combination of the selected dice plus the random value of the non-selected dice.

```python
state = turn.states[150]
print(repr(state))

>>> {step: 1, combination: (2, 2, 3, 5, 6)}

action = state.actions[20]
print(action)

>>> {n_keep: 4, keep_combination: (2, 2, 3, 5)}

print(action.to_states)

>>> [
    {step: 2, combination: (1, 2, 2, 3, 5)},
    {step: 2, combination: (2, 2, 2, 3, 5)},
    {step: 2, combination: (2, 2, 3, 3, 5)},
    {step: 2, combination: (2, 2, 3, 4, 5)},
    {step: 2, combination: (2, 2, 3, 5, 5)},
    {step: 2, combination: (2, 2, 3, 5, 6)}
]
```

A second type of action does exist, called `FinalChoice()` in the code. The agent can only execute it if it has chosen to keep the five dice from the previous stage, or because it has already rolled them three times. This action correspond to the selection of the final pattern that leads directly to the final state, while rewarding the agent with a certain number of points.


## How to use the algorithms?

The use of the reinforcement learning are quite simple. You just need to give a policy object to the function, tune its parameters, and then it will return a new policy with new value function and/or new transition probability between the states.

*Making a visualisation of this problem is not the easiest thing, I should think about it!*

The following parameters correspond to:
- `gamma`: the discount rate to compute the complete return of a state
- `n_iter`: the number of iteration to let the agent explore and exploit its opportunities


### Monte Carlo methods

```python
from learning.monte_carlo import predictions, exploring_starts, on_policy_control

n_iter = 100000
gamma = .8

predictions_policy = predictions(turn, gamma=gamma, n_iter=n_iter, first_visit=True)
exploring_starts_policy = exploring_starts(turn, gamma=gamma, n_iter=n_iter)
on_policy_control_policy = on_policy_control(turn, gamma=gamma, epsilon=.25, n_iter=n_iter, first_visit=True)
```

With:
- `first_visit`: if `True` use the complete return of the first state visit, otherwise use the complete return of every visits;
- `epsilon`: the epislon-greedy policy parameter, 0 means full exploitation, 1 means full exploration;


### Temporal differences methods

```python
from learning.temporal_differences import td0, sarsa

alpha = .5

td0_policy = td0(turn, alpha=alpha, gamma=gamma, n_iter=n_iter)
sarsa_policy = sarsa(turn, alpha=alpha, gamma=gamma, n_iter=n_iter)
```

With:
- `alpha`: a step-size parameter
