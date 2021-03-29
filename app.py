import json
import redis
import pickle
import random
from data.data_handler import DataHandler
from data.constants import (RANK, SENT, COUNT, TIMES, ADDITIONAL, 
                            MENTIONS_COUNT, MONO_MENTIONS_COUNT, 
                            CO_MENTIONS_COUNT, CO_MENTIONS_NAMES, 
                            GET_CHARACTER_INFO, GET_MAIN_CHARACTERS, 
                            GET_SUPPORT_CHARACTES, GET_EPISODE_CHARACTERS, 
                            GET_CHARACTER_MENTIONS, GET_CHARACTER_CO_MENTIONS,
                            MISSING_DATA_STR)
from loguru import logger
from flask import Flask, request, abort, jsonify

app = Flask(__name__)


def get_entities(names, the_data):
    arr = []
    for ent in names:
        arr.append(the_data[ent])
    return arr


@app.route('/')
def index():
    rules = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        rules.append((rule.endpoint, methods, str(rule)))

    return jsonify(rules)

@app.route(f'/{GET_CHARACTER_INFO}', defaults={'name': None}, methods=['GET'])
@app.route(f'/{GET_CHARACTER_INFO}/<name>')
def get_character_info(name):

    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)
    elif not name:
        abort(404, description='No name provided.')
    elif name not in data:
        abort(404, description=f"The name: {name} is not in the collection")

    res_entity = extract_entity(data[name])
    return jsonify(res_entity)


@app.route(f'/{GET_MAIN_CHARACTERS}', methods=['GET'])
def get_main_characers():
    # get all main characters of rank-1

    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)
    main_characters_names = list(
        filter(lambda x: data[x].get('rank') == 1, data))
    main_characters = get_entities(main_characters_names, data)

    return jsonify(create_response_schema(main_characters))


@app.route(f'/{GET_SUPPORT_CHARACTES}', methods=['GET'])
def get_support_characters():
    # get top 10 support characters

    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)

    secondary = list(filter(lambda x: data[x].get(RANK) == 2, data))
    secondary_characters = get_entities(secondary, data)

    return jsonify(create_response_schema(secondary_characters))


@app.route(f'/{GET_EPISODE_CHARACTERS}', methods=['GET'])
def get_episode_characters():
    # get 10 random episode characters

    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)

    episode_names = list(filter(lambda x: data[x].get(RANK) == 3, data))
    random.shuffle(episode_names)
    episode_characters = get_entities(episode_names[:10], data)

    return jsonify(create_response_schema(episode_characters))


@app.route(
    f'/{GET_CHARACTER_MENTIONS}',
    defaults={'name': None},
    methods=['GET'],
)
@app.route(f'/{GET_CHARACTER_MENTIONS}/<name>')
def get_character_mentions(name):
    # if name in names
    # return only the name
    # else return all the names

    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)
    elif not name:
        abort(404, description='No name provided.')
    elif name in data:
        res = list(data[name][SENT].keys())
    else:
        main_characters_names = list(
            filter(lambda x: data[x].get(RANK) == 1, data))
        res = {}
        for name in main_characters_names:
            res[name] = list(data[name][SENT].keys())

    return jsonify(res)


@app.route(f'/{GET_CHARACTER_CO_MENTIONS}', defaults={'name_a': None, 'name_b': None}, methods=['GET'])
@app.route(f'/{GET_CHARACTER_CO_MENTIONS}/<name_a>/<name_b>')
def get_characters_co_mentions(name_a, name_b):
    
    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)
    if all(name_a, name_b):
        abort(404, description='Missing name argument.')

    sents = set()
    if name_a in data and name_b in data:
        for sent in data[name_a][SENT]:
            if name_b in sent:
                sents.add(sent)
        for sent in data[name_b][SENT]:
            if name_a in sent:
                sents.add(sent)

    return jsonify(list(sents))


def extract_entity(character):
    """
    maybe include the entity name as its not in the response
    """
    rank = character.get(RANK)
    mentions_count = character.get(COUNT)
    mono_mentions_count = len(
        list(
            filter(lambda x: character[SENT][x][TIMES] == 1,
                   character.get(SENT))))
    co_mentions_count = list(
        filter(lambda x: character[SENT][x][TIMES] > 1,
               character.get(SENT)))
    co_mentions_names = []

    for key in co_mentions_count:
        co_mentions_names += list(
            character.get(SENT).get(key).get(ADDITIONAL))

    return {
        RANK: rank,
        MENTIONS_COUNT: mentions_count,
        MONO_MENTIONS_COUNT: mono_mentions_count,
        CO_MENTIONS_COUNT: len(co_mentions_count),
        CO_MENTIONS_NAMES: co_mentions_names
    }


def create_response_schema(characters):
    res = []
    for character in characters:
        res.append(extract_entity(character))

    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0')
