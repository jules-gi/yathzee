<!-- title: Mise en place d'un environnement -->

# Apprentissage par renforcement - Mise en place d'un environnement

**Girard Jules - M2 Science des Données - Université de Rouen**

L'objectif de ce travail est de mettre en forme les éléments nécessaires à la mise en place d'un environnement d'apprentissage par renforcement, dans le but d'apprendre la meilleure stratégie de choix de dés dans le contexte du Yathzee (ou Yam's). Pour rappel, le but du jeu est de réaliser au plus trois lancés de dés avant de choisir un certain motif nous rapportant un certain nombre de points.


# Description de l'environnement

Le projet est constitué de deux modules: `learning` et `game`. Le premier définit les classes et fonctions de base nécessaires à l'apprentissage par renforcement (*eg.* `State()`, `Action()`, méthodes de Monte Carlo, etc...), le deuxième utilise ces éléments de base pour définir une architecture de politique spécifique au jeu du Yathzee. Enfin, le fichier `main.py` permet d'exécuter et tester les algorithmes.

```shell
+-- learning
    +-- components.py
    +-- monte_carlo.py
    +-- temporal_differences.py
    +-- utils.py

+-- game
    +-- components.py
    +-- rewards.py
    +-- utils.py

main.py
```

## Module `learning`

### Fichier `components.py`

Dans ce fichier se trouve l'ensemble des classes de base nécessaires à l'implémentation d'une politique. On y définit les méthodes des base permettant d'ajouter une action à un état, d'obtenir un état d'arrivée après avoir exécuté une action, ou encore d'initialiser une politique uniforme ou aléatoire.


### Fichiers `monte_carlo.py` et `temporal_differences.py`

Ces deux fichiers contiennent les algorithmes d'apprentissage vus en cours.


### Fichier `utils.py`

Ce fichier contient des fonctions utilitaires, comme la sélection aléatoire d'un état et d'une action, le calcul de la "récompense" complète d'un état dans un épisode et la génération d'un épisode.


## Module `game`

Ce module permet de modéliser l'environnement, *ie.* la mise en place d'une architecture d'états et d'actions permettant de modéliser le jeu du Yathzee.


### Fichier `rewards.py`

Ce fichier définit les fonctions de récompense qu'on obtient en fonction d'une combinaison de dés donnée.


### Fichier `utils.py`

Ce fichier contient des fonctions utilitaires, particulièrement nécessaires à la définition de notre environnement comme l'énumération des combinaisons de dés possibles en fonction du nombre de dés qu'on possède.


### Fichier `components.py`

Ce fichier définit les classes nécessaires à la modélisation de notre environnement: les états et les actions. Il réutilise les classes de base présentées dans le module précédent, ainsi que les fonctions définies dans `game/rewards.py` et `game/utils.py`


#### Classe `Turn()`

Cet objet hérite de notre composant `Policy()` (cf. `learning/components.py`). On y redéfinit la méthode `.__init_states()`, méthode principale dans la mise en place de l'environnement.


#### Classe `Combination()`

Cet objet correspond aux états, il hérite donc de notre composant `State()` (cf. `learning/components.py`).

Une combinaison est définit à la fois par la combinaison de dés qu'elle représente, mais aussi par le nombre de fois que le joueur a déjà lancé les dés: `step={0, 1, 2, 3, 4}` (où 4 correspond à l'état terminal "fictif" après avoir choisit le motif final nous rapportant un certain nombre de points).


#### Classe `Choice()` et `FinalChoice()`

Ces objets correspondent aux actions qu'on peut effectuer lorsqu'on se trouve dans un état donné, ils héritent donc de notre composant `Action()` (cf. `learning/components.py`).

Une action `Choice()` est effectuée par les états ayant `step={0, 1, 2}`, la récompense obtenue est de $0$. Cette action est définit comme une combinaison de $n$ dés que le joueur conserve. Le joueur relance ensuite les dés restant: une action `Choice()` peut donc mener à plusieurs états différents ayant `step={0, 1, 2} + 1`. Si le joueur conserve tous les dés, alors il arrive directement vers l'état ayant la même combinaison et `step=3`.

