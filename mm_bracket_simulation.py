import numpy as np
from multiprocessing import Pool
import matplotlib.pyplot as plt
import random

import pandas as pd

espn_multipliers = [10, 20, 40, 80, 160, 320]
norm_multipliers = [1, 2, 3, 4, 5, 6]
simp_multipliers = [1, 1, 1, 1, 1, 1]

ROUND_1 = 0
ROUND_2 = 1
ROUND_3 = 2
ROUND_4 = 3
ROUND_5 = 4
ROUND_6 = 5


def select_winner(team_1, team_2):
    return team_1 if random.randint(0, 1) == 0 else team_2


def create_matchups(teams):
    matchups = []
    for idx in range(int(len(teams)/2)):
        team_1 = teams[idx]
        team_2 = teams[idx + int(len(teams) / 2)]
        matchups.append((team_1, team_2))
    return matchups


def generate_random_bracket():
    ret = [
        {'east': [], 'west': [], 'south': [], 'midwest': []},
        {'east': [], 'west': [], 'south': [], 'midwest': []},
        {'east': [], 'west': [], 'south': [], 'midwest': []},
        {'east': [], 'west': [], 'south': [], 'midwest': []},
        {'east': [], 'west': [], 'south': [], 'midwest': []},
        {'east': [], 'west': [], 'south': [], 'midwest': []}
    ]
    for region in ['east', 'west', 'south', 'midwest']:
        for t1, t2 in zip(range(1, 16, 2), range(16, 1, -2)):
            winner = select_winner(t1, t2)
            ret[ROUND_1][region].append(winner)
        for t1, t2 in create_matchups(ret[ROUND_1][region]):
            winner = select_winner(t1, t2)
            ret[ROUND_2][region].append(winner)
        for t1, t2 in create_matchups(ret[ROUND_2][region]):
            winner = select_winner(t1, t2)
            ret[ROUND_3][region].append(winner)
        for t1, t2 in create_matchups(ret[ROUND_3][region]):
            winner = select_winner(t1, t2)
            ret[ROUND_4][region].append(winner)

    east, west = ret[ROUND_4]['east'], ret[ROUND_4]['west']
    ew_winner = select_winner(east, west)
    if ret[ROUND_4]['east'] is ew_winner:
        ret[ROUND_5]['east'] = ret[ROUND_4]['east']
    else:
        ret[ROUND_5]['west'] = ret[ROUND_4]['west']

    south, midwest = ret[ROUND_4]['south'], ret[ROUND_4]['midwest']
    smw_winner = select_winner(south, midwest)
    if ret[ROUND_4]['south'] is smw_winner:
        ret[ROUND_5]['south'] = ret[ROUND_4]['south']
    else:
        ret[ROUND_5]['midwest'] = ret[ROUND_5]['midwest']

    final_winner = select_winner(ew_winner, smw_winner)
    if ret[ROUND_5]['east'] is final_winner:
        ret[ROUND_6]['east'] = final_winner
    elif ret[ROUND_5]['west'] is final_winner:
        ret[ROUND_6]['west'] = final_winner
    elif ret[ROUND_5]['south'] is final_winner:
        ret[ROUND_6]['south'] = final_winner
    elif ret[ROUND_5]['midwest'] is final_winner:
        ret[ROUND_6]['midwest'] = final_winner

    return ret


def score_bracket(correct_bracket, player_bracket, multipliers):
    score = 0
    for bracket_round, results in enumerate(correct_bracket):
        for region in results:
            for seed in player_bracket[bracket_round][region]:
                if seed in results[region]:
                    score += multipliers[bracket_round]
    return score


def simulate_bracket_groups(number_players, multipliers):
    group_scores = []
    correct_bracket = (generate_random_bracket())
    for player in range(number_players):
        player_bracket = (generate_random_bracket())
        group_scores.append(score_bracket(correct_bracket, player_bracket, multipliers))
    return group_scores


def check_tie_freq_group_size(group_size):
    tie_count = 0
    print(f'Starting: {group_size}')
    for _ in range(200):
        scores = simulate_bracket_groups(group_size, espn_multipliers)
        winning_score = max(scores)
        if scores.count(winning_score) > 1:
            tie_count += 1
    print(f'Finished: {group_size}')
    return tie_count


if __name__ == '__main__':
    groups = list(range(2, 500))
    tie_counts = []
    with Pool(14) as p:
        tie_counts = p.map(check_tie_freq_group_size, groups)
    plt.plot(groups, tie_counts)
    plt.title('Occurrence of Ties (ESPN Scoring System)')
    plt.xlabel('Bracket Game Participants')
    plt.ylabel('Number of Ties')
    plt.show()
    pd.DataFrame(data={
        'Number of Participants': groups,
        'Number of Ties': tie_counts}
    ).to_csv('temp.csv', index=False)