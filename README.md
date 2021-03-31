Spacy and serve
=================

Extract data from an unstructured text and serve it through an api

Usage
-----

Create virtualenv for local usage:

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

Run the server locally

    python app.py

Run the server through docker

    docker build -t flask_app .
    docker run

Try the endpoints:

    curl -XGET http://localhost:5000/health


Docs
----
if we want to run the data script we have to set the DB_HOST to 'localhost' as it's currently
set int .env to be run serverside

Explain why im gettign the data from DataHandler().get_data() on every request


if we want to run the jupyter book we have to install the "jupyter" package
pip install jupyter
It wasn't included in the requirements because it's not needed for the dockerised apps
COMMANDS:
docker-compose up -d --no-deps --build