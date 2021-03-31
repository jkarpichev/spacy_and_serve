import redis
import pickle
import os
import jsonschema
import json
from loguru import logger
from data.resources.the_data_schema import the_schema


class DataHandler:
    """
    The data connection class.
    We initially try to establish
    """
    def __init__(self):
        self.data = self.connect_to_redis()

    def get_data(self):
        if not self.data:
            self.data = self.connect_to_redis()
        return self.data
    
    def validate_schema(self):
        #try:
        #   validate(self.data, schema=the_data_schema)
        #except ValidationError as exc:
        #   logger.warning(f'Couldn't validate schema. Error: {exc}')
        # self.data = None
        pass

    def connect_to_redis(self):
        r = redis.Redis(host=os.environ.get('DB_HOST'), port=os.environ.get('DB_PORT'))
        try:
            data = pickle.loads(r.get(os.environ.get('DATA_NAME')))
        except redis.exceptions.ConnectionError as exc:
            logger.warning(f'Redis has not been started: Exact Error: {exc}')
            data = None
        except TypeError as exc:
            # catch type error for pickle.loads because if the r.get returns None
            # we will have an error
            logger.warning(f'No data in Redis yet: Exact Error: {exc}')
            data = None

        return data
