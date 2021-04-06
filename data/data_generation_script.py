import argparse
import spacy
import re
import json
import sys
import redis
import pickle
import os
from loguru import logger
from collections import Counter
from constants import FNAME, RANK, COUNT, PERSON, SENT, ADDITIONAL, TIMES, DB_HOST, DB_PORT, DATA_NAME, DATA_FILE_JSON, DATA_FILE_PICKLE
from exceptions import MissingENVVariable

DESCRIPTION = """
This script generates the data in the specified format.
It does that by reading a txt file performing some data cleaning.
Then loading it to spacy, extracting the NER of type PERSON.
Then we create the data skeleton.
Then handling the guest mentions.
Then setting the rank per entity.
In the end we persist the data in a file.
"""

arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
arg_parser.add_argument('--save_to_pickle',
                        default=False,
                        help='Save the generated data in a pickle file.')
arg_parser.add_argument('--save_to_json',
                        default=False,
                        help='Save the generated data in a json file.')
arg_parser.add_argument('--save_to_redis',
                        default=False,
                        help='Save the generated data in a json file.')
arg_parser.add_argument(
    '--verbose',
    default=False,
    help='Display the end result data after the transfromation')


def set_rank(collection: dict, min_val: int, max_val: int) -> dict:
    """
    Mutate the collection to set their rank
    Parametes:
        collection dict: the data collection
        min_val int: the current minimum
        max_val int: the current maximum
    Returns:
    the modded collection in place
    """
    for entity, vals in collection.items():
        collection[entity][RANK] = calc_rank(vals[COUNT], min_val, max_val)


def calc_rank(count: int, min_val, max_val) -> int:
    """
    Calculate the rank based on the current min/max counts
    Parametes:
        count dict: the current entitys occurences
        min_val int: the current minimum
        max_val int: the current maximum
    Returns:
    the calculated rank
    """
    percentage = ((count - min_val) * 100) / (max_val - min_val)

    if percentage <= 33:
        return 3
    elif percentage > 33 and percentage <= 66:
        return 2
    else:
        return 1


def save_collection_to_redis(the_collection: dict):
    """
    Connect to redis and save the generated collection
    """
    r = redis.Redis(host=DB_HOST, port=DB_PORT)
    try:
        r.set(DATA_NAME, pickle.dumps(the_collection))
    except redis.exceptions.ConnectionError as exc:
        logger.warning(f'Redis is not running: Exception: {exc}.')
        sys.exit()


def save_to_file(the_collection: dict, f_type: str):
    pass


def main():
    args = arg_parser.parse_args()

    logger.info('Checking requirements...')
    # if passed through the .env file
    if not all((DB_HOST, DB_PORT, DATA_NAME)):
        raise MissingENVVariable(
            'One of the needed environmental variables is missing.')

    logger.info('Reading file...')
    input_file = open(FNAME, encoding='utf8').readlines()

    # we replace all the unwanted symbols (@, #, $) and clean the text
    logger.info('Preprocessing the file...')
    pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'
    modded = [re.sub(pat, '', x.strip()) for x in input_file]
    modded = [x for x in modded if x != '']
    joined_sentences = ' '.join(modded)

    # load the cleaned sentences in spacy
    logger.info('Loading the sentences into spacy...')
    nlp = spacy.load("en_core_web_sm")
    start_data = nlp(joined_sentences)

    # individual sentences in which we find a given NE record
    # sents = [ent.sent for ent in start_data.ents if ent.text == 'Dante']
    # print(len(sents))

    mentions_sents = dict()

    # all entities, counted and all of the sentences in which they were mentioned
    # create the initial data schema for the entities of type PERSON
    # that we will at some point persist in a databased
    logger.info('Restructuring the data collection per NER for each PERSON...')
    visited = []
    for ent in start_data.ents:
        if ent.label_ == PERSON:
            sent_string = str(ent.sent)
            if ent.text not in visited:
                visited.append(ent.text)
                mentions_sents[ent.text] = {
                    COUNT: 1,
                    SENT: {
                        sent_string: {
                            ADDITIONAL: [],
                            TIMES: sent_string.count(ent.text)
                        }
                    }
                }
            else:
                mentions_sents[
                    ent.text][COUNT] = mentions_sents[ent.text][COUNT] + 1
                mentions_sents[ent.text][SENT][sent_string] = {
                    ADDITIONAL: [],
                    TIMES: sent_string.count(ent.text)
                }
    # Create a set of all the entities for the lookup below
    all_ner = set(
        [ent.text for ent in start_data.ents if ent.label_ == PERSON])

    # This is making me a little bit sick (tripple nested loops)
    # maybe implement it with generators to be faster or at least to look better
    logger.info('Creating the guest mentions in theentences...')
    for ner, elements in mentions_sents.items():
        for k, v in elements.get(SENT).items():
            for name in all_ner:
                if name != ner and name in k:
                    # if we want to add the count as well
                    mentions_sents[ner][SENT][k][ADDITIONAL].append(name)

    # add the counter, get the x most common
    # get the min and max val from it
    # we create a counter object to use the most_common method to get the entity with highest count
    items = [x.text for x in start_data.ents if x.label_ == PERSON]
    cter = Counter(items)

    # we'll always have at least one occurence
    min_val = 1
    max_val = cter.most_common(1)[0][1]

    logger.info('Creating the ranks for the entities...')
    set_rank(mentions_sents, min_val, max_val)

    # represent the entities from the data
    if args.verbose:
        for entity in mentions_sents:
            print(
                f"Name: {entity} --> Count: {mentions_sents[entity]['count']} --> Rank: {mentions_sents[entity]['rank']}"
            )

    logger.info('Saving the generated data in the desired format...')
    # Depending on the arguments we pass to the script execute it accordignly
    if args.save_to_json:
        with open(DATA_FILE_JSON, 'w') as f:
            json.dump(mentions_sents, f)
        logger.info(
            f'Successfully saved the data to a json file: {DATA_FILE_JSON}.')
    elif args.save_to_pickle:
        with open(DATA_FILE_PICKLE, 'wb') as f:
            pickle.dump(mentions_sents, f)
        logger.info(
            f'Successfully saved the data to a pickle file: {DATA_FILE_PICKLE}.'
        )
    elif args.save_to_redis:
        save_collection_to_redis(mentions_sents)
        logger.info('Successfully saved the data to redis.')
    else:
        logger.info("The script didn't write the results in any form.")


if __name__ == '__main__':
    main()
