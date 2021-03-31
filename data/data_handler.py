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
        """
        Always try to get the lates data from redis
        and assign it to self.data
        Returns:
            The data after performing the lookup
        """
        if not self.data:
            self.data = self.connect_to_redis()
        return self.data
    
    def validate_schema(self):
        """
        In the roadmap:
        Define the structure of the schema in
        the_schema.
        After that uncomment so that every
        data lookup can perform the validation.
        Retruns:
            The validated schema or None
        """

        #try:
        #   validate(self.data, schema=the_data_schema)
        #except ValidationError as exc:
        #   logger.warning(f'Couldn't validate schema. Error: {exc}')
        # self.data = None
        pass

    def connect_to_redis(self):
        """
        Connect to redis and perform the data lookup,
        throw errors if the it hasn't been started or
        we have no data in it.
        """

        r = redis.Redis(host=os.environ.get('DB_HOST'), port=os.environ.get('DB_PORT'))
        try:
            data = pickle.loads(r.get(os.environ.get('DATA_NAME')))
        except redis.exceptions.ConnectionError as exc:
            logger.warning(f'Redis has not been started: Exact Error: {exc}')
            data = None
        except TypeError as exc:
            # catch TypeError for pickle.loads because if the r.get returns None
            # it will be raised
            logger.warning(f'No data in Redis yet: Exact Error: {exc}')
            data = None

        return data
