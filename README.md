# Spacy and serve

Extract data from an unstructured text using spacy and serve it through an API

# Usage

#### Create virtualenv for local usage:

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

----
#### Ways to run the app
1) Run the app & redis containers (recommended)
`docker-compose up -d --build`
* In this case an api call should be made to: http://localhost:5000/generate_data
* That way the data will get generated and the api is ready to use
* If not the endpoints will return an error
* Option two is to generate the using data_generation_script.py
2) Run the server locally
 `python app.py`
* In this case the `data_generation_script.py` should be used from within the data folder
* Different parameters could be passed to the script to save the file in different ways
* The generic way should be to use **--save_to_redis=True**
* Or call the endpoint:  http://localhost:5000/generate_data
3) Run the server through docker
* uncomment the commented lines in the **Dockerfile**
`docker build -t flask_app .`
`docker run flask_app`
* After that use the `data_generation_script.py` script or call the endpoint
* **Note**! The redis container **will not** be started using this approach
----
#### Perform the healthcheck:

curl -XGET http://localhost:5000/health

#### Notes
One of the requirements wasn't implemented:
Identify and standartise all the short forms to the full form of the name.

## License
[MIT](https://choosealicense.com/licenses/mit/)
