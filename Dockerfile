FROM python:3.8-buster
WORKDIR /app 
COPY requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir
RUN python -m spacy download en_core_web_sm
COPY . /app 
EXPOSE 5000
# ENTRYPOINT ["python3"]
# CMD ["app.py"]
