import subprocess

import constants as ct
from decks import genome_to_decklist, write_decklist


def build_cmd(candidate_name, opponent_name, nr_matches):
    return ['java', '-Xmx1024m', '-jar',
            'forge-gui-desktop-1.5.61-SNAPSHOT-jar-with-dependencies.jar', 'sim',
            '-d', candidate_name, opponent_name,
            '-n', nr_matches, '-f', 'sealed']


def evaluate_deck_by_wins(data):

    individual = data[0]
    matches_per_opponent = data[1]

    number_of_matches = len(ct.OPPONENTS) * int(matches_per_opponent)

    decklist = genome_to_decklist(individual)
    filename = "candidate.dck"
    write_decklist(ct.CARD_DIRECTORY + filename, decklist)
    wins = 0
    for opponent in ct.OPPONENTS:
        cmd = build_cmd(filename, opponent, matches_per_opponent)
        p = subprocess.Popen(cmd, cwd=ct.FORGE_PATH, stdout=subprocess.PIPE)
        for line in p.stdout:
            line = line.decode("utf-8").strip()
            if 'Match result' in line:
                result = line.split(' ')
        wins += int(result[3])
        p.wait()
    fitness = (wins / float(number_of_matches)) * 100
    return fitness,  # MUST BE TUPLE!