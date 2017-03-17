import datetime

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


# TODO: fix this ugly shit
def write_log(top_list, median_list, worst_list, global_maximum, time_to_complete, matches_per_opponent, opponents,
              number_of_generations, popsize,
              mutation_rate, crossover_rate, alpha_deck):
    filename = str(datetime.datetime.now()) + '.txt'
    with open('results/' + filename, 'w') as file:
        number_of_matches = int(matches_per_opponent) * len(opponents) * number_of_generations * popsize

        file.write('Experiment log:\n')
        file.write('Mutation rate: {}\n'.format(mutation_rate))
        file.write('Crossover rate: {}\n'.format(crossover_rate))
        file.write('Number of generations: {}\n'.format(number_of_generations))
        file.write('Number of matches pr opponent: {}\n'.format(matches_per_opponent))
        file.write('Number of opponents: {}\n'.format(len(opponents)))
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
