import random
from colorama import Fore, Style
import numpy as np
# Define the actions
COOPERATE = 'cooperate'
DEFECT = 'defect'


# Define the strategies
def always_cooperate(history):
    return COOPERATE

def always_defect(history):
    return DEFECT

def random_choice_cooperate(history):
    return COOPERATE if random.random() < 0.75 else DEFECT

def random_choice_defect(history):
    return COOPERATE if random.random() < 0.25 else DEFECT

def random_choice_neutral(history):
    return COOPERATE if random.random() < 0.5 else DEFECT

def tit_for_tat(history):
    if not history:  # If it's the first round, cooperate
        return COOPERATE
    opponent_last_move = history[-1][1]  # Get the opponent's last move
    return opponent_last_move  # Mimic the opponent's last move

def bully(history):
    if not history:  # If it's the first round, defect
        return DEFECT
    opponent_last_move = history[-1][1]  # Get the opponent's last move
    return COOPERATE if opponent_last_move == DEFECT else DEFECT  # Do the opposite of the opponent's last move

def tat_for_tit(history):
    if not history:  # If it's the first round, cooperate
        return DEFECT
    opponent_last_move = history[-1][1]  # Get the opponent's last move
    return opponent_last_move  # Mimic the opponent's last move

def tit_for_two_tats(history):
    if len(history) < 2:  # If it's the first or second round, cooperate
        return COOPERATE
    opponent_last_two_moves = history[-2:]  # Get the opponent's last two moves
    if all(move[1] == DEFECT for move in opponent_last_two_moves):  # If the opponent defected in the last two rounds
        return DEFECT
    return COOPERATE
def original_gradual(history):
    if not history:  # If it's the first round, cooperate
        return COOPERATE

    # Initialize state variables
    if not hasattr(original_gradual, "calming"):
        original_gradual.calming = False
        original_gradual.punishing = False
        original_gradual.punishment_count = 0
        original_gradual.punishment_limit = 0

    # Calming phase
    if original_gradual.calming:
        original_gradual.calming = False
        return COOPERATE

    # Punishing phase
    if original_gradual.punishing:
        if original_gradual.punishment_count < original_gradual.punishment_limit:
            original_gradual.punishment_count += 1
            return DEFECT
        else:
            original_gradual.calming = True
            original_gradual.punishing = False
            original_gradual.punishment_count = 0
            return COOPERATE

    # Check if opponent defected in the last round
    if history[-1][1] == DEFECT:
        original_gradual.punishing = True
        original_gradual.punishment_count += 1
        original_gradual.punishment_limit += 1
        return DEFECT

    return COOPERATE

def contrite_tit_for_tat(history):
    if not history:  # If it's the first round, cooperate
        return COOPERATE

    # Initialize state variables
    if not hasattr(contrite_tit_for_tat, "contrite"):
        contrite_tit_for_tat.contrite = False
        contrite_tit_for_tat._recorded_history = []

    # If contrite but managed to cooperate: apologise.
    if contrite_tit_for_tat.contrite and history[-1][0] == COOPERATE:
        contrite_tit_for_tat.contrite = False
        return COOPERATE

    # Check if noise provoked opponent
    if contrite_tit_for_tat._recorded_history and contrite_tit_for_tat._recorded_history[-1] != history[-1][0]:  # Check if noise
        if history[-1][0] == DEFECT and history[-1][1] == COOPERATE:
            contrite_tit_for_tat.contrite = True

    contrite_tit_for_tat._recorded_history.append(history[-1][0])
    return history[-1][1]  # Mimic opponent's last move
def spiteful_tit_for_tat(history):
    if not history:  # If it's the first round, cooperate
        return COOPERATE

    # Initialize state variables
    if not hasattr(spiteful_tit_for_tat, "retaliating"):
        spiteful_tit_for_tat.retaliating = False

    # Check if opponent defected twice in a row
    if len(history) > 1 and history[-2][1] == DEFECT and history[-1][1] == DEFECT:
        spiteful_tit_for_tat.retaliating = True

    # If retaliating, always defect
    if spiteful_tit_for_tat.retaliating:
        return DEFECT
    else:
        # Mimic opponent's last move
        return history[-1][1]
players = [always_cooperate, always_defect, random_choice_defect, tit_for_tat, tit_for_two_tats, random_choice_cooperate, tat_for_tit, random_choice_neutral, bully,original_gradual, contrite_tit_for_tat, spiteful_tit_for_tat]

# Define the payoff matrix
payoff_matrix = {
    (COOPERATE, COOPERATE): (3, 3),
    (COOPERATE, DEFECT): (0, 5),
    (DEFECT, COOPERATE): (5, 0),
    (DEFECT, DEFECT): (1, 1)
}


# Define the players

