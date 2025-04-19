from cellularautomata import GenerateCA, SimulateCA, ShowSimulation

# Constants
b = 1.8  # Temptation to defect (1 < b < 2)
strategies = ['C', 'D']

# Payoff function
def get_payoff(strategy1, strategy2):
    if strategy1 == 'C' and strategy2 == 'C':
        return 1
    elif strategy1 == 'C' and strategy2 == 'D':
        return 0
    elif strategy1 == 'D' and strategy2 == 'C':
        return b
    else:  # D vs D
        return 0

# Evolution function for Nowak's Prisoner's Dilemma
def NowakPD(cell, neighbors):
    # Normalize cell format
    if not isinstance(cell, tuple) or len(cell) != 2:
        cell = (cell, None)
    # Normalize neighbors
    if neighbors is None:
        neighbors = []
    else:
        normalized_neighbors = []
        for n in neighbors:
            if not isinstance(n, tuple) or len(n) != 2:
                n = (n, None)
            normalized_neighbors.append(n)
        neighbors = normalized_neighbors

    my_strategy, _ = cell
    scores = {}

    # Compute payoffs for all players (self + neighbors)
    players = [cell] + neighbors
    for i, (strat_i, _) in enumerate(players):
        score = 0
        for j, (strat_j, _) in enumerate(players):
            if i != j:
                score += get_payoff(strat_i, strat_j)
        scores[i] = (score, strat_i)

    # Adopt the strategy of the player with the highest score
    best_index = max(scores, key=lambda k: scores[k][0])
    best_strategy = scores[best_index][1]

    return (best_strategy, None)


# Colors for visualization: Blue for Cooperators, Red for Defectors
cellcolors = {('C', None): 'blue', ('D', None): 'red'}

# Generate the initial cellular automaton with a 50-50 chance for 'C' and 'D'
weights = {'C': 0.5, 'D': 0.5}
CA0 = GenerateCA(100, cellcolors, weights)

# Simulate the CA evolution using NowakPD rules for 200 time steps.
simulation = SimulateCA(CA0, NowakPD, duration=200)

# Display the simulation results.
animation = ShowSimulation(simulation, cellcolors)

