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

def get_main_characers():
    # get all main characters of rank-1
    pass

def get_support_characters():
    # get top 10 support characters
    pass

def get_episode_characters():
    # get 10 random episode characters
    pass

def get_character_mentions():
    pass


@app.route('getCharacterInfo/<name>')
def get_character_info(name):
    return jsonify(f'Character Info: {name}')


if __name__ == '__main__':
    app.run()