# Assign a unique color to each player
player_colors = {
    'always_cooperate': '\033[38;2;0;255;0m',  # Green
    'always_defect': '\033[38;2;255;0;0m',  # Red
    'tit_for_tat': '\033[38;2;0;0;255m',  # Blue
    'random_choice_cooperate': '\033[38;2;255;0;255m',  # Magenta
    'random_choice_defect': '\033[38;2;255;80;80m',  # Light red
    'tat_for_tit': '\033[38;2;255;255;80m',  # Light yellow
    'random_choice_neutral': '\033[38;2;128;128;128m',  # Gray
    'tit_for_two_tats': '\033[38;2;80;80;80m',  # Light black
    'bully': '\033[38;2;0;255;255m',  # Cyan
    'original_gradual': '\033[38;2;80;255;80m',  # Light green
    'contrite_tit_for_tat': '\033[38;2;80;80;255m',  # Light blue
    'spiteful_tit_for_tat': '\033[38;2;80;255;255m'  # Light cyan
}

def tournament(players, rounds=100, filter_strategy='tat_for_tit'):
    total_scores = {player.__name__: 0 for player in players}
    wins = {player.__name__: 0 for player in players}
    losses = {player.__name__: 0 for player in players}  # New dictionary to store losses
    draws = {player.__name__: 0 for player in players}  # New dictionary to store draws
    for i in range(len(players)):
        for j in range(i, len(players)):
            player1 = players[i]
            player2 = players[j]
            history1 = []
            history2 = []
            match_scores = {player1.__name__: 0, player2.__name__: 0}
            for round in range(rounds):
                move1 = player1(history1)
                move2 = player2(history2)
                score1, score2 = payoff_matrix[(move1, move2)]
                match_scores[player1.__name__] += score1
                match_scores[player2.__name__] += score2
                total_scores[player1.__name__] += score1
                total_scores[player2.__name__] += score2
                history1.append((move1, move2))
                history2.append((move2, move1))

            # Increment win, loss, or draw count based on the match result
            if match_scores[player1.__name__] > match_scores[player2.__name__]:
                wins[player1.__name__] += 1
                losses[player2.__name__] += 1
            elif match_scores[player1.__name__] < match_scores[player2.__name__]:
                wins[player2.__name__] += 1
                losses[player1.__name__] += 1
            else:
                draws[player1.__name__] += 1
                draws[player2.__name__] += 1


            if  (player2.__name__ == filter_strategy) :
                print(f"\n{player_colors.get(player1.__name__, Fore.RESET)}{player1.__name__[:15].ljust(15)} moves: {''.join([Fore.GREEN+'O'+Style.RESET_ALL if move[0]==COOPERATE else Fore.RED+'X'+Style.RESET_ALL for move in history1])}")
                print(f"{player_colors.get(player2.__name__, Fore.RESET)}{player2.__name__[:15].ljust(15)} moves: {''.join([Fore.GREEN+'O'+Style.RESET_ALL if move[0]==COOPERATE else Fore.RED+'X'+Style.RESET_ALL for move in history2])}")
                print(f"Match scores: {player1.__name__} {match_scores[player1.__name__]}, {player2.__name__} {match_scores[player2.__name__]}")  
                
            # print(f"\n{player_colors.get(player1.__name__, Fore.RESET)}{player1.__name__[:15].ljust(15)} moves: {''.join([Fore.GREEN+'O'+Style.RESET_ALL if move[0]==COOPERATE else Fore.RED+'X'+Style.RESET_ALL for move in history1])}")
            # print(f"{player_colors.get(player2.__name__, Fore.RESET)}{player2.__name__[:15].ljust(15)} moves: {''.join([Fore.GREEN+'O'+Style.RESET_ALL if move[0]==COOPERATE else Fore.RED+'X'+Style.RESET_ALL for move in history2])}")
            # print(f"Match scores: {player1.__name__} {match_scores[player1.__name__]}, {player2.__name__} {match_scores[player2.__name__]}")  
    for player in players:
        print(f'{player.__name__}: {wins[player.__name__]} wins, {losses[player.__name__]} losses, {draws[player.__name__]} draws')

    sorted_scores = sorted(total_scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_scores

# Run the tournament
# for player, score in tournament(players):
#     print(f'\nFinal score: {player}: {score}')

num_tournaments = 1
results = {player.__name__: [] for player in players}

for _ in range(num_tournaments):
    for player, score in tournament(players):
        results[player].append(score)

# Calculate the median score for each player and store them in a list of tuples
medians = [(player, np.mean(scores)) for player, scores in results.items()]

# Sort the list of tuples based on the median score
sorted_medians = sorted(medians, key=lambda x: x[1])

num_players = len(sorted_medians)

# Print the sorted median scores with gradient color
for i, (player, median_score) in enumerate(sorted_medians):
    # Calculate the ratio of green and red based on the player's position
    green_ratio = i / (num_players - 1)
    red_ratio = 1 - green_ratio

    # Calculate the green and red components of the color
    green = int(green_ratio * 255)
    red = int(red_ratio * 255)

    # Create the color code
    color_code = f'\033[38;2;{red};{green};0m'
    player_color = player_colors.get(player, Fore.RESET)
    # Print the player name and median score with the color
    print(f'{player_color}{player}: {median_score} coins')