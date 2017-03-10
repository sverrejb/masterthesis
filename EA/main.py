from random import randint

import multiprocessing

from cards import read_card_pool
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import time

import subprocess

from pprint import pprint

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

POPSIZE = 10
DECKSIZE = 40
CARD_POOL = read_card_pool('../AER-POOL-1.txt')
CARD_POOL_SIZE = len(CARD_POOL)
CARD_DIRECTORY = '/Users/sverre/Library/Application Support/Forge/decks/constructed/'


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
    print(individual)
    size = len(individual)
    mutation_site = randint(0, size)
    mutated = False
    while not mutated:
        new_gene = randint(0, CARD_POOL_SIZE)
        gene_limit = CARD_POOL[new_gene][1]
        if individual.count(new_gene) < gene_limit:
            individual[mutation_site] = new_gene
            mutated = True
    print(individual)
    return individual,  # MUST RETURN TUPLE


def build_cmd(candidate_name, opponent_name):
    return ['java', '-Xmx1024m', '-jar',
            'forge-gui-desktop-1.5.61-SNAPSHOT-jar-with-dependencies.jar', 'sim',
            '-d', candidate_name, opponent_name,
            '-n', '80', '-f', 'sealed', '-q']


def evaluate_decks(offspring):
    start = time.time()
    jobs = []
    pipe_list = []
    for i in range(len(offspring)):
        individual = offspring[i]
        recv_end, send_end = multiprocessing.Pipe(False)
        p = multiprocessing.Process(target=evaluate_deck, args=(individual, i, send_end))
        jobs.append(p)
        pipe_list.append(recv_end)
        p.start()

    for proc in jobs:
        proc.join()
    result_list = [x.recv() for x in pipe_list]
    print(result_list)
    print(time.time() - start)
    return [(0,), (0,), (0,), (0,), (0,), (0,), (0,), (0,), (0,), (0,)]


def evaluate_deck(individual, num, send_end):
    decklist = genome_to_decklist(individual)
    filename = str(num)+'candidate.dck'
    opponent = 'Merfolk.dck'
    with open(CARD_DIRECTORY+filename, 'w') as file:
        file.write('[metadata]\nName=candidate\n[Main]\n')
        for card in decklist:
            file.write(card+'\n')

    cmd = build_cmd(filename, opponent)

    p = subprocess.Popen(cmd, cwd='/Users/sverre/workspace/masteroppgave/forgeGUI', stdout=subprocess.PIPE)
    for line in p.stdout:
        line = line.decode("utf-8").strip()
        if 'Match result' in line:
            result = line.split(' ')
    p.wait()
    fitness = int(result[3])
    send_end.send(fitness)
    return


def init_individual(icls, content):
    return icls(content)


def init_population(pcls, ind_init, list_of_decks):
    return pcls(ind_init(c) for c in list_of_decks)


first_gen_decks = generate_first_generation_decks(CARD_POOL)

toolbox = base.Toolbox()

toolbox.register("individual_guess", init_individual, creator.Individual)
toolbox.register("card_population", init_population, list, toolbox.individual_guess, first_gen_decks)




toolbox.register("evaluate", evaluate_decks)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutate_deck)
toolbox.register("select", tools.selTournament, tournsize=3)


NUMBER_OF_GENERATIONS = 100

# TODO: VELG BREEDING OG MUTASJONSSTRATEGI

population = toolbox.card_population()

print(evaluate_decks(population))

# for gen in range(NUMBER_OF_GENERATIONS):
#     offspring = algorithms.varAnd(population, toolbox, cxpb=0.0, mutpb=0.5)
#     fits = toolbox.evaluate(offspring)
#     print(list(fits))
#     for fit, ind in zip(fits, offspring):
#         ind.fitness.values = fit
#     population = toolbox.select(offspring, k=len(population))
#
# top10 = tools.selBest(population, k=10)
# for individual in top10:
#     print(individual)