Une action `FinalChoice()` est effectuée par les états ayant `step=3`. Il s'agit du choix du motif (*eg.* *Full*, petite suite, Yathzee, etc...) rapportant un certain nombre de points en fonction de la combinaison de dés que le joueur a obtenu: la récompense dépend donc de la combinaison finale et du motif choisi. Cette action mène vers l'état terminal "fictif" (`step=4`), et la récompense correspond au nombre de points obtenu du motif choisit par rapport à la combinaison. De fait, la récompense n'est obtenue qu'à la fin, lors du choix final du motif.


## Exemples

Tout d'abord, on initialise l'environnement de la politique en appelant `Turn()`. Le problème est modéliser par $758$ états connectés les uns aux autres par $12 013$ actions.

```python
from game.components import Turn

turn = Turn(init_policy='uniform')

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

### Modélisation des états

Dans notre cas, on peut distinguer quatre catégories d'états:

- L'état initial `step=0`: aucun dé n'a été lancé, la seule action possible est de lancer tous les dés.

```python
# Step = 0
init_state = turn.states[0]

print(repr(init_state))

>>> {step: 0, combination: ()}

print(init_state.actions)

>>> [{n_keep: 0, keep_combination: ()}]
```

- Les états de transition `step={1, 2, 3}`, correspondant aux 252 combinaisons qu'il est possible d'obtenir après le premier, le deuxième et le troisème lancé de dés. Pour les combinaisons ayant `step={1, 2}`, seules les actions `Choice()` sont possibles: conserver un certain nombre de dés associé à une combinaison possible ; pour les combinaisons ayant `step=3`, seules les actions `FinalChoice()` associées à un nom de motif sont possibles. 

```python
# Step = 1
state = turn.states[150]

print(repr(state))

>>> {step: 1, combination: (2, 2, 3, 5, 6)}

print(state.actions)

>>> [{n_keep: 0, keep_combination: ()}, {n_keep: 1, keep_combination: (6)}, {n_keep: 1, keep_combination: (2)}, {n_keep: 1, keep_combination: (3)}, {n_keep: 1, keep_combination: (5)}, {n_keep: 2, keep_combination: (2, 3)}, {n_keep: 2, keep_combination: (2, 6)}, {n_keep: 2, keep_combination: (3, 6)}, {n_keep: 2, keep_combination: (5, 6)}, {n_keep: 2, keep_combination: (2, 2)}, {n_keep: 2, keep_combination: (2, 5)}, {n_keep: 2, keep_combination: (3, 5)}, {n_keep: 3, keep_combination: (2, 2, 3)}, {n_keep: 3, keep_combination: (2, 2, 6)}, {n_keep: 3, keep_combination: (2, 3, 6)}, {n_keep: 3, keep_combination: (3, 5, 6)}, {n_keep: 3, keep_combination: (2, 2, 5)}, {n_keep: 3, keep_combination: (2, 3, 5)}, {n_keep: 3, keep_combination: (2, 5, 6)}, {n_keep: 4, keep_combination: (2, 2, 5, 6)}, {n_keep: 4, keep_combination: (2, 2, 3, 5)}, {n_keep: 4, keep_combination: (2, 2, 3, 6)}, {n_keep: 4, keep_combination: (2, 3, 5, 6)}, {n_keep: 5, keep_combination: (2, 2, 3, 5, 6)}]


# Step = 3
state = turn.states[-150]

print(repr(state))

>>> {step: 3, combination: (1, 3, 4, 4, 6)}

print(state.actions)

>>> [{pattern: Count_1, keep_combination: (1, 3, 4, 4, 6), reward: 1}, {pattern: Count_2, keep_combination: (1, 3, 4, 4, 6), reward: 0}, {pattern: Count_3, keep_combination: (1, 3, 4, 4, 6), reward: 3}, {pattern: Count_4, keep_combination: (1, 3, 4, 4, 6), reward: 8}, {pattern: Count_5, keep_combination: (1, 3, 4, 4, 6), reward: 0}, {pattern: Count_6, keep_combination: (1, 3, 4, 4, 6), reward: 6}, {pattern: Kind_3, keep_combination: (1, 3, 4, 4, 6), reward: 0}, {pattern: Kind_4, keep_combination: (1, 3, 4, 4, 6), reward: 0}, {pattern: Full, keep_combination: (1, 3, 4, 4, 6), reward: 0}, {pattern: Small_Straight, keep_combination: (1, 3, 4, 4, 6), reward: 0}, {pattern: Large_Straight, keep_combination: (1, 3, 4, 4, 6), reward: 0}, {pattern: Yathzee, keep_combination: (1, 3, 4, 4, 6), reward: 0}, {pattern: Chance, keep_combination: (1, 3, 4, 4, 6), reward: 18}]
```

- L'état terminal `step=4`: aucune action n'est possible.

```python
# Step = 4
terminal_state = turn.states[-1]

