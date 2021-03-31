import spacy
import re
import json
import sys
import redis
import pickle
import os
from loguru import logger
from collections import Counter
from data.constants import FNAME, RANK, COUNT, PERSON, SENT, ADDITIONAL, TIMES
from data.exceptions import MissingENVVariable

# Here we use os.environ becasue we've passed the .env
# file in the docker-compose.yml
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DATA_NAME = os.environ.get('DATA_NAME')


class DataGenerator:
    """
    Data class that does the same work as the script and the
    notebook, but with the difference that it gets called in
    our app through an api call and populates redis.
    """

    def set_rank(self, collection: dict, min_val: int, max_val: int) -> dict:
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
            collection[entity][RANK] = self.calc_rank(vals[COUNT], min_val, max_val)


    def calc_rank(self, count: int, min_val, max_val) -> int:
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


    def save_collection_to_redis(self, the_collection):
        """
        Connect to redis and save the generated collection
        """
        r = redis.Redis(host=os.environ.get('DB_HOST'), port=os.environ.get('DB_PORT'))
        try:
            r.set(DATA_NAME, pickle.dumps(the_collection))
        except redis.exceptions.ConnectionError as exc:
            logger.warning(f'Redis is not running: Exception: {exc}.')
            sys.exit()


    def generate(self):
        logger.info('Checking requirements...')
        if not all((DB_HOST, DB_PORT, DATA_NAME)):
            raise MissingENVVariable('One of the needed environmental variables is missing.')

        logger.info('Reading file...')
        input_file = open(FNAME, encoding='utf8').readlines()

        logger.info('Preprocessing the file...')
        pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'
        modded = [re.sub(pat, '', x.strip()) for x in input_file]
        modded = [x for x in modded if x != '']
        joined_sentences = ' '.join(modded)

        logger.info('Loadign the sentences into spacy...')
        nlp = spacy.load("en_core_web_sm")
        start_data = nlp(joined_sentences)

        # individual sentences in which we find a given NER
        mentions_sents = dict()

        # all entities, counted and all of the sentences in which they were mentioned
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
                                ADDITIONAL: set(),
                                TIMES: sent_string.count(ent.text)
                            }
                        }
                    }
                else:
                    mentions_sents[
                        ent.text][COUNT] = mentions_sents[ent.text][COUNT] + 1
                    mentions_sents[ent.text][SENT][sent_string] = {
                        ADDITIONAL: set(),
                        TIMES: sent_string.count(ent.text)
                    }

        all_ner = set(
            [ent.text for ent in start_data.ents if ent.label_ == PERSON])

        logger.info('Creating the guest mentions in the sentences...')
        for ner, elements in mentions_sents.items():
            for k, v in elements.get(SENT).items():
                for name in all_ner:
                    if name != ner and name in k:
                        # if we want to add the count as well
                        mentions_sents[ner][SENT][k][ADDITIONAL].add(name)

        # add the counter, get the x most common
        # get the min and max val from it
        items = [x.text for x in start_data.ents if x.label_ == PERSON]
        cter = Counter(items)

        # we'll always have at least one occurence
        min_val = 1
        max_val = cter.most_common(1)[0][1]

        logger.info('Creating the ranks for the entities...')
        self.set_rank(mentions_sents, min_val, max_val)

        logger.info('Updating Redis...')
        self.save_collection_to_redis(mentions_sents)
        logger.info('The data has been written to redis.')

        return True
