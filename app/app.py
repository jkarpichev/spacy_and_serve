import json
import redis
import pickle
import random
#from data.data_handler import DataHandler
from loguru import logger
from flask import Flask, request, abort, jsonify


app = Flask(__name__)
#the_data = DataHandler()


def get_data():
    r = redis.Redis(host='localhost', port=6379, db=0)
    try:
        data = pickle.loads(r.get('collection'))
    except redis.exceptions.ConnectionError as exc:
        logger.warning(f'Redis is not running or something happened: {exc}')
        data = None

    return data

data = get_data()

def get_entities(names, the_data):
    arr = []
    for ent in names:
        arr.append(the_data[ent])
    return arr


@app.route('/getCharacterInfo/<name>', methods=['GET'])
def get_character_info(name):
    if name in data:
        res_entity = extract_entity(data[name])

    return jsonify(res_entity)

@app.route('/getMainCharacters', methods=['GET'])
def get_main_characers():
    # get all main characters of rank-1
    main_characters_names = list(filter(lambda x: data[x].get('rank') == 1, data))
    main_characters = get_entities(main_characters_names, data)
    return jsonify(create_response_schema(main_characters))

@app.route('/getSupportCharactes', methods=['GET'])
def get_support_characters():
    # get top 10 support characters
    secondary = list(filter(lambda x: data[x].get('rank') == 2, data))
    secondary_characters = get_entities(secondary, data)
    return jsonify(create_response_schema(secondary_characters))


@app.route('/getEpisodeCharacters', methods=['GET'])
def get_episode_characters():
    # get 10 random episode characters
    episode_names = list(filter(lambda x: data[x].get('rank') == 3, data))
    random.shuffle(episode_names)
    episode_characters = get_entities(episode_names[:10], data)
    return jsonify(create_response_schema(episode_characters))

@app.route('/getCharacterMentions/<name>', methods=['GET'])
def get_character_mentions(name):

    # if name in names
    # return only the name
    # else return all the names
    if name in data:
        res = list(data[name]['sent'].keys())
    else:
        main_characters_names = list(filter(lambda x: data[x].get('rank') == 1, data))
        res = {}
        for name in main_characters_names:
            res[name] = list(data[name]['sent'].keys())

    return jsonify(res)


@app.route('/getCharactersCoMenitons/<name_a>/<name_b>', methods=['GET'])
def get_characters_co_mentions(name_a, name_b):
    sents = set()
    if name_a in data and name_b in data:
        for sent in data[name_a]['sent']:
            if name_b in sent:
                sents.add(sent)
        for sent in data[name_b]['sent']:
            if name_a in sent:
                sents.add(sent)

    return jsonify(list(sents))


def extract_entity(character):
    """
    maybe include the entity name as its not in the response
    """
    rank = character.get('rank')
    mentions_count = character.get('count')
    mono_mentions_count = len(list(filter(lambda x: character['sent'][x]['times'] == 1, character.get('sent'))))
    co_mentions_count = list(filter(lambda x: character['sent'][x]['times'] > 1, character.get('sent')))
    co_mentions_names = []

    for key in co_mentions_count:
        co_mentions_names += list(character.get('sent').get(key).get('additional'))

    return {
            'rank': rank,
            'mentions_count': mentions_count,
            'mono_mentions_count': mono_mentions_count,
            'co_mentions_count': len(co_mentions_count),
            'co_mentions_names': co_mentions_names
        }

def create_response_schema(characters):
    res = []
    for character in characters:
        res.append(extract_entity(character))

    return res

if __name__ == '__main__':
    app.run()
