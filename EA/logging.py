def write_log(fitness_list, time_to_complete):
    with open('result.txt', 'w') as file:
        number_of_matches = int(MATCHES_PER_OPPONENT) * len(OPPONENTS) * NUMBER_OF_GENERATIONS * POPSIZE

        file.write("Experiment log:\n")
        file.write("Mutation rate: {}\n".format(MUTATION_RATE))
        file.write("Crossover rate: {}\n".format(CROSSOVER_RATE))
        file.write("Number of generations: {}\n".format(NUMBER_OF_GENERATIONS))
        file.write("Number of matches pr opponent: {}\n".format(MATCHES_PER_OPPONENT))
        file.write("Number of opponents: {}\n".format(len(OPPONENTS)))
        file.write("Total number of matches: {}\n".format(number_of_matches))
        file.write('Time to complete: {}\n'.format(time_to_complete))
        file.write('Avg time per match: {}\n'.format(time_to_complete/number_of_matches))
        file.write('\n')
        file.write('Topscore for each generation:\n')
        for fitness in fitness_list:
            file.write(str(fitness) + ', ')
        file.write('\n')