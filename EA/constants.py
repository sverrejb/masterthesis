import datetime
import config
from cards import read_card_pool
from read_json import read_cards_json

POPSIZE = 10
DECKSIZE = 40
CROSSOVER_RATE = 0.1
MUTATION_RATE = 0.2
NUMBER_OF_GENERATIONS = 20
MATCHES_PER_OPPONENT = '50'  # must be string!
CARD_POOL = read_card_pool('../AER-POOL-1.txt')
CARD_POOL_SIZE = len(CARD_POOL)
CARD_DIRECTORY = config.CARD_DIR
FORGE_PATH = config.FORGE_DIR
DECKLIST_HEADER = '[metadata]\nName=candidate\n[Main]\n'
OPPONENTS = ["GB-sealed-opponent.dck", "UWg-sealed-opponent.dck", "RG-sealed-opponent1.dck",
             "BGw-sealed-opponent.dck", "UR-sealed-opponent.dck", "RW-sealed-opponent.dck"]
EXPERIMENT_TIMESTAMP = datetime.datetime.now().strftime("%d%m%H%M")
EXPERIMENT_FOLDER = "results/" + EXPERIMENT_TIMESTAMP
TERMINATION_TRESHOLD = 65
# CARDS = read_cards_json()
