from flask import Flask, request, abort, jsonify
import json
app = Flask(__name__)


schema = {
    'rank': None,
    'mentions_count': None,
    'mono_mentions_count': None,
    'co_mentions_count': None,
    'co_mentions_names': None
}

def get_data():
    r = redis.Redis(host='localhost', port=6379, db=0)
    try:
        data = pickle.loads(r.get('collection', mentions_sents))
    except redis.exceptions.ConnectionError as exc:
        print(f'Redis is not running: {exc}')
        data = None
    return data

data = get_data()

@app.route('getMainCharacters/', methods=['GET'])
def get_main_characers():
    # get all main characters of rank-1
    main_characters = list(filter(lambda x: x.get(rank) == 1, data))
    return jsonify(create_response_schema(main_characters))

@app.route('getSupportCharactes/', methods=['GET'])
def get_support_characters():
    # get top 10 support characters
    secondary = list(filter(lambda x: data[x].get('rank') == 2, data))
    return jsonify(create_response_schema('the secondary charactes'))


@app.route('getEpisodeCharacters/', methods=['GET'])
def get_episode_characters():
    # get 10 random episode characters
    return jsonify(create_response_schema('the episode charactes'))

@app.route('getCharacterMentions/<name>', methods=['GET'])
def get_character_mentions(name):

    # if name in names
    # return only the name
    # else return all the names

    return jsonify(create_response_schema('the episode charactes'))


app.route('getCharactersCoMenitons/<name_a>/<name_b>', methods=['GET'])
def get_characters_co_mentions(name_a, name_b):

    return jsonify(create_response_schema('the episode charactes'))


@app.route('getCharacterInfo/<name>', methods=['GET'])
def get_character_info(name):
    if name in data:
        res_entity = extract_entity(name)

    return jsonify(res_entity)


def extract_entity(character):
    rank = character.get('rank')
    mentions_count = character.get('count')
    mono_mentions_count = len(list(filter(lambda x: character['sent'][x]['times'] == 1, character.get('sent'))))
    co_mentions_count = list(filter(lambda x: character['sent'][x]['times'] > 1, character.get('sent')))
    co_mentions_names = set()

    for key in co_mentions_count:
        co_mentions_names.update(character.get('sent').get(key).get('additional'))

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
