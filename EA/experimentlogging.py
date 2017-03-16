import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# TODO: fix this ugly shit
def write_log(fitness_list, time_to_complete, matches_per_opponent, opponents, number_of_generations, popsize,
              mutation_rate, crossover_rate):
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
        file.write('\n')
        file.write('Topscore for each generation:\n')
        for fitness in fitness_list:
            file.write(str(fitness) + ', ')
        file.write('\n')


def write_graph(top_list, median_list, worst_list):
    filename = "results.png"
    plt.plot(top_list)
    plt.plot(median_list, 'ro')
    plt.plot(worst_list, 'g^')
    plt.legend(['Strongest', 'Median', 'Worst'], loc='upper left')
    plt.savefig(filename)
