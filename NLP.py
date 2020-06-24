"""
Created on Wed Jun 17 2020
@author: Leon Lu
"""
from geotext import GeoText
import nltk
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

import numpy as np
import os
import json 
import gzip
import re
import string

def get_listings(entry):
    """Get file names that are jobs listings"""
    sub_entries = os.listdir('C:/Users/Leon/Data/Jobs/'+entry)
    entries = []
    for i in sub_entries:
        if i[-4:] == '_.gz':
            entries.append(i)
    return entries

def decide_loc(locations):
    """Decide which location is the right location"""
    if locations.size != 0:
        unique,pos = np.unique(locations,return_inverse=True) 
        counts = np.bincount(pos)                    
        maxpos = counts.argmax()
        return unique[maxpos]
    return 'no location found'

def decide_org(orgs):
    """Decide which company name is the right company name"""
    if orgs.size != 0:
        unique,pos = np.unique(orgs,return_inverse=True) 
        counts = np.bincount(pos)                    
        maxpos = counts.argmax()
        return unique[maxpos]
    return 'no company found'

def check_remote(text):
    """Check whether or not a posting is remote"""
    r = re.compile(r'\bRemote\b | \bwork from home\b', flags=re.I | re.X)
    matches = r.findall(text)
    return len(matches) != 0 

def not_common(text):
    """Check whether or not entity is a false positive company ie programming language or blockchain keyword"""
    false_positive = re.compile('[Bb]lockchain|Ethereum|Rust|Kotlin|Elixer|Julia|Swift|Go|Java|Python|C#|OCaml|Javascript|Lua|Haskell|Octave|MATLAB|Perl|Ruby|PHP|SQL|[Cc]ryptocurrencies|AWS|Amazon|Microsoft|UX|React [Native|JS| ]|Dice')
    return not false_positive.search(text)

def check_state(text):
    """Look for common state abbreviations"""
    states = re.compile(' AL | AK | AZ | AR | CA | CO | CT | DC | DE | FL | GA | HI | ID | IL | IN | IA | KS |'+
    ' KY | LA | ME | MD | MA | MI | MN | MS | MO | MT | NE | NV | NH | NJ | NM | NY | NC | ND | OH | OK | OR |'+
    ' PA | RI | SC | SD | TN | TX | UT | VT | VA | WA | WV | WI | WY ')
    return states.findall(text)

def nlp_title(text,tagger):
    """Retrieve information from title line"""
    tokenized_text = word_tokenize(text)
    tokenized_text = [n for n in tokenized_text if not_common(n.strip())]
    classified_text = tagger.tag(tokenized_text)
    loc = []
    name = []
    prev = ''
    for (t,lab) in classified_text:
        if t in string.punctuation:
            prev = ''
        elif lab == 'LOCATION':
            if prev == 'LOCATION':
                loc.append(loc.pop()+' '+t)
            else:
                loc.append(t)
            prev = 'LOCATION'
        elif lab == 'ORGANIZATION':
            if prev == 'ORGANIZATION':
                name.append(name.pop()+' '+t)
            else:
                name.append(t)
            prev = 'ORGANIZATION'
        else:
            prev = ''

    if loc:
        location = loc[-1]
    else:
        location = 'Location not found'

    if name:
        org_name = name[-1]
    else:
        org_name = 'Company not found'

    if check_remote(text):  
        location = 'remote'
    salary = 'not found'
    return location, org_name, salary

def nlp_body(text,tagger):
    """Retrieve information from body"""
    tokenized_text = word_tokenize(text)
    classified_text = tagger.tag(tokenized_text)
    loc = []
    name = []

    for (t,lab) in classified_text:
        if lab == 'LOCATION':
            loc.append(t)
        elif lab == 'ORGANIZATION':
            name.append(t)

    loc = loc[:len(loc)//4]
    name = name[:len(name)//4]
    name = [n for n in name if not_common(n.strip())]

    org_name = decide_org(np.array(name))
    location = decide_loc(np.array(loc))
    if check_remote(text):  
        location = 'remote'
    salary = 'not found'
    return location, org_name, salary

def index_json(filenames,site):
    """Get retrive data from json files"""
    tagger = StanfordNERTagger('C:/Users/Leon/BlockchainOpportunityAnalysis/stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz',
    'C:/Users/Leon/BlockchainOpportunityAnalysis/stanford-ner-4.0.0/stanford-ner.jar',
    encoding='utf-8')
    regex = re.compile('[^a-zA-Z\-]')
    for f in filenames:
        with gzip.GzipFile('C:/Users/Leon/Data/Jobs/'+site+'/'+f,"r") as json_file:
            job = json.loads(json_file.read().decode('utf-8'))
         
            text_loc, text_org,body_sal = nlp_body(regex.sub(' ',job['Body']),tagger)
            title_loc, title_org,title_sal = nlp_title(regex.sub(' ',job['Title']),tagger)
            
            state = check_state(job['Title'])
            if title_loc == "Location not found" and state:
                    title_loc = check_state(job['Title'])[0]

            with open('C:/Users/Leon/BlockchainOpportunityAnalysis/Data/'+site+'/'+f[:-3]+'nlp.txt', "w") as w:
                w.write("bodylocation:"+text_loc+'\nbodycompany:'+text_org+'\nbodysalary'+body_sal+'\ntitlelocation:'
                +title_loc+'\ntitlecompany:'+title_org+'\ntitlesalary:'+title_sal)
            

def get_entities(site_dict):
    """Retrive entities for each job posting if it is available"""
    keys = site_dict.keys()
    #for k in keys:
    index_json(site_dict['dice'],'dice')

if __name__ == "__main__":
    entries = os.listdir('C:/Users/Leon/Data/Jobs')
    site_dict = {}
    for e in entries:
        site_dict[e] = get_listings(e)
        print(e,len(site_dict[e]))
    get_entities(site_dict)
