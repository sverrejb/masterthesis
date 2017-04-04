import subprocess

import constants as ct
from decks import genome_to_decklist, write_decklist


def build_cmd(candidate_name, opponent_name, nr_matches):
    return ['java', '-Xmx1024m', '-jar',
            'forge-gui-desktop-1.5.61-SNAPSHOT-jar-with-dependencies.jar', 'sim',
            '-d', candidate_name, opponent_name,
            '-n', nr_matches, '-f', 'sealed']


def evaluate_deck_by_wins(individual):
    number_of_matches = len(ct.OPPONENTS) * int(ct.MATCHES_PER_OPPONENT)
    decklist = genome_to_decklist(individual)
    filename = "candidate.dck"
    write_decklist(ct.CARD_DIRECTORY + filename, decklist)
    wins = [0]*len(ct.OPPONENTS)
    for counter, opponent in enumerate(ct.OPPONENTS):
        cmd = build_cmd(filename, opponent, ct.MATCHES_PER_OPPONENT)
        p = subprocess.Popen(cmd, cwd=ct.FORGE_PATH, stdout=subprocess.PIPE)
        for line in p.stdout:
            line = line.decode("utf-8").strip()
            if 'Match result' in line:
                result = line.split(' ')
        wins[counter] += int(result[3])
        p.wait()
    for i in range(len(ct.OPPONENTS)):
        wins[i] = (wins[i] / float(number_of_matches)) * 100
    wins = [round(x, 2) for x in wins]
    return tuple(wins)  # MUST BE TUPLE!
