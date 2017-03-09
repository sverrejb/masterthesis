from deap import base
from deap import creator

creator.create("FitnessMax", base.Fitness, weights=(1.0, 1.0))
creator.create("Individual", list, fitness=creator.FitnessMax)

POPSIZE = 10
CARD_POOL = []

decks = [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]
         ]


with open('../AER-POOL-1.txt', 'r') as file:
    card_list = []
    for line in file:
        card_list.append(line.strip())

for card in card_list:
    card = card.split(' ')
    number_of_card = int(card[0])
    name_of_card = " ".join(card[1:])
    for i in range(number_of_card):
        CARD_POOL.append(name_of_card)

for card in CARD_POOL:
    print(card)


def generate_first_generation_decks(card_pool):
    pass


def initIndividual(icls, content):
    return icls(content)


def initPopulation(pcls, ind_init, list_of_decks):
    return pcls(ind_init(c) for c in list_of_decks)


toolbox = base.Toolbox()

toolbox.register("individual_guess", initIndividual, creator.Individual)
toolbox.register("population_guess", initPopulation, list, toolbox.individual_guess, decks)

population = toolbox.population_guess()

print(population)