print(repr(terminal_state))

>>> {step: 4, combination: ()}

print(terminal_state.actions)

>>> []
```


### Modélisation des actions

Comme expliqué précédemment, une action effectuée par un état ayant `step={0, 1, 2}` permet d'aller vers un état ayant `step={0, 1, 2} + 1`. L'ensemble des états d'arrivée correspondent aux combinaisons qu'on peut obtenir à partir de la combinaison de dés que conserve l'action et les autres valeur de dés qu'on peut obtenir. *A ce propos, je n'ai pas réussi à utiliser les probabilités d'effectuer une combinaison particulière. De fait, dans ma modélisation, la probabilité d'arriver dans un état à partir d'une action effectuée est identique pour tous les états d'arrivée (ce qui n'est pas correct: par exemple la probabilité d'obtenir 2 fois la même valeur sur un lancé de deux dés est plus faible que d'obtenir 2 valeurs différentes...). Il faudrait corriger cette erreur.*

Aussi, pour le même état, l'action de conserver les cinq dés emmène directement vers l'état ayant la même combinaison et `step=3`. Dans ce cas, un seul état d'arrivé est possible.

```python
# Step = 1, n_keep = 4
action = turn.states[150].actions[20]

print(action)

>>> {n_keep: 4, keep_combination: (2, 2, 3, 5)}

print(action.to_states)

>>> [{step: 2, combination: (1, 2, 2, 3, 5)}, {step: 2, combination: (2, 2, 2, 3, 5)}, {step: 2, combination: (2, 2, 3, 3, 5)}, {step: 2, combination: (2, 2, 3, 4, 5)}, {step: 2, combination: (2, 2, 3, 5, 5)}, {step: 2, combination: (2, 2, 3, 5, 6)}]

# Step = 1, n_keep = 5
action = turn.states[150].actions[-1]

print(action)

>>> {n_keep: 5, keep_combination: (2, 2, 3, 5, 6)}

print(action.to_states)

>>> [{step: 3, combination: (2, 2, 3, 5, 6)}]
```

Le fait d'effectuer cette action (en appelant la méthode `__call__` de l'objet) nous emmène directement vers l'état suivant:

```python
next_state = action()

print(next_state)

>>> {step: 3, combination: (2, 2, 3, 5, 6)}
```

Enfin, l'éxécution d'une action `FinalChoice()` nous emmène bien vers le dernier état terminal, ce qui met fin à notre tour:

```python
final_states = []
for action in next_state.actions:
    final_states.append(action())

print(np.all(final_state))

>>> True
```

# Utilisation des algorithmes

Il est assez compliqué de visualiser les résultats que l'on obtient, mais il semble que les méthodes d'apprentissage fonctionnent plutôt bien. Étant donné que les actions pouvant être effectuées dépendent bien de l'état dans lequel on est, et que les actions mènent bien vers les états qu'il est possible d'obtenir, il n'y a pas de raison que les algorithmes fonctionnent moins bien que précédemment...

## Méthodes de Monte Carlo

```python
from learning.monte_carlo import predictions, exploring_starts, on_policy_control

n_iter = 100000
gamma = .8
```

### Monte Carlo *Predictions*

```python
predictions_policy = predictions(turn, gamma=gamma, n_iter=n_iter, first_visit=True)
```


### Monte Carlo *Exploring Start*

```python
exploring_starts_policy = exploring_starts(turn, gamma=gamma, n_iter=n_iter)
```


### Monte Carlo *On Policy Control*

```python
on_policy_control_policy = on_policy_control(turn, gamma=gamma, epsilon=.25, n_iter=n_iter, first_visit=True)
```

## Méthodes *Temporal Differences*

```python
from learning.temporal_differences import td0, sarsa

alpha = .5
```

### TD0

```python
td0_policy = td0(turn, alpha=alpha, gamma=gamma, n_iter=N_ITER)
```

### SARSA

```python
sarsa_policy = sarsa(turn, alpha=alpha, gamma=gamma, n_iter=N_ITER)
```