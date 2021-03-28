from loguru import logger


class DataHandler:
    data = None

    def __init__(self):
        self.data = set_data()

    def get_data(self):
        if not self.data:
            self.data = self.set_data()

    def set_data(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        try:
            data = pickle.loads(r.get('collection', mentions_sents))
        except redis.exceptions.ConnectionError as exc:
            logger.warning(f'Redis is not running or something happened: {exc}')
            data = None

        return data
