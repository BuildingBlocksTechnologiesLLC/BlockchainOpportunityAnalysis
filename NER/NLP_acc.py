"""
Created on Wed July 1 2020
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
from date_extractor import extract_dates
from datetime import datetime

def decide_loc(locations):
    """
    Decide which location is the right location
    """
    if locations.size != 0:
        unique,pos = np.unique(locations,return_inverse=True) 
        counts = np.bincount(pos)                    
        maxpos = counts.argmax()
        return unique[maxpos]
    return 'Not Found'

def decide_org(orgs):
    """
    Decide which company name is the right company name
    """
    if orgs.size != 0:
        unique,pos = np.unique(orgs,return_inverse=True) 
        counts = np.bincount(pos)                    
        maxpos = counts.argmax()
        return unique[maxpos]
    return 'Not Found'

def check_remote(text):
    """
    Check whether or not a posting is remote
    """
    r = re.compile(r'Remote|work from home| Remotely', re.IGNORECASE) 
    matches = r.findall(text)
    return len(matches) != 0 

def not_common(text):
    """
    Check whether or not entity is a false positive company ie programming language or blockchain keyword
    """
    false_positive = re.compile('[Bb]lockchain|Ethereum|Rust|Kotlin|Elixer|Julia|Swift|Go|Java|Python|C#|OCaml|Javascript|Lua|Haskell|Octave|MATLAB|Perl|Ruby|PHP|SQL|[Cc]ryptocurrencies|AWS|Amazon|Microsoft|UX|React [Native|JS| ]|Dice')
    return not false_positive.search(text)
def check_state(text):
    """
    Look for common state abbreviations
    """
    states = re.compile('Alaska|Alabama|Alaska|Arizona|'+
    'Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|'+
    'Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|'+
    'Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|'+
    'North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|'+
    'South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming')
    state_abbr = re.compile(' AL | AK | AZ | AR | CA | CO | CT | DC | DE | FL | GA | HI | ID | IL | IN | IA | KS |'+
    ' KY | LA | ME | MD | MA | MI | MN | MS | MO | MT | NE | NV | NH | NJ | NM | NY | NC | ND | OH | OK | OR |'+
    ' PA | RI | SC | SD | TN | TX | UT | VT | VA | WA | WV | WI | WY ')
    d_state = {
        ' AK ': 'Alaska',
        ' AL ': 'Alabama',
        ' AR ': 'Arkansas',
        ' AS ': 'American Samoa',
        ' AZ ': 'Arizona',
        ' CA ': 'California',
        ' CO ': 'Colorado',
        ' CT ': 'Connecticut',
        ' DC ': 'District of Columbia',
        ' DE ': 'Delaware',
        ' FL ': 'Florida',
        ' GA ': 'Georgia',
        ' GU ': 'Guam',
        ' HI ': 'Hawaii',
        ' IA ': 'Iowa',
        ' ID ': 'Idaho',
        ' IL ': 'Illinois',
        ' IN ': 'Indiana',
        ' KS ': 'Kansas',
        ' KY ': 'Kentucky',
        ' LA ': 'Louisiana',
        ' MA ': 'Massachusetts',
        ' MD ': 'Maryland',
        ' ME ': 'Maine',
        ' MI ': 'Michigan',
        ' MN ': 'Minnesota',
        ' MO ': 'Missouri',
        ' MP ': 'Northern Mariana Islands',
        ' MS ': 'Mississippi',
        ' MT ': 'Montana',
        ' NA ': 'National',
        ' NC ': 'North Carolina',
        ' ND ': 'North Dakota',
        ' NE ': 'Nebraska',
        ' NH ': 'New Hampshire',
        ' NJ ': 'New Jersey',
        ' NM ': 'New Mexico',
        ' NV ': 'Nevada',
        ' NY ': 'New York',
        ' OH ': 'Ohio',
        ' OK ': 'Oklahoma',
        ' OR ': 'Oregon',
        ' PA ': 'Pennsylvania',
        ' PR ': 'Puerto Rico',
        ' RI ': 'Rhode Island',
        ' SC ': 'South Carolina',
        ' SD ': 'South Dakota',
        ' TN ': 'Tennessee',
        ' TX ': 'Texas',
        ' UT ': 'Utah',
        ' VA ': 'Virginia',
        ' VI ': 'Virgin Islands',
        ' VT ': 'Vermont',
        ' WA ': 'Washington',
        ' WI ': 'Wisconsin',
        ' WV ': 'West Virginia',
        ' WY ': 'Wyoming'
        }
    abbr = state_abbr.findall(text)
    full = states.findall(text)
    state = ''
    if abbr:
        state = d_state[abbr[0]]
    if full:
        state = full[0]
    return state

def regex_title(text):
    """
    Find location in the title
    """
    loc = GeoText(text)
    if loc.cities:
        if 'US' in loc.country_mentions:
            state = check_state(text)
            if state != '':
                return loc.cities[0]+', '+state[0]+', '+'United States'
        elif loc.countries:
            return loc.cities[0]+', '+loc.countries[0]

    return 'Not Found'
def nlp_title(text,tagger):
    """
    Retrieve information from title line
    """
    location = regex_title(text)
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

    geo = GeoText(text)
    if loc:
        location = loc[-1]
    elif geo.cities:
        nation = list(geo.country_mentions.keys())
        location = str(geo.cities[0])+', '+str(nation[0])
    else:
        location = 'Not Found'

    if name:
        org_name = name[-1]
    else:
        org_name = 'Not Found'

    if check_remote(text):  
        location = 'Remote'

    find_at = re.compile(r' at ',re.IGNORECASE)
    punct = re.compile(r'\,|\-|\.|\/|\:|\;|\\|\||\–')
    if find_at.findall(text):
        text_post = text[text.index(' at '):]
        abbr_re = re.compile('Inc|LLC|Co|Ltd|.com|.org|.net')
        abb = abbr_re.findall(text_post)
        abbrev = [m.start(0) for m in abbr_re.finditer(text_post)]
        if abbrev:
            org_name = text_post[4:abbrev[0]+len(abb[0])]
        elif punct.findall(text_post):
            org_name = text_post[4:text_post.index(punct.findall(text_post)[0])-1]
        else:
            org_name = text_post[4:]
    
    return location.strip(), org_name.strip()

def check_sal_fp(text):
    """
    Check for false positives in salary
    """
    halves = text.split('-')
    if halves:
        if len(halves[0]) < 3:
            return True
    symbols = re.compile('\W',re.IGNORECASE)
    all_s = symbols.findall(text)
    for i in all_s:
        if i != '$' and i != '/' and i != ',' and i != '.' and i != '-' and i != '+':
            return True

    if len(text) <=4 or text[-1] == ',' or text.count('-') > 1:
        return True
    return False

def find_sal(text):
    """
    Find salary from posting
    """
    text = text.replace('\u2013','-')
    text = text.replace('401K','')
    text = text.replace('401k','')
    salary = 'Not Found'
    re_sal = re.compile(r'compensation|salary|estimate', re.IGNORECASE) 
    sal = re_sal.findall(text)
    
    if sal:
        for i in sal:
            salary_search = text[text.index(i)-20:text.index(i)+32]
            case = re.compile('[0-9]K|\$|[0-9]',re.IGNORECASE)
            sal1 = case.findall(salary_search)
            indices = [m.start(0) for m in case.finditer(salary_search)]
            if sal1:
                salary = salary_search[indices[0]:indices[-1]+2]
                if salary_search[indices[-1]:indices[-1]+1] == 'k' or salary_search[indices[-1]:indices[-1]+1] == 'K':
                    salary = salary + 'K'
                break

    if salary == 'Not Found':
        sal_range_re = re.compile('\-|\–')
        sal_range = sal_range_re.findall(text)
        indices = [m.start(0) for m in sal_range_re.finditer(text)]

        for i in indices:
            re_dol = re.compile('\$',re.IGNORECASE) 
            dol = re_dol.findall(text)
            
            salary_dol = text[i-10:i+10]
            end = re.compile(' per ', re.IGNORECASE)
            sal = end.findall(salary_dol)
            if sal:
                if sal[-1] == 'per':
                    salary = salary_dol[:salary_dol.index(sal[-1])+len(sal[-1])]
                    next_word = salary_dol[salary_dol.index(sal[-1])+len(sal[-1]):salary_dol.index(' ')]

                    salary = salary +' '+next_word
                else:
                    salary = salary_dol[:salary_dol.index(sal[-1])+len(sal[-1])]
                break
            else:
                case = re.compile('[0-9]K|\$|[0-9]',re.IGNORECASE)
                sal1 = case.findall(salary_dol)
                indices = [m.start(0) for m in case.finditer(salary_dol)]
                if sal1:
                    salary = salary_dol[indices[0]:indices[-1]+2]
                    if salary_dol[indices[-1]:indices[-1]+1] == 'k' or salary_dol[indices[-1]:indices[-1]+1] == 'K':
                        salary = salary + 'K'
                    break
                
    false_positive = re.compile(r'20[0-9][0-9]|\#|\(|\%|\!|[0-9][a-z][0-9]|am|pm',re.IGNORECASE)
    sal_no_space = salary.replace(' ','')
    if false_positive.findall(salary) or check_sal_fp(sal_no_space):
        salary = "Not Found"
    return salary

def nlp_body(text,tagger):
    """
    Retrieve information from body
    """
    regex = re.compile('[^a-zA-Z\-\|\,0-9\+]')
    re_text = regex.sub(' ',text)
    tokenized_text = word_tokenize(re_text)
    classified_text = tagger.tag(tokenized_text)
    loc = []
    name = []

    for (t,lab) in classified_text:
        if lab == 'LOCATION':
            loc.append(t)
        elif lab == 'ORGANIZATION':
            name.append(t)

    name = [n for n in name if not_common(n.strip())]

    org_name = decide_org(np.array(name))
    location = decide_loc(np.array(loc))
    geo = GeoText(re.sub(r'\bdate\b', '', re_text))
    if location == 'Not Found' and geo.cities:
        nation = list(geo.country_mentions.keys())
        location = str(geo.cities[0]) +', '+str(nation[0])
    if check_remote(re_text):  
        location = 'Remote'
        
    salary = 'Not Found'
    date = 'Not Found'

    re_date = re.compile(r'date post|date posted ',re.IGNORECASE) 
    find_date = re_date.findall(re_text)
    if find_date:
        find_date = re_text[re_text.index(find_date[0]):re_text.index(find_date[0])+30]

        date_time = extract_dates(find_date)[0]
        date = date_time.strftime("%e %b %Y")
        
    if date == 'Not Found':
        re_date = re.compile(r'\bmonths ago\b|\bdays ago\b|\bhours ago\b',re.IGNORECASE) 
        dtype = re_date.findall(re_text)
        if dtype:
            find_date = re_text[re_text.index(dtype[0])-4:re_text.index(dtype[0])+2]
            date_time = re.compile('[1-9][0-9][0-9]|[1-9][0-9]|[0-9]')
            date = date_time.findall(find_date)[0]+' '+dtype[0]
    
    salary = find_sal(text)
        
    return location.strip(), org_name.strip(), salary.strip(), date.strip()

def linkedin_title(text, tagger):
    """
    Retrieve information specifically from linkedin titles
    """
    try:
        comp_index = text.index(' hiring ')
        org_name = text[:comp_index]
    except ValueError:
        org_name = 'Not Found'
    try:
        loc_index = text.index(' in ')
        loc_end = text.index('|',loc_index)
        location = text[loc_index+4:loc_end-1]
    except ValueError:
        location = 'Not Found'

    return location.strip(), org_name.strip()

def index_json(filenames):
    """
    Get data from json files
    """

    tagger = StanfordNERTagger('C:/Users/Leon/BlockchainOpportunityAnalysis/stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz',
    'C:/Users/Leon/BlockchainOpportunityAnalysis/stanford-ner-4.0.0/stanford-ner.jar',
    encoding='utf-8')
    tot = 0 
    title_cor_loc = 0
    body_cor_loc = 0
    title_cor_org = 0
    body_cor_org = 0
    total_cor_date = 0
    total_cor_sal = 0
    total_cor_org = 0
    total_cor_loc = 0
    nf_tcd = 0
    nf_tcs = 0
    nf_td = 0
    nf_ts = 0
    incorrect = ''
    
    for f in filenames:

        with open('C:/Users/Leon/BlockchainOpportunityAnalysis/NER/'+f,"r") as json_file:
            job = json.load(json_file)

            correct_org = job['Company name']
            correct_loc = job['Location']
            correct_sal = job['Salary']
            correct_date = job['Date Posted']
            da = re.compile(r'ago',re.IGNORECASE)
            if not da.findall and correct_date != "Not Found":
                try:
                    date_time = extract_dates(correct_date)[0]
                    correct_date = date_time.strftime("%e %b %Y")
                except IndexError:
                    print(f)
                    print(correct_date)

            if correct_date != "Not Found":
                nf_td += 1
            if correct_sal != "Not Found":
                nf_ts += 1

            text = job['Body']            
            site = job['Site']

            pred = {}
            if site == 'linkedin':
                title_loc, title_org = linkedin_title(job['Title'],tagger)
            else:
                title_loc, title_org = nlp_title(job['Title'],tagger)

            text_loc, text_org,text_sal, text_date = nlp_body(job['Body'],tagger)
            tot += 1
            pred['site'] = site
            pred['body loc'] = text_loc
            pred['body org'] = text_org
            pred['salary'] = text_sal
            pred['date'] = text_date
            pred['title loc'] = title_loc
            pred['title org'] = title_org
            if title_loc == correct_loc:
                title_cor_loc += 1 
            '''    
            else:
                print(correct_loc,title_loc)
                print(site)
                print(f)
            '''
            if text_loc == correct_loc:   
                body_cor_loc += 1
            if title_org == correct_org:
                title_cor_org += 1
            if title_org.strip() == correct_org.strip() or text_org.strip() == correct_org.strip():
                total_cor_org += 1
            else:
                incorrect = incorrect+f+'\n'+ 'correct: ' +correct_org +'\n' +'pred: '+text_org+' - '+title_org+'\n'
            '''
            else:
                print(correct_org,title_org)
                print(site)
                print(f)
            '''

            if text_org == correct_org:
                body_cor_org += 1
            if text_date == correct_date:
                total_cor_date += 1
            
            if title_loc.strip() == correct_loc.strip() or text_loc.strip() == correct_loc.strip():
                total_cor_loc += 1 

            if text_sal == correct_sal:
                total_cor_sal += 1
            '''
            else:
                print(correct_sal,text_sal)
                print(site)
                print(f)
            '''
            if text_date == correct_date and correct_date != "Not Found":
                nf_tcd += 1
            if text_sal == correct_sal and correct_sal != "Not Found":
                nf_tcs += 1

            json_str = json.dumps(pred, indent = 4) + "\n" 

            with open('C:/Users/Leon/BlockchainOpportunityAnalysis/NER/predictions/'+f[:-3]+'nlp', "w") as w:
                w.write(json_str)
    print('Title location Accuracy:',title_cor_loc/tot)
    print('Body location Accuracy:',body_cor_loc/tot)
    print('Title company Accuracy:',title_cor_org/tot)
    print('Body company Accuracy:',body_cor_org/tot)
    print('Total location Accuracy:',total_cor_loc/tot)
    print('Total company Accuracy:',total_cor_org/tot)
    print('Date Accuracy:',total_cor_date/tot)
    print('Salary Accuracy:',total_cor_sal/tot)
    print('No Not Found, Date Accuracy:',nf_tcd/nf_td)
    print('No Not Found, Salary Accuracy:',nf_tcs/nf_ts)
    with open('incorrect.txt','w') as o:
        o.write(incorrect)
'''
Title location Accuracy: 0.6160520607375272
Body location Accuracy: 0.0368763557483731
Title company Accuracy: 0.7787418655097614
Body company Accuracy: 0.16268980477223427
Total location Accuracy: 0.6355748373101953
Total company Accuracy: 0.7960954446854663
Date Accuracy: 0.9891540130151844
Salary Accuracy: 0.9718004338394793
No Not Found, Date Accuracy: 0.9122807017543859
No Not Found, Salary Accuracy: 0.7560975609756098
'''


if __name__ == "__main__":
    print(datetime.now())

    sub_entries = os.listdir('C:/Users/Leon/BlockchainOpportunityAnalysis/NER')
    entries = []
    for i in sub_entries:
        if i[-9:] == 'train.txt':
            entries.append(i)

    index_json(entries)

    print(datetime.now())
