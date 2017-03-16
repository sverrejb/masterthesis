import copy
import subprocess
import time
from random import randint

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from scoop import futures

import config
from cards import read_card_pool
from experimentlogging import write_log, write_graph


POPSIZE = 10
DECKSIZE = 40
CROSSOVER_RATE = 0.1
MUTATION_RATE = 0.2
NUMBER_OF_GENERATIONS = 2
MATCHES_PER_OPPONENT = '1'  # must be string!
CARD_POOL = read_card_pool('../AER-POOL-1.txt')
CARD_POOL_SIZE = len(CARD_POOL)
CARD_DIRECTORY = config.CARD_DIR
FORGE_PATH = config.FORGE_DIR
DECKLIST_HEADER = '[metadata]\nName=candidate\n[Main]\n'
OPPONENTS = ["GB-sealed-opponent.dck", "UWg-sealed-opponent.dck"]

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


def genome_to_decklist(individual):
    deck_list = []
    for c in individual:
        deck_list.append(CARD_POOL[c][0])
    return deck_list


def generate_individual(card_pool):
    individual = []
    card_pool_size = len(card_pool)
    while len(individual) < 40:
        genome = randint(0, card_pool_size - 1)
        number_of_genome_present = individual.count(genome)
        if number_of_genome_present < card_pool[genome][1]:
            individual.append(genome)
    return individual


def generate_first_generation_decks(card_pool):
    population = []
    for i in range(POPSIZE):
        population.append(generate_individual(card_pool))
    return population


def mutate_deck(individual):
    size = len(individual)
    mutation_site = randint(0, size - 1)
    mutated = False
    while not mutated:
        new_gene = randint(0, CARD_POOL_SIZE - 1)
        gene_limit = CARD_POOL[new_gene][1]
        if individual.count(new_gene) < gene_limit:
            individual[mutation_site] = new_gene
            mutated = True
    return individual,  # MUST RETURN TUPLE


def build_cmd(candidate_name, opponent_name, nr_matches):
    return ['java', '-Xmx1024m', '-jar',
            'forge-gui-desktop-1.5.61-SNAPSHOT-jar-with-dependencies.jar', 'sim',
            '-d', candidate_name, opponent_name,
            '-n', nr_matches, '-f', 'sealed']


def evaluate_deck_by_damage(individual):
    decklist = genome_to_decklist(individual)
    filename = 'candidate.dck'
    total_damage = 0
    wins = 0
    for opponent in OPPONENTS:
        with open(CARD_DIRECTORY + filename, 'w') as file:
            file.write(DECKLIST_HEADER)
            for card in decklist:
                file.write(card + '\n')
        cmd = build_cmd(filename, opponent, MATCHES_PER_OPPONENT)
        p = subprocess.Popen(cmd, cwd=FORGE_PATH, stdout=subprocess.PIPE)
        for line in p.stdout:
            line = line.decode("utf-8").strip()
            if 'combat damage to Ai(2' in line:
                hit_event = line.split(' ')
                # print(hit_event) #For debugging
                damage_index = hit_event.index('deals') + 1
                damage = int(hit_event[damage_index])
                total_damage += damage
            if 'Match result' in line:
                result = line.split(' ')
                wins += int(result[3])
        p.wait()
        fitness = wins * total_damage  # (wins/float(MATCHES_PER_OPPONENT*len(opponents)))*damage
    return fitness,  # MUST BE TUPLE!


def evaluate_deck_by_wins(individual):
    decklist = genome_to_decklist(individual)
    filename = 'candidate.dck'
    fitness = 0
    for opponent in OPPONENTS:
        with open(CARD_DIRECTORY + filename, 'w') as file:
            file.write(DECKLIST_HEADER)
            for card in decklist:
                file.write(card + '\n')
        cmd = build_cmd(filename, opponent, MATCHES_PER_OPPONENT)
        p = subprocess.Popen(cmd, cwd=FORGE_PATH, stdout=subprocess.PIPE)
        for line in p.stdout:
            line = line.decode("utf-8").strip()
            if 'Match result' in line:
                result = line.split(' ')
        p.wait()
        fitness += int(result[3])
    return fitness,  # MUST BE TUPLE!


def init_individual(icls, content):
    return icls(content)


def init_population(pcls, ind_init, list_of_decks):
    return pcls(ind_init(c) for c in list_of_decks)


def mate_individuals(ind1, ind2):
    templist = sorted(copy.deepcopy(ind1) + copy.deepcopy(ind2))
    list_ind1 = templist[0::2]
    list_ind2 = templist[1::2]
    for i in range(len(list_ind1)):
        ind1[i], ind2[i] = list_ind1[i], list_ind2[i]
    return ind1, ind2


def main():
    # TODO: VELG BREEDING OG MUTASJONSSTRATEGI
    # TODO: VURDER fitnessfunksjon til å returnere skade på motstander, evt antall hits på motstander

    start_time = time.time()

    first_gen_decks = generate_first_generation_decks(CARD_POOL)

    toolbox = base.Toolbox()
    toolbox.register("individual_deck", init_individual, creator.Individual)
    toolbox.register("card_population", init_population, list, toolbox.individual_deck, first_gen_decks)
    toolbox.register("evaluate", evaluate_deck_by_wins)
    toolbox.register("mate", mate_individuals)
    toolbox.register("mutate", mutate_deck)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.card_population()
    top1_list = []

    for gen in range(NUMBER_OF_GENERATIONS):
        offspring = algorithms.varAnd(population, toolbox, cxpb=CROSSOVER_RATE, mutpb=MUTATION_RATE)
        fits = list(futures.map(toolbox.evaluate, offspring))
        print(list(fits))
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=len(population))
        top1 = tools.selBest(population, k=1)
        top1_list.append(top1)

    top10 = tools.selBest(population, k=10)
    for i in range(len(top10)):
        print(i, top10[i].fitness.values)

    fitness_list = []
    for generation in top1_list:
        for ind in generation:
            fitness_list.append(ind.fitness.values)

    fitness_list = [x[0] for x in fitness_list]
    time_to_complete = (time.time() - start_time)


    # TODO: FIX THIS UGLY SHIT
    write_log(fitness_list, time_to_complete, MATCHES_PER_OPPONENT, OPPONENTS, NUMBER_OF_GENERATIONS, POPSIZE,
              MUTATION_RATE, CROSSOVER_RATE)

    write_graph(fitness_list)


if __name__ == '__main__':
    main()
