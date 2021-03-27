import spacy
import re
from collections import Counter
FNAME = '../y_task/a_portrait_new.txt'


pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'  
input_file = open(FNAME, encoding='utf8').readlines()
#ifile = re.sub(pat, '', input_file)
modded = [re.sub(pat, '', x.strip()) for x in input_file]
modded = [x for x in modded if x != '']
lel = ' '.join(modded)
nlp = spacy.load("en_core_web_sm")
start_data = nlp(lel)
sentences = list(start_data.sents)
print(start_data)
# this bad boy finds all of the sentences where a NER is mentioned
# sents = [ent.sent for ent in start_data.ents if ent.text == 'Dante']
# print(len(sents))

all_ner = set([ent.text for ent in start_data.ents if ent.label_ == 'PERSON'])

# individual sentences in which we find a given NER
mentions_sents = dict()

# all entities, counted and all of the sentences in which they were mentioned
visited = []
for ent in start_data.ents:
    if ent.label_ == 'PERSON':
        if ent.text not in visited:
            visited.append(ent.text)
            mentions_sents[ent.text] = {
                'count': 1,
                'sent': [ent.sent],
                'co_mentions': []
            }
        else:
            mentions_sents[ent.text]['count'] = mentions_sents[ent.text]['count'] + 1
            mentions_sents[ent.text]['sent'].append(ent.sent)


# 
for ner, elements in mentions_sents.items():
    for sent in elements.get('sent'):
        for name in all_ner:
            if name in sent:
                # if we want to add the count as well
                # sent.count(name)
                mentions_sents[ner]['co_mentions'].append(name)
