import json
import redis
import pickle
import random
from loguru import logger
from data.data_handler import DataHandler
from data.data_generator import DataGenerator
from data.constants import (RANK, SENT, COUNT, TIMES, ADDITIONAL, 
                            MENTIONS_COUNT, MONO_MENTIONS_COUNT, 
                            CO_MENTIONS_COUNT, CO_MENTIONS_NAMES, 
                            GET_CHARACTER_INFO, GET_MAIN_CHARACTERS, 
                            GET_SUPPORT_CHARACTES, GET_EPISODE_CHARACTERS, 
                            GET_CHARACTER_MENTIONS, GET_CHARACTER_CO_MENTIONS,
                            MISSING_DATA_STR, GENERATE_DATA)
from loguru import logger
from flask import Flask, request, abort, jsonify

app = Flask(__name__)


@app.route('/health')
def health():
    """
    Super simple endpoint that indicates wherther the api is operational
    Returns:
    """
    return jsonify('Up and running')


@app.route('/')
def index():
    """
    Route to display all available api endpoints.
    """
    logger.info('CALLED FROM: index ENDPOINT: Displaying all the available api endpoints.')

    rules = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        rules.append((rule.endpoint, methods, str(rule)))

    return jsonify(rules)


@app.route(f'/{GENERATE_DATA}', methods=['GET'])
def generate_data():
    """
    Route to regenerate the data collection.
    """
    # We could also run it on a separate thread
    # from threading import Thread
    # t = Thread(daemon=True)
    # t.run(DataGenerator().generate())

    logger.info(f'CALLED FROM: {GENERATE_DATA} ENDPOINT: Generating the data collection.')
    DataGenerator().generate()
    return jsonify("The data collection has been generated")

@app.route(
    f'/{GET_CHARACTER_INFO}',
    defaults={'name': None},
    methods=['GET'],
)
@app.route(f'/{GET_CHARACTER_INFO}/<name>')
def get_character_info(name):
    """
    Performs a lookup in the data collection for a
    specific name and if we have a match returns is schema,
    else it return 404 with the error
    Parametes:
        name str: The name of the named entity
    Returns:
        the generate schema
    """
    logger.info(f'CALLED FROM: {GET_CHARACTER_INFO} ENDPOINT: Performing a lookup on an entity.')

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
def get_main_characters():
    """
    Get all the entities from the data collection
    that have the rank = 1
    Returns:
    The generated schema for all the main entities
    """
    logger.info(f'CALLED FROM: {GET_MAIN_CHARACTERS} ENDPOINT: Displaying all the main characters.')

    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)
    main_characters_names = list(
        filter(lambda x: data[x].get('rank') == 1, data))
    main_characters = get_entities(main_characters_names, data)

    return jsonify(create_response_schema(main_characters))


@app.route(f'/{GET_SUPPORT_CHARACTES}', methods=['GET'])
def get_support_characters():
    """
    Get all the entities from the data collection
    that have the rank = 2
    Returns:
    The generated schema for all the support entities
    """
    logger.info(f'CALLED FROM: {GET_SUPPORT_CHARACTES} ENDPOINT: Displaying all the support characters.')

    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)

    secondary = list(filter(lambda x: data[x].get(RANK) == 2, data))
    secondary_characters = get_entities(secondary, data)

    return jsonify(create_response_schema(secondary_characters))


@app.route(f'/{GET_EPISODE_CHARACTERS}', methods=['GET'])
def get_episode_characters():
    """
    Get 10 random entities from the data collection
    that have the rank = 3
    Returns:
    The generated schema for all the episode entities
    """
    logger.info(f'CALLED FROM: {GET_EPISODE_CHARACTERS} ENDPOINT: Displaying all the episode characters.')

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
    """
    Perform a lookup for all the sentences in which
    a character has been mentioned, if we don't have
    a match on the name we return all the sentences
    for the main characters
    Parameters:
        name str: The name of a character, could be None
    Returns:
    A list of all the sentences for the given character
    or the list for every main character
    """
    logger.info(f'CALLED FROM: {GET_CHARACTER_MENTIONS} ENDPOINT: Displaying the sentences for a character mentions or the sentences for all main characters.')

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
    """
    Display all the sentences in which we have both entities
    else an error
    Parameters:
        name_a str: The name of the first character from the book
        name_b str: The name of the second character from the book
    Returns:
    The list of sentences or 404
    """
    logger.info(f'CALLED FROM: {GET_CHARACTER_CO_MENTIONS} ENDPOINT: Displaying the sentences in which we have both character_a and character_b.')

    data = DataHandler().get_data()

    if not data:
        abort(404, description=MISSING_DATA_STR)
        logger.info('Called FROM: {GET_CHARACTER_CO_MENTIONS} ENDPOINT: No data in the collection.')
    if not all((name_a, name_b)):
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
    Package the entity info as a data schema
    Parametes:
        character dict: current entity from the collection
    Returns:
    The schema like object in the desired format
    """
    rank = character.get(RANK)
    mentions_count = character.get(COUNT)
    mono_mentions_count = len(
        list(
            filter(lambda x: character[SENT][x][TIMES] == 1,
                   character.get(SENT))))

    co_mentions_names = []
    co_mentions_count = 0

    # we separate the sentences for convenience
    sentences = character[SENT]
    for sent in sentences:
        if len(sentences[sent][ADDITIONAL]) > 0:
            co_mentions_count += 1
            co_mentions_names.extend(sentences[sent][ADDITIONAL])

    # we cast the list to set so that we eliminate the duplications
    # and we cast it to list again to be json serializable
    co_mentions_names = list(set(co_mentions_names))

    return {
        RANK: rank,
        MENTIONS_COUNT: mentions_count,
        MONO_MENTIONS_COUNT: mono_mentions_count,
        CO_MENTIONS_COUNT: co_mentions_count,
        CO_MENTIONS_NAMES: co_mentions_names
    }


def create_response_schema(characters: dict) -> list:
    """
    Wrapper function that accepts a set of entities 
    and packages them in the desired schema
    Parametes:
        characters dict: The collection of entities
    Returns:
        the list of extracted dicts
    """
    res = []
    for character in characters:
        res.append(extract_entity(character))

    return res


def get_entities(names: list, the_data: dict) -> list:
    """
    Extract the given entitiy names from the data
    Parameters:
        names list[str]: The names to be extracted
        the_data: The collection from which to extract the names
    Returns:
        the extracted entities from the_data
    """
    entities = []
    for ent in names:
        entities.append(the_data[ent])
    return entities


if __name__ == '__main__':
    logger.info('::Starting the app::')
    app.run(host='0.0.0.0')
