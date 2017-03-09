from random import randint

from cards import read_card_pool
from deap import base
from deap import creator
from deap import tools
from deap import algorithms

from pprint import pprint

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

POPSIZE = 10
DECKSIZE = 40
CARD_POOL = {}
CARD_POOL = read_card_pool('../AER-POOL-1.txt')


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


# must return fitness value as tuple eg. (31, )
def evaluate_deck(individual):
    return (sum(individual), )


def initIndividual(icls, content):
    return icls(content)


def initPopulation(pcls, ind_init, list_of_decks):
    return pcls(ind_init(c) for c in list_of_decks)


first_gen_decks = generate_first_generation_decks(CARD_POOL)

toolbox = base.Toolbox()

toolbox.register("individual_guess", initIndividual, creator.Individual)
toolbox.register("population_guess", initPopulation, list, toolbox.individual_guess, first_gen_decks)

population = toolbox.population_guess()


toolbox.register("evaluate", evaluate_deck)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)



NGEN = 1000
for gen in range(NGEN):
    offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=1)
    fits = toolbox.map(toolbox.evaluate, offspring)
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
    population = toolbox.select(offspring, k=len(population))

top10 = tools.selBest(population, k=10)
for individual in top10:
    print(individual)