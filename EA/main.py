import copy
import os
import time
from random import randint
from statistics import median

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from scoop import futures

import constants as ct
from decks import genome_to_decklist, write_decklist
from fitness import evaluate_deck_by_wins
from logger import log_experiment
from mail import send_mail

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


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


def card_to_genome(card):
    names = [x[0] for x in ct.CARD_POOL.values()]
    card_int = names.index(card)
    print(names)
    return card_int


def continiue_generation():
    decks = []
    for filename in os.listdir("seed"):
        genome = []
        with open("seed/"+filename, 'r') as file:
            lines = [line.strip() for line in file.readlines()]
            deckfile = lines[3:44]
            for card in deckfile:
                genome.append(card_to_genome(card))

        decks.append(genome)
    print(decks)
    return decks


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
    number_of_matches = int(ct.MATCHES_PER_OPPONENT) * len(ct.OPPONENTS) * ct.NUMBER_OF_GENERATIONS * ct.POPSIZE
    print('Starting experiment {}'.format(ct.EXPERIMENT_TIMESTAMP))
    print('Doing {} matches'.format(number_of_matches))

    start_time = time.time()
    first_gen_decks = continiue_generation()

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
    os.makedirs(ct.EXPERIMENT_FOLDER)
    global_maximum = 0
    best_median = 0
    last_improvement = 0
    alpha_deck = []

    for gen in range(ct.NUMBER_OF_GENERATIONS):
        offspring = algorithms.varAnd(population, toolbox, cxpb=ct.CROSSOVER_RATE, mutpb=ct.MUTATION_RATE)
        fits = list(futures.map(toolbox.evaluate, offspring))
        print("Generation {}, {}".format(gen, fits))

        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=len(population))
        card_location = ct.EXPERIMENT_FOLDER + "/" + str(gen)
        os.makedirs(card_location)

        for i, solution in enumerate(population):
            write_decklist(card_location + "/" + str(i) + '.dck', genome_to_decklist(solution))
        fitness_list = [x[0] for x in fits]
        maximum = max(fitness_list)

        strongest_individual = tools.selBest(population, k=1)

        median_score = median(fitness_list)
        if median_score > best_median:
            best_median = median_score
            last_improvement = gen

        if maximum >= global_maximum:
            global_maximum = maximum
            alpha_deck = strongest_individual

        if median_score >= 65:
            break

        if gen - last_improvement > 60:
            break

        top_list.append(maximum)
        median_list.append(median_score)
        worst_list.append(min(fitness_list))

    runtime = (time.time() - start_time)

    top10 = tools.selBest(population, k=10)
    for i in range(len(top10)):
        print(i, top10[i].fitness.values)

    alpha_deck = genome_to_decklist(alpha_deck[0])

    log_experiment(top_list, median_list, worst_list, global_maximum, runtime, alpha_deck)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("Unexpected error:\n{}".format(e))
        send_mail(['sverrejb@stud.ntnu.no', 'knutfludal@gmail.com'], "The program has crashed:\n{}".format(e))
