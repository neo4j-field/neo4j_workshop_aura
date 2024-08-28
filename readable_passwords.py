import time
import random
import argparse
import logging

import pandas as pd
from os import path

from graphdatascience import GraphDataScience

logger = logging.getLogger(__name__)
logging.basicConfig(level='INFO')


word_list = [
    'apple', 'banana', 'orange', 'strawberry', 'grape', 'kiwi', 'pineapple', 'watermelon',
    'blueberry', 'mango', 'pepper', 'onion', 'garlic', 'lizard', 'garage','sandwich', 'essay',
    'carrot', 'potato', 'broccoli', 'spinach', 'lettuce', 'cucumber', 'tomato','pasta', 'sea',
    'dog', 'cat', 'rabbit', 'hamster', 'hedgehog', 'bird', 'fish', 'turtle', 'snake', 'truck',
    'sun', 'moon', 'star', 'sky', 'cloud', 'rain', 'snow', 'wind', 'storm', 'thunder', 'fern',
    'tree', 'flower', 'grass', 'leaf', 'branch', 'root', 'bark', 'twig', 'mushroom', 'dining',
    'mountain', 'hill', 'valley', 'canyon', 'river', 'stream', 'lake', 'pond', 'ocean',
    'sand', 'rock', 'stone', 'pebble', 'dirt', 'mud', 'clay', 'silt', 'sandstone', 'granite',
    'house', 'apartment', 'building', 'room', 'kitchen', 'bathroom', 'bedroom', 'parlor',
    'car', 'bicycle', 'bus', 'train', 'boat', 'plane', 'helicopter', 'rocket', 'motorcycle',
    'book', 'magazine', 'newspaper', 'journal', 'diary', 'notebook', 'novel', 'poem', 'story'
]


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help="filename of csv with passwords")
    return parser.parse_args()


def generate_passphrase(self, word_list=word_list, min_words=2, max_words=3, separator='-'):
    num_words = random.randint(min_words, max_words)
    passphrase = random.sample(list(word_list), num_words)
    return separator.join(passphrase)


def create_passwords(filename):
    df = pd.read_csv(filename, dtype=object)
    df['readablechunk'] = df.apply(generate_passphrase, axis=1)
    df['newpassword'] = df['id'] + '-' + df['readablechunk']
    nameroot = path.splitext(filename)[0]
    df.to_csv(nameroot + '_readable_pw.csv', index=False)


def update_passwords(filename):
    nameroot = path.splitext(filename)[0]
    df = pd.read_csv(nameroot + '_readable_pw.csv', dtype=object)

    NEO4J_USERNAME = 'neo4j'
    AURA_DS = True
    for ix, irow in df.iterrows():
        NEO4J_URI = irow['connection_url']
        NEO4J_PASSWORD = irow['password']
        NEW_PW = irow['newpassword']

        gds = GraphDataScience(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
            aura_ds=AURA_DS)

        gds.set_database("system")

        gds.run_cypher(f'''
                    ALTER CURRENT USER SET PASSWORD FROM '{NEO4J_PASSWORD}' TO '{NEW_PW}';
                   ''')


if __name__ == '__main__':
    args = cli()
    filename = args.filename

    pw_start = time.time()
    create_passwords(filename)
    logger.info("Time to create passwords: {}s".format(time.time()-pw_start))

    update_start = time.time()
    update_passwords(filename)
    logger.info("Time to update passwords: {}s".format(time.time()-update_start))
    