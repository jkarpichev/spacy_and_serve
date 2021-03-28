FROM python:3.8.6-buster
WORKDIR /app 
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
RUN python -m spacy download en_core_web_sm
COPY . /app 
ENTRYPOINT ["python3"] 
CMD ["app.py"]

# CMD [ "gunicorn -w 1 -b 127.0.0.1:5000 app:app" ]

