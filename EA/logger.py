import datetime
import constants as ct

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def write_log(top_list, median_list, worst_list, global_maximum, time_to_complete, alpha_deck):
    filename = str(datetime.datetime.now()) + '.txt'
    with open('results/' + filename, 'w') as file:
        number_of_matches = int(ct.MATCHES_PER_OPPONENT) * len(ct.OPPONENTS) * ct.NUMBER_OF_GENERATIONS * ct.POPSIZE

        file.write('Experiment log:\n')
        file.write('Mutation rate: {}\n'.format(ct.MUTATION_RATE))
        file.write('Crossover rate: {}\n'.format(ct.CROSSOVER_RATE))
        file.write('Number of generations: {}\n'.format(ct.NUMBER_OF_GENERATIONS))
        file.write('Number of matches pr opponent: {}\n'.format(ct.MATCHES_PER_OPPONENT))
        file.write('Number of opponents: {}\n'.format(len(ct.OPPONENTS)))
        file.write('Opponents: {}\n'.format(str(ct.OPPONENTS)))
        file.write('Total number of matches: {}\n'.format(number_of_matches))
        file.write('Time to complete: {}\n'.format(time_to_complete))
        file.write('Avg time per match: {}\n'.format(time_to_complete / number_of_matches))
        file.write('Strongest overall individual: {}\n'.format(global_maximum))
        file.write('Topscore for each generation:\n')
        for fitness in top_list:
            file.write(str(fitness) + ', ')
        file.write('\n')
        file.write('Median score for each generation:\n')
        for fitness in median_list:
            file.write(str(fitness) + ', ')
        file.write('\n')
        file.write('Worst score for each generation: \n')
        for fitness in worst_list:
            file.write(str(fitness) + ', ')
        file.write('\nOverall best deck: \n')
        for card in alpha_deck:
            file.write("{}\n".format(card))


def write_graph(top_list, median_list, worst_list):
    timestamp = datetime.datetime.now().strftime("%d%m%H%M")
    filename = "{}.png".format(timestamp)
    plt.plot(top_list, 'blue')
    plt.plot(median_list, 'green')
    plt.plot(worst_list, 'red')
    plt.legend(['Strongest', 'Median', 'Worst'], loc='upper left')
    plt.savefig(filename)
