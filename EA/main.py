import copy
import os
import subprocess
import time
from random import randint
from statistics import median

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from scoop import futures

import constants as ct
from experimentlogging import write_log, write_graph

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


def genome_to_decklist(individual):
    deck_list = []
    for c in individual:
        deck_list.append(ct.CARD_POOL[c][0])
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
    for i in range(ct.POPSIZE):
        population.append(generate_individual(card_pool))
    return population


def mutate_deck(individual):
    size = len(individual)
    mutation_site = randint(0, size - 1)
    mutated = False
    while not mutated:
        new_gene = randint(0, ct.CARD_POOL_SIZE - 1)
        gene_limit = ct.CARD_POOL[new_gene][1]
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
    with open(filename, 'w') as file:
        file.write(ct.DECKLIST_HEADER)
        for card in decklist:
            file.write(card + '\n')


def evaluate_deck_by_wins(individual):
    decklist = genome_to_decklist(individual)
    filename = "candidate.dck"  # card_location + "\\" + str(time.time()).replace(".","")+'.dck'
    write_decklist(filename, decklist)
    total_damage = 0
    wins = 0
    # colors,lands = colorsymbols_in_deck(CARDS, decklist)

    for opponent in ct.OPPONENTS:
        cmd = build_cmd(filename, opponent, ct.MATCHES_PER_OPPONENT)
        p = subprocess.Popen(cmd, cwd=ct.FORGE_PATH, stdout=subprocess.PIPE)
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
        fitness = wins  # (wins/float(MATCHES_PER_OPPONENT*len(opponents)))*damage
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

    first_gen_decks = generate_first_generation_decks(ct.CARD_POOL)

    toolbox = base.Toolbox()
    toolbox.register("individual_deck", init_individual, creator.Individual)
    toolbox.register("card_population", init_population, list, toolbox.individual_deck, first_gen_decks)
    toolbox.register("evaluate", evaluate_deck_by_wins)
    toolbox.register("mate", mate_individuals)
    toolbox.register("mutate", mutate_deck)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.card_population()
    top_list = []
    median_list = []
    worst_list = []
    os.makedirs(ct.CARD_DIRECTORY + "\\" + ct.EXPERIMENT_FOLDER)
    global_maximum = -10.0
    alpha_deck = []

    for gen in range(ct.NUMBER_OF_GENERATIONS):
        offspring = algorithms.varAnd(population, toolbox, cxpb=ct.CROSSOVER_RATE, mutpb=ct.MUTATION_RATE)
        fits = list(futures.map(toolbox.evaluate, offspring))
        print(fits)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=len(population))
        card_location = ct.CARD_DIRECTORY + "\\" + ct.EXPERIMENT_FOLDER + "\\" + str(gen)
        os.makedirs(card_location)

        counter = 0
        for solution in population:  # TODO: use enumerate()?
            write_decklist(card_location + "\\" + str(counter) + '.dck', genome_to_decklist(solution))
            counter += 1
        fitness_list = [x[0] for x in fits]
        maximum = max(fitness_list)

        strongest_individual = tools.selBest(population, k=1)

        if maximum > global_maximum:
            global_maximum = maximum
            alpha_deck = strongest_individual

        top_list.append(maximum)
        median_list.append(median(fitness_list))
        worst_list.append(min(fitness_list))

    time_to_complete = (time.time() - start_time)

    top10 = tools.selBest(population, k=10)
    for i in range(len(top10)):
        print(i, top10[i].fitness.values)

    alpha_deck = genome_to_decklist(alpha_deck[0])

    # TODO: FIX THIS UGLY SHIT
    write_log(top_list, median_list, worst_list, global_maximum, time_to_complete, alpha_deck)

    write_graph(top_list, median_list, worst_list)


if __name__ == '__main__':
    main()
