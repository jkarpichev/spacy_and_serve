import spacy
import re
import json
import sys
import redis
import pickle
from collections import Counter

FNAME = 'a_portrait_new.txt'


def set_rank(collection):
    for entity, vals in collection.items():
        collection[entity]['rank'] = calc_rank(vals['count'])

def calc_rank(count):
    percentage = ((count - min_val) * 100) / (max_val - min_val)

    if percentage <= 33:
        return 3
    elif percentage > 33 and percentage <= 66:
        return 2
    else:
        return 1
    

pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'  
input_file = open(FNAME, encoding='utf8').readlines()
#ifile = re.sub(pat, '', input_file)
modded = [re.sub(pat, '', x.strip()) for x in input_file]
modded = [x for x in modded if x != '']
lel = ' '.join(modded)
nlp = spacy.load("en_core_web_sm")
start_data = nlp(lel)
sentences = list(start_data.sents)
# this bad boy finds all of the sentences where a NER is mentioned
# sents = [ent.sent for ent in start_data.ents if ent.text == 'Dante']
# print(len(sents))

all_ner = set([ent.text for ent in start_data.ents if ent.label_ == 'PERSON'])

# individual sentences in which we find a given NER
mentions_sents = dict()

# all entities, counted and all of the sentences in which they were mentioned
# visited = []
# for ent in start_data.ents:
#     if ent.label_ == 'PERSON':
#         if ent.text not in visited:
#             visited.append(ent.text)
#             mentions_sents[ent.text] = {
#                 'count': 1,
#                 'sent': [ent.sent]
#             }
#         else:
#             mentions_sents[ent.text]['count'] = mentions_sents[ent.text]['count'] + 1
#             mentions_sents[ent.text]['sent'].append(ent.sent)

# individual sentences in which we find a given NER
mentions_sents = dict()

# all entities, counted and all of the sentences in which they were mentioned
visited = []
for ent in start_data.ents:
    if ent.label_ == 'PERSON':
        sent_string = str(ent.sent)
        if ent.text not in visited:
            visited.append(ent.text)
            mentions_sents[ent.text] = {
                'count': 1,
                'sent': {sent_string: {'additional': set(), 'times': sent_string.count(ent.text)}}
            }
        else:
            mentions_sents[ent.text]['count'] = mentions_sents[ent.text]['count'] + 1
            mentions_sents[ent.text]['sent'][sent_string] = {'additional': set(), 'times': sent_string.count(ent.text)}

print(len(mentions_sents))


items = [x.text for x in start_data.ents if x.label_ == 'PERSON']
cter = Counter(items)

for ner, elements in mentions_sents.items():
    for k, v in elements.get('sent').items():
        for name in all_ner:
            if name != ner and name in k:
                # if we want to add the count as well
                mentions_sents[ner]['sent'][k]['additional'].add(name)
print(mentions_sents.get('Dante'))

# think about how to divide them to 3 categories
# add the counter, get the x most common
# get the min and max val from it
min_val = 1
max_val = cter.most_common(1)[0][1]

set_rank(mentions_sents)

for entity in mentions_sents:
    print(f"Name: {entity} --> Count: {mentions_sents[entity]['count']} --> Rank: {mentions_sents[entity]['rank']}")


r = redis.Redis(host='localhost', port=6379, db=0)
try:
    r.set('collection', pickle.dumps(mentions_sents))
except redis.exceptions.ConnectionError as exc:
    print(f'Redis is not running: {exc}')
    sys.exit()