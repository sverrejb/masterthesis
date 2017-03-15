import copy
import subprocess
import time
import os
from random import randint

from deap import algorithms
from deap import base
from deap import creator

import datetime
from deap import tools

import config
from cards import read_card_pool
from read_json import read_cards_json

import matplotlib.pyplot as plt


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

POPSIZE = 10
DECKSIZE = 40
NUMBER_OF_GENERATIONS = 10
MATCHES_PER_OPPONENT = '10'
CARD_POOL = read_card_pool('../AER-POOL-1.txt')
CARD_POOL_SIZE = len(CARD_POOL)
CARD_DIRECTORY = config.CARD_DIR
FORGE_PATH = config.FORGE_DIR
DECKLIST_HEADER = '[metadata]\nName=candidate\n[Main]\n'
EXPERIMENT_FOLDER = str(datetime.datetime.now()).replace(":","-")
gen = 0
card_location = ""
CARDS = read_cards_json


def color_symbols(cardName):
    colors=[CARDS[cardName['manaColor'].count('W')],
            CARDS[cardName['manaColor'].count('U')],
            CARDS[cardName['manaColor'].count('B')],
            CARDS[cardName['manaColor'].count('R')],
            CARDS[cardName['manaColor'].count('G')]] #WUBRG
    return colors


def land_symbols(cardName):
    colors=[CARDS[cardName['colorIdentity'].count('W')],
            CARDS[cardName['colorIdentity'].count('U')],
            CARDS[cardName['colorIdentity'].count('B')],
            CARDS[cardName['colorIdentity'].count('R')],
            CARDS[cardName['colorIdentity'].count('G')]] #WUBRG
    return colors


def colorsymbols_in_deck(decklist):
    colors = [0, 0, 0, 0, 0]
    lands = [0, 0, 0, 0, 0]
    for card in decklist:
        if is_land(card):
            lands = list(map(sum, lands, land_symbols(card)))
        else:
            colors = list(map(sum, colors, color_symbols(card)))
    return lands, colors


def is_land(cardName):
    return 'manaColor' in CARDS[cardName]


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

def write_decklist(filename, decklist):
    with open(CARD_DIRECTORY + "\\" +filename, 'w') as file:
        file.write(DECKLIST_HEADER)
        for card in decklist:
            file.write(card + '\n')

def evaluate_deck_by_damage(individual):
    decklist = genome_to_decklist(individual)
    filename = card_location + "\\" + str(time.time()).replace(".","")+'.dck'
    write_decklist(filename, decklist)
    opponents = ["GB-sealed-opponent.dck", "UWg-sealed-opponent.dck"]
    total_damage = 0
    wins = 0


    for opponent in opponents:
        cmd = build_cmd(filename, opponent, MATCHES_PER_OPPONENT)
        p = subprocess.Popen(cmd, cwd=FORGE_PATH, stdout=subprocess.PIPE)
        for line in p.stdout:
            line = line.decode("utf-8").strip()
            if 'combat damage to Ai(2' in line:
                hit_event = line.split(' ')
                #print(hit_event) #For debugging
                damage_index = hit_event.index('deals') + 1
                damage = int(hit_event[damage_index])
                total_damage += damage
            if 'Match result' in line:
                result = line.split(' ')
                wins += int(result[3])

        p.wait()
        fitness = (wins+1) * total_damage   #(wins/float(MATCHES_PER_OPPONENT*len(opponents)))*damage
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


first_gen_decks = generate_first_generation_decks(CARD_POOL)

toolbox = base.Toolbox()

toolbox.register("individual_deck", init_individual, creator.Individual)
toolbox.register("card_population", init_population, list, toolbox.individual_deck, first_gen_decks)

toolbox.register("evaluate", evaluate_deck_by_damage)
toolbox.register("mate", mate_individuals)
toolbox.register("mutate", mutate_deck)
toolbox.register("select", tools.selTournament, tournsize=3)

population = toolbox.card_population()
start_time = time.time()

top1_list = []
os.makedirs(CARD_DIRECTORY + "\\" + EXPERIMENT_FOLDER)
for gen in range(NUMBER_OF_GENERATIONS):
    card_location = EXPERIMENT_FOLDER + "\\" + str(gen)
    os.makedirs(CARD_DIRECTORY + "\\" +card_location)
    offspring = algorithms.varAnd(population, toolbox, cxpb=0.1, mutpb=0.7)
    fits = list(toolbox.map(toolbox.evaluate, offspring))
    print(list(fits))
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
    population = toolbox.select(offspring, k=len(population))
    top1 = tools.selBest(population, k=1)
    top1_list.append(top1)

top10 = tools.selBest(population, k=10)
for i in range(len(top10)):
    print(i, top10[i].fitness.values)

print(time.time() - start_time)

fitness_list = []
for generation in top1_list:
    for ind in generation:
        fitness_list.append(ind.fitness.values)
print(fitness_list)
print(type(fitness_list[0]))

image_name = str(time.time()) + '.png'

plt.plot([x[0] for x in fitness_list])
plt.ylabel('some numbers')
plt.savefig(image_name)

