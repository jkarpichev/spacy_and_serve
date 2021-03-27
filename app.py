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

@app.route('getMainCharacters/', methods=['GET'])
def get_main_characers():
    # get all main characters of rank-1
    return jsonify(create_response_schema('the charactes'))

@app.route('getSupportCharactes/', methods=['GET'])
def get_support_characters():
    # get top 10 support characters
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
    return jsonify(f'Character Info: {name}')


def create_response_schema(*args, **kwargs):
    return {}

if __name__ == '__main__':
    app.run()
