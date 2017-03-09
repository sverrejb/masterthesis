from deap import base
from deap import creator

creator.create("FitnessMax", base.Fitness, weights=(1.0, 1.0))
creator.create("Individual", list, fitness=creator.FitnessMax)

POPSIZE = 10

#LIST OF CARDS
CARD_POOL = []

decks = [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]
         ]


def generate_first_generation_decks(card_pool):


def initIndividual(icls, content):
    return icls(content)


def initPopulation(pcls, ind_init, list_of_decks):
    return pcls(ind_init(c) for c in list_of_decks)


toolbox = base.Toolbox()

toolbox.register("individual_guess", initIndividual, creator.Individual)
toolbox.register("population_guess", initPopulation, list, toolbox.individual_guess, decks)

population = toolbox.population_guess()

print(population)
