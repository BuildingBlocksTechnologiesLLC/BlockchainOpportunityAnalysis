import sys
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
from bs4 import BeautifulSoup
import requests
from date_extractor import extract_dates
import datefinder
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
def confirm_remote(text):
    """
    Confirm remote posting
    """
    r = re.compile(r'(?i)work from home|Work From Home| remotely') 
    matches = r.findall(text)
    if matches:
        return True
    r = re.compile(r'(?i)Remote')        
    indices = [m.start(0) for m in r.finditer(text)]
    rem_words = re.compile(r'(?i)only|100%| location')
    if rem_words.findall(text[indices[0]-30:indices[0]+30]):
        return True

    return False
def check_remote(text):
    """
    Check whether or not a posting is remote
    """
    r = re.compile(r'(?i)Remote|work from home|Work From Home| Remotely') 
    matches = r.findall(text)
    indices = [m.start(0) for m in r.finditer(text)]
    for i in indices:
        if ' not ' in text[i-6:i+20] or ' no ' in text[i-6:i+20] or ' Not ' in text[i-6:i+20] or ' No ' in text[i-6:i+20]:
            return False 
    return len(matches) != 0 

def check_state_title(text):
    """
    Look for common state abbreviations
    """
    states = re.compile('Alaska|Alabama|Alaska|Arizona|'+
    'Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|'+
    'Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|'+
    'Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|'+
    'North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|'+
    'South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming')
    state_abbr = re.compile(' AL| AK| AZ| AR| CA| CO| CT| DC| DE| FL| GA| HI| ID| IL| IN| IA| KS|'+
    ' KY| LA| ME| MD| MA| MI| MN| MS| MO| MT| NE| NV| NH| NJ| NM| NY| NC| ND| OH| OK| OR|'+
    ' PA| RI| SC| SD| TN| TX| UT| VT| VA| WA| WV| WI| WY')
    d_state = {
        ' AK': 'Alaska',
        ' AL': 'Alabama',
        ' AR': 'Arkansas',
        ' AS': 'American Samoa',
        ' AZ': 'Arizona',
        ' CA': 'California',
        ' CO': 'Colorado',
        ' CT': 'Connecticut',
        ' DC': 'District of Columbia',
        ' DE': 'Delaware',
        ' FL': 'Florida',
        ' GA': 'Georgia',
        ' GU': 'Guam',
        ' HI': 'Hawaii',
        ' IA': 'Iowa',
        ' ID': 'Idaho',
        ' IL': 'Illinois',
        ' IN': 'Indiana',
        ' KS': 'Kansas',
        ' KY': 'Kentucky',
        ' LA': 'Louisiana',
        ' MA': 'Massachusetts',
        ' MD': 'Maryland',
        ' ME': 'Maine',
        ' MI': 'Michigan',
        ' MN': 'Minnesota',
        ' MO': 'Missouri',
        ' MP': 'Northern Mariana Islands',
        ' MS': 'Mississippi',
        ' MT': 'Montana',
        ' NA': 'National',
        ' NC': 'North Carolina',
        ' ND': 'North Dakota',
        ' NE': 'Nebraska',
        ' NH': 'New Hampshire',
        ' NJ': 'New Jersey',
        ' NM': 'New Mexico',
        ' NV': 'Nevada',
        ' NY': 'New York',
        ' OH': 'Ohio',
        ' OK': 'Oklahoma',
        ' OR': 'Oregon',
        ' PA': 'Pennsylvania',
        ' PR': 'Puerto Rico',
        ' RI': 'Rhode Island',
        ' SC': 'South Carolina',
        ' SD': 'South Dakota',
        ' TN': 'Tennessee',
        ' TX': 'Texas',
        ' UT': 'Utah',
        ' VA': 'Virginia',
        ' VI': 'Virgin Islands',
        ' VT': 'Vermont',
        ' WA': 'Washington',
        ' WI': 'Wisconsin',
        ' WV': 'West Virginia',
        ' WY': 'Wyoming'
        }
    abbr = state_abbr.findall(text)
    full = states.findall(text)
    state = ''
    if abbr:
        state = d_state[abbr[0]]
    if full:
        state = full[0]
    return state

def check_state_body(text):
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
    ab_ind = [m.start(0) for m in state_abbr.finditer(text)]
    full = states.findall(text)
    f_ind = [m.start(0) for m in states.finditer(text)]
    state = ''
    if full and abbr:
        if ab_ind[0] > f_ind[0] and ab_ind[0] - f_ind[0]+len(full[0])-1 >3:
            state = full[0]
        else:
            state = d_state[abbr[0]]
    elif full:
        state = full[0]
    elif abbr:
        state = d_state[abbr[0]]
    return state

def regex_location(text):
    """
    Find location in the body
    """
    text = text.replace('Asia','')
    loc = GeoText(text)
    if loc.cities:
        city = loc.cities[0]
        g_cit = GeoText(city)
        if 'US' in g_cit.country_mentions:
            i = text.index(city)+len(city)
            state = check_state_body(text[i:])
            if state != '':
                return city+', '+state+', '+'United States'
            else:
                c = GeoText(city).country_mentions
                return city+', '+ list(c)[0]
        elif loc.countries and list(GeoText(loc.countries[0]).country_mentions)[0] in g_cit.country_mentions:
            return city+', '+loc.countries[0]
        else:
            return city+', '+list(g_cit.country_mentions)[0]
    elif loc.countries:
        return loc.countries[0]

    return 'Not Found'

def nlp_title(text,tagger):
    """
    Retrieve information from title line
    """
    tokenized_text = word_tokenize(text)
    classified_text = tagger.tag(tokenized_text)
    loc = []
    name = []
    org_name = 'Not Found'
    location = 'Not Found'
    prev = ''
    city = False
    org = False


    for (t,lab) in classified_text:
        if t in string.punctuation:
            prev = ''
        elif lab == 'LOCATION':
            if prev == 'LOCATION':
                loc.append(loc[-1]+' '+t)
            else:
                loc.append(t)
            prev = 'LOCATION'
        elif lab == 'ORGANIZATION':
            if prev == 'ORGANIZATION':
                name.append(name[-1]+' '+t)
            else:
                name.append(t)
            prev = 'ORGANIZATION'
        else:
            prev = ''

    try:
        loc_index = text.rfind(' in ')
        loc_end = text.index(r'\|| at ',loc_index)
        location = text[loc_index+4:loc_end-1]
    except ValueError:
        location = 'Not Found'

    if location == 'Not Found':
        state_r = re.compile(' AL | AK | AZ | AR | CA | CO | CT | DC | DE | FL | GA | HI | ID | IL | IN | IA | KS |'+
    ' KY | LA | ME | MD | MA | MI | MN | MS | MO | MT | NE | NV | NH | NJ | NM | NY | NC | ND | OH | OK | OR |'+
    ' PA | RI | SC | SD | TN | TX | UT | VT | VA | WA | WV | WI | WY ')
        states = state_r.findall(text)
        s_ind = [m.start(0) for m in state_r.finditer(text)]
        if states:
            state_loc_1 = text[:s_ind[0]-1].rfind(' ')
            state_loc_2 = text[:state_loc_1].rfind(' ')
            state_loc = text[:state_loc_2].rfind(' ')
            location = regex_location(text[state_loc:s_ind[0]+4])
        else:
            location = regex_location(text)

    if location != 'Not Found':
        city = True
    if location == 'Not Found':
        if loc:
            location = loc[-1]
        else:
            location = 'Not Found'
    if check_remote(text):  
        location = 'Remote'

    find_at = re.compile(r' at ',re.IGNORECASE)
    punct = re.compile(r'\||\-|\/|\:|\;|\\|\)|\}')
    if find_at.findall(text):
        text_post = text[text.index(' at '):]
        abbr_re = re.compile('Inc |LLC|Co |Ltd|.com|.org|.net')
        abb = abbr_re.findall(text_post)
        abbrev = [m.start(0) for m in abbr_re.finditer(text_post)]
        if punct.findall(text_post):
            org_name = text_post[4:text_post.index(punct.findall(text_post)[0])-1]
        elif abbrev:
            at_i = text_post[0:abbrev[0]+len(abb[0])].rfind(' at ')
            org_name = text_post[at_i+4:abbrev[0]+len(abb[0])]
        else:
            org_name = text_post[4:]


    if org_name == 'Not Found':      
        abbr_re = re.compile(r'(?i)[ |, |,]Inc|[ |, |,]LLC|[ |, |,]Co |[ |, |,]Ltd|\.com|\.org|\.net')
        abb = abbr_re.findall(text)
        abbrev = [m.start(0) for m in abbr_re.finditer(text)]
        if abbrev:
            if punct.findall(text[:abbrev[0]]):
                t = text[:abbrev[0]+len(abb[0])]
                s = [m.start(0) for m in punct.finditer(t[:-(len(abb[0])+1)])]
                org_name = t[s[-1]+1:]

    if org_name != 'Not Found':
        org = True
    if name and org_name == 'Not Found':
        org_name = name[-1]
    return location.strip(), org_name.strip(),city, org

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
        sal_range_re = re.compile('\-| to ')
        sal_range = sal_range_re.findall(text)
        indices = [m.start(0) for m in sal_range_re.finditer(text)]

        for i in indices:
            re_dol = re.compile('\$',re.IGNORECASE) 
            dol = re_dol.findall(text)
            fir_t = text[:i-3].rfind(' ') 
            try:
                l_t = text[i+4:].index(' ')
            except ValueError:
                l_t = 0
            salary_dol = text[i-(i-fir_t):i+4+l_t]
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
    if len(salary.split(' ')) <= 3:
        return salary
    else:
        return ' '.join(salary.split(' ')[-4:])

def remove_keywords(text):
    r = re.compile(r"(?i) ordered_list['|\-|.|,| ]| ERP['|\-|.|,| ]| ETL['|\-|.|,| ]| qualifications['|\-|.|,| ]| platform operations | benefits['|\-|.|,| ]| native['|\-|.|,| ]| about['|\-|.|,| ]| \.net['|\-|.|,| ]| crypto['|\-|.|,| ]| 3gpp['|\-|.|,| ]| 4gpp['|\-|.|,| ]| acceptance test['|\-|.|,| ]| agile['|\-|.|,| ]| Blockchain['|\-|.|,| ]| blockchain['|\-|.|,| ]| blockchain interoperability['|\-|.|,| ]| interoperability['|\-|.|,| ]| interoperable['|\-|.|,| ]| full time['|\-|.|,| ]| fulltime['|\-|.|,| ]| full\-time['|\-|.|,| ]| ai['|\-|.|,| ]| algorithms['|\-|.|,| ]| algorithm['|\-|.|,| ]| alteryx['|\-|.|,| ]| amelia['|\-|.|,| ]| aml['|\-|.|,| ]| anti money laundering['|\-|.|,| ]| financial exchanges['|\-|.|,| ]| digital asset exchange['|\-|.|,| ]| analytical['|\-|.|,| ]| analytical and problem solving['|\-|.|,| ]| laravel['|\-|.|,| ]| analytical generics['|\-|.|,| ]| android['|\-|.|,| ]| angular['|\-|.|,| ]| angularjs['|\-|.|,| ]| ansible['|\-|.|,| ]| appliation architecture['|\-|.|,| ]| application apis['|\-|.|,| ]| application development['|\-|.|,| ]| artificial intelligence['|\-|.|,| ]| asset management['|\-|.|,| ]| asset tokenization['|\-|.|,| ]| aws['|\-|.|,| ]| azure['|\-|.|,| ]| babel['|\-|.|,| ]| back end['|\-|.|,| ]| backend['|\-|.|,| ]| banking['|\-|.|,| ]| digital banking['|\-|.|,| ]| beacon['|\-|.|,| ]| beacon chain['|\-|.|,| ]| big data['|\-|.|,| ]| bigdata['|\-|.|,| ]| bigchain db['|\-|.|,| ]| bitcoin['|\-|.|,| ]| stable coin['|\-|.|,| ]| stablecoin['|\-|.|,| ]| middleware['|\-|.|,| ]| non custodial['|\-|.|,| ]| custodial['|\-|.|,| ]| scarcity token['|\-|.|,| ]| loans['|\-|.|,| ]| bitcoin 2\.0['|\-|.|,| ]| blockchain agnostic['|\-|.|,| ]| blockchain architecture['|\-|.|,| ]| blockchain based['|\-|.|,| ]| blockchain developer['|\-|.|,| ]| product manager['|\-|.|,| ]| product management['|\-|.|,| ]| senior consultant['|\-|.|,| ]| platform developer['|\-|.|,| ]| blockchain platforms['|\-|.|,| ]| blockchain research['|\-|.|,| ]| blockchain services['|\-|.|,| ]| blockstack['|\-|.|,| ]| business development['|\-|.|,| ]| business intelligence['|\-|.|,| ]| loyalty programs['|\-|.|,| ]| hedge funds['|\-|.|,| ]| hedge fund['|\-|.|,| ]| edtech['|\-|.|,| ]| legal tech['|\-|.|,| ]| cannabis['|\-|.|,| ]| online auctions['|\-|.|,| ]| c['|\-|.|,| ]| c\+\+['|\-|.|,| ]| capital markets['|\-|.|,| ]| cellular network['|\-|.|,| ]| chaincode['|\-|.|,| ]| chef['|\-|.|,| ]| ci cd['|\-|.|,| ]| circuit design['|\-|.|,| ]| clarity['|\-|.|,| ]| clarity smart language['|\-|.|,| ]| cloud['|\-|.|,| ]| cloud computing['|\-|.|,| ]| cloud experience['|\-|.|,| ]| cloud services['|\-|.|,| ]| cognitive automation['|\-|.|,| ]| cognitive systems['|\-|.|,| ]| collaboration['|\-|.|,| ]| communication generics['|\-|.|,| ]| interoperability platform['|\-|.|,| ]| interoperable  blockchain['|\-|.|,| ]| staking['|\-|.|,| ]| consensus['|\-|.|,| ]| consensus algorithms['|\-|.|,| ]| containerization['|\-|.|,| ]| containers['|\-|.|,| ]| continuous deployment['|\-|.|,| ]| continuous integration['|\-|.|,| ]| corda['|\-|.|,| ]| cosmos['|\-|.|,| ]| cosmos sdk['|\-|.|,| ]| couchdb['|\-|.|,| ]| crawling['|\-|.|,| ]| cross chain['|\-|.|,| ]| cross\-chain['|\-|.|,| ]| credential information['|\-|.|,| ]| crypto enthusiast['|\-|.|,| ]| crypto wallet['|\-|.|,| ]| cryptoasset['|\-|.|,| ]| cryptoassets['|\-|.|,| ]| cryptocurrencies['|\-|.|,| ]| cryptocurrency['|\-|.|,| ]| cryptocurrency for payments['|\-|.|,| ]| cryptographic principles['|\-|.|,| ]| cryptographic protocols['|\-|.|,| ]| cryptography['|\-|.|,| ]| protocol developer['|\-|.|,| ]| mobile payments['|\-|.|,| ]| mobile apps['|\-|.|,| ]| predictive analytics['|\-|.|,| ]| crowdfunding['|\-|.|,| ]| parachain['|\-|.|,| ]| voting['|\-|.|,| ]| backbone['|\-|.|,| ]| embedded['|\-|.|,| ]| css['|\-|.|,| ]| cyber['|\-|.|,| ]| cyber security['|\-|.|,| ]| dao['|\-|.|,| ]| dapps['|\-|.|,| ]| data & analytics['|\-|.|,| ]| analytics['|\-|.|,| ]| data aggragation['|\-|.|,| ]| data analytics['|\-|.|,| ]| data science['|\-|.|,| ]| data structures['|\-|.|,| ]| data warehousing['|\-|.|,| ]| dataiku['|\-|.|,| ]| datarobot['|\-|.|,| ]| debugging testing generics['|\-|.|,| ]| decentralized applications['|\-|.|,| ]| decentralised['|\-|.|,| ]| decentralised autonomous organisations['|\-|.|,| ]| decentralised finance['|\-|.|,| ]| decentralised systems['|\-|.|,| ]| decentralized['|\-|.|,| ]| decentralized autonomous organizations['|\-|.|,| ]| decentralized finance['|\-|.|,| ]| decentralized systems['|\-|.|,| ]| decntralized reputation systems['|\-|.|,| ]| defi['|\-|.|,| ]| deliver production['|\-|.|,| ]| design patterns['|\-|.|,| ]| developing and deploying['|\-|.|,| ]| devops['|\-|.|,| ]| digital asset['|\-|.|,| ]| digital asset platform['|\-|.|,| ]| digital assets['|\-|.|,| ]| digital transofrmation['|\-|.|,| ]| disruptive['|\-|.|,| ]| disruptive solutions['|\-|.|,| ]| disruptive technologies['|\-|.|,| ]| distributed application['|\-|.|,| ]| distributed applications['|\-|.|,| ]| distributed ledger['|\-|.|,| ]| ledger technology['|\-|.|,| ]| ledger technologies['|\-|.|,| ]| online games['|\-|.|,| ]| gaming['|\-|.|,| ]| gambling['|\-|.|,| ]| distributed systems['|\-|.|,| ]| django['|\-|.|,| ]| advertising['|\-|.|,| ]| dlt['|\-|.|,| ]| dlt service['|\-|.|,| ]| docker['|\-|.|,| ]| rancher['|\-|.|,| ]| drizzle['|\-|.|,| ]| e\-commerce['|\-|.|,| ]| e commerce['|\-|.|,| ]| marketplace['|\-|.|,| ]| ecma script['|\-|.|,| ]| ecmascript['|\-|.|,| ]| ecr['|\-|.|,| ]| elastic search['|\-|.|,| ]| elasticsearch['|\-|.|,| ]| electromagnetic['|\-|.|,| ]| emerging technologies['|\-|.|,| ]| encryption['|\-|.|,| ]| encryption signatures['|\-|.|,| ]| enterprise blockchain software['|\-|.|,| ]| enterprise software['|\-|.|,| ]| erlang['|\-|.|,| ]| eth['|\-|.|,| ]| eth 2\.0['|\-|.|,| ]| ethereum['|\-|.|,| ]| ethereum 2\.0['|\-|.|,| ]| ethereumjs['|\-|.|,| ]| ethers\.js['|\-|.|,| ]| etl['|\-|.|,| ]| ewasm['|\-|.|,| ]| fabric['|\-|.|,| ]| finance['|\-|.|,| ]| financial['|\-|.|,| ]| financial application['|\-|.|,| ]| financial services['|\-|.|,| ]| financial solutions['|\-|.|,| ]| financial technology['|\-|.|,| ]| fintech['|\-|.|,| ]| fpga['|\-|.|,| ]| fpga design['|\-|.|,| ]| frameworks['|\-|.|,| ]| fraud['|\-|.|,| ]| fraud detection['|\-|.|,| ]| front end['|\-|.|,| ]| frontend['|\-|.|,| ]| full stack['|\-|.|,| ]| fullstack['|\-|.|,| ]| functional test['|\-|.|,| ]| test automation['|\-|.|,| ]| functional program['|\-|.|,| ]| compliance['|\-|.|,| ]| strategic planning['|\-|.|,| ]| risk management['|\-|.|,| ]| information technology['|\-|.|,| ]| ganache['|\-|.|,| ]| genetic['|\-|.|,| ]| geth['|\-|.|,| ]| parity['|\-|.|,| ]| besu24['|\-|.|,| ]| multigeth['|\-|.|,| ]| multi\-chain['|\-|.|,| ]| multi chain['|\-|.|,| ]| para\-chain['|\-|.|,| ]| para chain['|\-|.|,| ]| middleware['|\-|.|,| ]| graph theory['|\-|.|,| ]| nethermind['|\-|.|,| ]| forensic['|\-|.|,| ]| git['|\-|.|,| ]| github['|\-|.|,| ]| golang['|\-|.|,| ]| gpus['|\-|.|,| ]| gradle['|\-|.|,| ]| graphql['|\-|.|,| ]| hadoop['|\-|.|,| ]| hardware developer['|\-|.|,| ]| hardware engineer['|\-|.|,| ]| hash functions['|\-|.|,| ]| haskell['|\-|.|,| ]| hbase['|\-|.|,| ]| healthcare['|\-|.|,| ]| health care['|\-|.|,| ]| health industry['|\-|.|,| ]| health organizations['|\-|.|,| ]| high performance computing['|\-|.|,| ]| html['|\-|.|,| ]| html5['|\-|.|,| ]| hyperledger['|\-|.|,| ]| exchanges['|\-|.|,| ]| ico['|\-|.|,| ]| identity management['|\-|.|,| ]| identity managment['|\-|.|,| ]| identity protocols['|\-|.|,| ]| information systems['|\-|.|,| ]| infura['|\-|.|,| ]| instanbul['|\-|.|,| ]| intellectual curiosity['|\-|.|,| ]| intellij['|\-|.|,| ]| internet of things['|\-|.|,| ]| investment funds['|\-|.|,| ]| iot['|\-|.|,| ]| ipfs['|\-|.|,| ]| j2ee['|\-|.|,| ]| java['|\-|.|,| ]| javascript['|\-|.|,| ]| jira['|\-|.|,| ]| jquery['|\-|.|,| ]| js frameworks['|\-|.|,| ]| jscript['|\-|.|,| ]| json['|\-|.|,| ]| json\-rpc['|\-|.|,| ]| kafka['|\-|.|,| ]| kanban['|\-|.|,| ]| kendo ui['|\-|.|,| ]| kmi['|\-|.|,| ]| kotlin['|\-|.|,| ]| automated testing['|\-|.|,| ]| quality engineer['|\-|.|,| ]| sofware engineer['|\-|.|,| ]| sofware developer['|\-|.|,| ]| kovan['|\-|.|,| ]| kubernetes['|\-|.|,| ]| kyc['|\-|.|,| ]| know your customer['|\-|.|,| ]| threat modeling['|\-|.|,| ]| layer 2['|\-|.|,| ]| layer\-2['|\-|.|,| ]| large scale deployment['|\-|.|,| ]| lending platforms['|\-|.|,| ]| libra network['|\-|.|,| ]| lightning network['|\-|.|,| ]| linux['|\-|.|,| ]| lisp['|\-|.|,| ]| litecoin['|\-|.|,| ]| logic circuit['|\-|.|,| ]| machine learning['|\-|.|,| ]| mainnet['|\-|.|,| ]| matlab['|\-|.|,| ]| maven['|\-|.|,| ]| merkle tree['|\-|.|,| ]| patricia tree['|\-|.|,| ]| metamask['|\-|.|,| ]| micro services['|\-|.|,| ]| microservices['|\-|.|,| ]| monero['|\-|.|,| ]| mongo['|\-|.|,| ]| mongo db['|\-|.|,| ]| mongodb['|\-|.|,| ]| mqtt['|\-|.|,| ]| multi currency['|\-|.|,| ]| multi currency wallet['|\-|.|,| ]| multithreading['|\-|.|,| ]| mysql['|\-|.|,| ]| natural language procesing['|\-|.|,| ]| network security['|\-|.|,| ]| nlg['|\-|.|,| ]| nlp['|\-|.|,| ]| nlu['|\-|.|,| ]| node js['|\-|.|,| ]| node\.js['|\-|.|,| ]| nodejs['|\-|.|,| ]| nodeops['|\-|.|,| ]| nosql['|\-|.|,| ]| npm['|\-|.|,| ]| numpy['|\-|.|,| ]| object model['|\-|.|,| ]| object oriented['|\-|.|,| ]| object oriented design['|\-|.|,| ]| object oriented programming['|\-|.|,| ]| off chain['|\-|.|,| ]| off\-chain['|\-|.|,| ]| open source technologies['|\-|.|,| ]| open source tools['|\-|.|,| ]| opencl['|\-|.|,| ]| opensource['|\-|.|,| ]| p2p['|\-|.|,| ]| parallel programming['|\-|.|,| ]| patrecia trees['|\-|.|,| ]| peer to peer['|\-|.|,| ]| peer\-to\-peer['|\-|.|,| ]| collectible asset['|\-|.|,| ]| digital collectible['|\-|.|,| ]| pgp['|\-|.|,| ]| pharma['|\-|.|,| ]| pharmaceutical['|\-|.|,| ]| civictech['|\-|.|,| ]| polygot['|\-|.|,| ]| pos['|\-|.|,| ]| postgres['|\-|.|,| ]| pow['|\-|.|,| ]| augmented reality['|\-|.|,| ]| virtual reality['|\-|.|,| ]| virtual reality['|\-|.|,| ]| smart blem solving generics['|\-|.|,| ]| proof of stake['|\-|.|,| ]| proof of work['|\-|.|,| ]| protocols['|\-|.|,| ]| public blockhain['|\-|.|,| ]| public key encryption['|\-|.|,| ]| public keys['|\-|.|,| ]| puppet['|\-|.|,| ]| python['|\-|.|,| ]| quantum computing['|\-|.|,| ]| quasar['|\-|.|,| ]| quorum['|\-|.|,| ]| r3 corda['|\-|.|,| ]| rabbit mq['|\-|.|,| ]| rdbms['|\-|.|,| ]| react['|\-|.|,| ]| react\.js['|\-|.|,| ]| prediction market['|\-|.|,| ]| prediction markets['|\-|.|,| ]| real estate['|\-|.|,| ]| realestate['|\-|.|,| ]| remix['|\-|.|,| ]| repuation systems['|\-|.|,| ]| restful apis['|\-|.|,| ]| ripple['|\-|.|,| ]| rootstock['|\-|.|,| ]| ropsten['|\-|.|,| ]| rpc['|\-|.|,| ]| rsk['|\-|.|,| ]| ruby['|\-|.|,| ]| rust['|\-|.|,| ]| sass['|\-|.|,| ]| scala['|\-|.|,| ]| scikit['|\-|.|,| ]| scripting['|\-|.|,| ]| scrum['|\-|.|,| ]| code review['|\-|.|,| ]| sdk['|\-|.|,| ]| sdlc['|\-|.|,| ]| security and  identity management['|\-|.|,| ]| security with identity management['|\-|.|,| ]| serenity['|\-|.|,| ]| server side language['|\-|.|,| ]| smart contract['|\-|.|,| ]| smart grids['|\-|.|,| ]| side\-chain['|\-|.|,| ]| side chain['|\-|.|,| ]| smt checker['|\-|.|,| ]| social good['|\-|.|,| ]| social impact['|\-|.|,| ]| social network['|\-|.|,| ]| solidity['|\-|.|,| ]| solr['|\-|.|,| ]| spark['|\-|.|,| ]| spring boot['|\-|.|,| ]| sql['|\-|.|,| ]| trading['|\-|.|,| ]| staker['|\-|.|,| ]| standards protocols['|\-|.|,| ]| startup['|\-|.|,| ]| stellar['|\-|.|,| ]| stellar core['|\-|.|,| ]| sto['|\-|.|,| ]| subscription based['|\-|.|,| ]| substrate['|\-|.|,| ]| supply chain['|\-|.|,| ]| supply chains['|\-|.|,| ]| swift['|\-|.|,| ]| systems implementation['|\-|.|,| ]| tableau['|\-|.|,| ]| tcl['|\-|.|,| ]| tdd['|\-|.|,| ]| tendermint['|\-|.|,| ]| teneo['|\-|.|,| ]| terraform['|\-|.|,| ]| test driven development['|\-|.|,| ]| testnet['|\-|.|,| ]| tokenization['|\-|.|,| ]| tokenomics['|\-|.|,| ]| trinity['|\-|.|,| ]| truffle['|\-|.|,| ]| typescript['|\-|.|,| ]| ui ux['|\-|.|,| ]| unit and functional test['|\-|.|,| ]| unit test['|\-|.|,| ]| user facing['|\-|.|,| ]| utility token['|\-|.|,| ]| validator['|\-|.|,| ]| vector analysis['|\-|.|,| ]| verilog['|\-|.|,| ]| vhdl['|\-|.|,| ]| viper['|\-|.|,| ]| visualization['|\-|.|,| ]| vyper['|\-|.|,| ]| waffle['|\-|.|,| ]| wallet['|\-|.|,| ]| wasm['|\-|.|,| ]| web applications['|\-|.|,| ]| web\-2['|\-|.|,| ]| web2['|\-|.|,| ]| web 2['|\-|.|,| ]| web\-3['|\-|.|,| ]| web3['|\-|.|,| ]| web 3['|\-|.|,| ]| web3\.py['|\-|.|,| ]| webassembly['|\-|.|,| ]| webpack['|\-|.|,| ]| websocket['|\-|.|,| ]| wireframes['|\-|.|,| ]| wireframs['|\-|.|,| ]| workfusion['|\-|.|,| ]| z\-cash['|\-|.|,| ]| zcash['|\-|.|,| ]| zero knowledge['|\-|.|,| ]| zero knowledge proof['|\-|.|,| ]| zkp['|\-|.|,| ]| zokrates['|\-|.|,| ]| zookeeper")    
    return r.sub(' ',text)

def nlp_body(text,tagger):
    """
    Retrieve information from body
    """
    r = re.compile(r'\\u')
    s_text = r.sub('',text)
    text = (text.encode('ascii', 'ignore')).decode("utf-8")

    regex = re.compile('[^a-zA-Z\-\|\,0-9\+]')
    re_text = regex.sub(' ',text)

    re_text = remove_keywords(re_text)
    l = re_text[:(len(re_text)*9)//10].rfind(' ')
    re_text = re_text[:l]
    loc = []
    name = []
    loc_re =  re.compile('location[:| | :]',re.IGNORECASE)
    loc_ind = [m.start(0) for m in loc_re.finditer(re_text)]
    location = 'Not Found'
    date_remove = re.compile(r'(?i) date | nice | manage | mentor')
    city = False
    remote = False
    if loc_ind:
        location = regex_location(re.sub(date_remove, '', re_text[loc_ind[0]:loc_ind[0]+60]))
        
    if location == 'Not Found':
        state_r = re.compile(' AL | AK | AZ | AR | CA | CO | CT | DC | DE | FL | GA | HI | ID | IL | IN | IA | KS |'+
    ' KY | LA | ME | MD | MA | MI | MN | MS | MO | MT | NE | NV | NH | NJ | NM | NY | NC | ND | OH | OK | OR |'+
    ' PA | RI | SC | SD | TN | TX | UT | VT | VA | WA | WV | WI | WY ')
        states = state_r.findall(re_text)
        s_ind = [m.start(0) for m in state_r.finditer(re_text)]
        if states:
            state_loc_1 = re_text[:s_ind[0]-1].rfind(' ')
            state_loc = re_text[:state_loc_1].rfind(' ')
            check_city = re_text[state_loc:s_ind[0]+4].split(' ')
            cc = []
            for i in check_city:
                if i != '':
                    if i not in' AL AK AZ | AR | CA | CO | CT | DC | DE | FL | GA | HI | ID | IL | IN | IA | KS | KY | LA | ME | MD | MA | MI | MN | MS | MO | MT | NE | NV | NH | NJ | NM | NY | NC | ND | OH | OK | OR | PA | RI | SC | SD | TN | TX | UT | VT | VA | WA | WV | WI | WY ':
                        cc.append(i.lower().capitalize())
                    else:
                        cc.append(i+' ')
            n = word_tokenize(' '.join(cc))

            if not GeoText(' '.join(cc)).cities and cc:
                cc[0] = ''

            t = ' '.join(cc)
            location = regex_location(re.sub(date_remove, '', t))
            
            if location == 'Not Found':
                lct = tagger.tag(n)
                lo = ''
                for (word,tag) in lct:
                    if tag == 'LOCATION':
                        lo = lo+word+' '
                if lo !='':
                    location = lo

    if location == 'Not Found':
        location = regex_location(re.sub(date_remove, '', re_text))

    if location != 'Not Found':
       city = True
    state_r = re.compile(' AL | AK | AZ | AR | CA | CO | CT | DC | DE | FL | GA | HI | ID | IL | IN | IA | KS |'+
    ' KY | LA | ME | MD | MA | MI | MN | MS | MO | MT | NE | NV | NH | NJ | NM | NY | NC | ND | OH | OK | OR |'+
    ' PA | RI | SC | SD | TN | TX | UT | VT | VA | WA | WV | WI | WY ')
    re_text = state_r.sub('',re_text)
    tokenized_text = word_tokenize(re_text)
    classified_text = tagger.tag(tokenized_text)
       
    prev = ''
    for (t,lab) in classified_text:
        if t in string.punctuation:
            prev = ''
        elif lab == 'LOCATION':
            if prev == 'LOCATION':
                loc.append(loc[-1]+' '+t)
            else:
                loc.append(t)
            prev = 'LOCATION'
        elif lab == 'ORGANIZATION':
            if prev == 'ORGANIZATION':
                name.append(name[-1]+' '+t)
            else:
                name.append(t)
            prev = 'ORGANIZATION'
        else:
            prev = ''

    org_name = decide_org(np.array(name))

    if location == 'Not Found':
        location = decide_loc(np.array(loc))
    
    if check_remote(re_text):  
        location = 'Remote'
        if confirm_remote(re_text):
            remote = True

    salary = 'Not Found'
    date = 'Not Found'

    re_date = re.compile(r'(?i) date post[:| ]|date posted[:| ]| posted[:| ]| post[:| ]') 
    find_date = re_date.findall(re_text)
    if find_date:
        find_date = re_text[re_text.index(find_date[0])+len(find_date[0]):re_text.index(find_date[0])+30]
        if datefinder.find_dates(find_date):
            date_time = list(datefinder.find_dates(find_date))[0]
            date = date_time.strftime("%e %b %Y")

    re_date = re.compile(r'20[0-9][0-9]') 
    find_date = re_date.findall(re_text[:40])
    indices = [m.start(0) for m in re_date.finditer(re_text)]
    if find_date:
        fd = re_text[:indices[0]+4]
        date_loc_1 = fd[:indices[0]-1].rfind(' ')
        date_loc = fd[:date_loc_1].rfind(' ')
        find_date = re_text[date_loc:indices[0]+4]

        if datefinder.find_dates(find_date):
            date_time = list(datefinder.find_dates(find_date))[0]
            date = date_time.strftime("%e %b %Y")

    if date == 'Not Found':
        re_date = re.compile(r'\bmonths ago\b|\bdays ago\b|\bhours ago\b',re.IGNORECASE) 
        dtype = re_date.findall(re_text)
        if dtype:
            find_date = re_text[re_text.index(dtype[0])-4:re_text.index(dtype[0])+2]
            date_time = re.compile('[1-9][0-9][0-9]|[1-9][0-9]|[0-9]')
            date = date_time.findall(find_date)[0]+' '+dtype[0]
    
    salary = find_sal(s_text)
        
    return location.strip(), org_name.strip(), salary.strip(), date.strip(),city,remote

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
        loc_index = text.rfind(' in ')
        loc_end = text.index('|',loc_index)
        location = text[loc_index+4:loc_end-1]
    except ValueError:
        location = 'Not Found'

    if check_remote(text):  
        location = 'Remote'
    
    return location.strip(), org_name.strip()

def dice_title(text,tagger):
    org = text.split('- ')[-2]
    location = (text.split('- ')[-1]).split('|')[0]
    if check_remote(text):  
        location = 'Remote'
    return location, org

def simp_title(text):
    location = text.split(' | ')[-1]
    org = (text.split(' | ')[0]).split(' - ')[-1]
    if check_remote(text):  
        location = 'Remote'
    return location, org
def blocktribeorg(prev,text):
    
    r = re.compile(r"\(ASTRI\) Hong Kong Applied Science and Technology Research Institute Company Limited | 1000Spartans | 1c0 | 21MIL | 310 Coin Launch | 4 Way Technologies | 55Exchange | 5g | aap3 | aap3 Recruitment | ABC | ABCC Exchange | AboveBoard | ABRA | Abra | Accelerate Enterprise Ltd | Accenture | Accredit HR Consultancy Pte Ltd | Acquaint Inc\. | adChain | administratormail | Adventure Pizza Incorporated | Aeonideq | Aggregion | AICO | Aicumen Technologies | Aicumen Technologies Inc | Airdrop Alert BV | AKASHA Foundation | Alba Holdings | Algorythma | Alkemi | Allforcrypto | Alluminate | Almond | AlphaPoint | Altoros | AmaZix | Amit 27 | anonymous | Antler | AnyLedger | APLA | AppTad Inc\. | ARK\.io | Asia Live Tech | Aspect Resources | Assembly | ASTRI | Athena Bitcoin, Inc | Atlas City | Australasian Blockchain Music Association | Automata | Autonomos Capital | Awesome Gaming Pte Ltd | Axiom Zen | Axoni | Axoni | AZTEC protocol | Bancambios Financial Technologies | banque HODL | BC Group | Bdtask Limited | BeInCrypto | BF-Fi | BiblePay | Big Couch Ltd | BiGGChain Ltd | Binary\.com | Bit Refill | BitAccess | BitCarbon | Bitcoin | Bitcoin PR Buzz | Bitcoin\.com | Bitdeal | Bitdeal | Bitdeal | Bitfinex | bitfish | bitfish | bitfish | Bitflyer | bitFlyer EUROPE | Bitgosu Ltd\. | Bitinka | Bitkey technologies | BitMarket | Bitpay | Bitrefill | Bitstamp | Bitwage | Bleumi inc | BLK\.io | Block Gemini | Block Recruiters | BlockAble | BlockApps | Blockbid | Blockblox | Blockblox LLC | Blockchain | Blockchain Consulting GmbH | Blockchain development company- Developcoins | Blockchain Education Initiative | Blockchain Headhunter | Blockchain Healthcare Review | Blockchain Help | Blockchain People | Blockchain Rec | Blockchain Smart Technologies | Blockchain startup \(stealth mode\) | Blockchain Talent Acquisition Ltd | blockchain Technology | Blockchain Works | Blockchain XP | Blockchainappsdeveloper | BlockchainCareerbuilders | blockchaindevelopers\.net | Blockchainhub Prague | Blockchaininvest | BlockCi | BlockFactory ag | Blockfreight™ | Blockgeeks | Blockhire | BlockIvy | blockrize | Blocksmith | BlockState | Blockstate | Blockstream | Blocktel | Blocktribe | Blockwise Ltd\. | Blokur | BlueQbit | BNYMellon | Boltt Coin\.io | brainbot technologies AG | Braintrust | Breakthrough Innovation Lab | bridge21 | British Blockchain Frontier Technologies Association | Broctagon | BTCC | bullcatalyst | BurstIQ | Business Blockchain HQ | Cairn Energy | Cambridge Blockchain, LLC | Cander Group | Capital Match | CARPHONE WAREHOUSE | Cashback Script - CashCraft | Catradora | Caviar | Chainera | Chainlink | Chainlink | ChainSecurity AG | Chainstarter | Charles Levick | Charles Levick | Chorus One | Chronicled | Circle | CK Technical | Clause | Clear Stream | ClearCube Consulting | Clearmatics | CleverTech | Clevertech | Clink | Close Cross Ltd | cloudmlmsoftware | CME Group | Coaddrex | coderkube | Coin Cloud | Coin Developer India | Coin Metric | CoinAdvisor | Coinbase | Coincover | Coinect\.ai | Coinjoker | Coinjoker | Coinomi Wallet | CoinRating | Coinsclone | Coinsclone | Coinstruct | Colendi | Colony | ComedyPlay | Confidential | Conflux | Coral Health Research & Discovery | Cornucopia | Cornucopia IT | CottageCase | COUTURE SEARCH LLC | Cowork Unite | Cricket\.me | Cryptexxx | Crypto App factory | Crypto Asset Rating | Crypto Infos | Crypto Profits | Crypto Research Group, Inc\. | Cryptocurrency Exchange Script - BlockchainAppsDeveloper | CryptoHorse | Cryptomnia | CryptoRated | Cryptorecruit | CryptoSoftwares | Curiositas\.io | Cyber Infrastructure | CYBER-GUARD ENTERPRISE LTD | CyFin Technologies OU | Daily Deals Coupon | DAO\.Casino | Dapper Labs | Darico | Dash Core Group | DealBook | Decent\.bet | delete | Deloitte Luxembourg | developcoins-cryptocurrency-development-company | Devio | Digital | Digital Asset Custody Company | Digital Assets Data Inc\. | Digital Billions | Digital Singularity Pte Ltd | Dignyfy | Direct Capital Investments | Dividendee | Divistock LLC | DoveTail Digital Ltd\. | Dovetail Lab | DOVU | dsfjsdfksdlfm | Durie Capital Management | EarthBenign | Eco | EDR Global Search | Elemential Labs | Elevate Digital | Elite Recruitment | elkrem | Elliptic | Elocity | Email processing | Embleema | EMIREX | Emotiq AG | Employcoder | Encrypted Reviews | Enecuum | Energo Labs | Enterprise Digital Resources | Enterprise Digital Resources Ltd | Enzyme Advising Group | EPRI | Equidato Technologies AG | Espay Exchange | ethereum | Ethereum Payments company | Etherparty | Etherparty | Everex | Everex | Everex | everis Consultancy Ltd | Evershine Co-Operative Society Bank | Eximchain | Experis | EXTNOC | ExxonMobil Company | factocert | Factocert Technologies Pvt Ltd | Factom, Inc\. | Farm Credit Canada | Favour house | FemtoWeb | Ferchau Engineering GmbH | Ferdon Inc | FieldEngineer | Finance Careers | Fintech Recruiters | Fintricity | Fintricity | Fintricity Consulting | First Universal Blockchain Services \(USA\) Inc | Fit4bond - Custom Tailoring Software Development Company | Flexiana | Fluent | Fluidity | Fluidity | Fold | FunFair Technologies | Game Period | Gatecoin | GBMiners | Gem | Glassbay | Globacap Limited | Global Crypto News | GlobeTrotter Cryptocurrency Ecosystem | GMP | GoldCub | Goldcub | goming\.co | Gordon | Gotaki Maps | Grace Themes | Grayblock Power | GRAYLL | H2 Industries SE | Halo Platform, LLC | HappyFunCorp | HappyMod | Harrisburg University of Science and Technology | Hedera Hashgraph | Herdius | HKEOS | Hosho Group | HRSource | Huff Consulting | Huobi Global | Hydrogen | Hyperledger Blockchain Development Company | HYSOOP COMPANY | IBC | IBM Client Innovation Center Benelux | ICO All IN | ICOBrands | ICOCLONE | ICOCLONE Security token offering services | iContract | identitii | iFixers | Ignite Digital Talent | Ikaros TIC Solvers | Immortality X | Immuto, Inc\. | In'saneLab | Incenti | Independent HR Specialist | Indie Storm | Infinity Blockchain Ventures | Information Assurance Platform | innogy Innovation Hub | Instant Systems Inc | Interlay | Intrepid ventures | IOHK | IOHK | IOV | isoconsultation | isolution design | Ivno\.io | JAAK | Jaspercoin | Job Compass | Jobs in Crypto | John Hancock | John wick | Kairos Search | Kerr | Keyrock | Kinesis Money | Kinex Media | Kingsland University | Kite Human Capital | Kite Human Capital | Kiva\.org | KnowledgeGRIDS | Komodo | Konkrete | Kraken Digital Asset Exchange | Krypc Technologies Inc\. | Krypital Group | Kyokan | lalalala | Larson Resource Group | LAToken | LCX | Leaptrade | Learning Blocks | Leax LCC | Left | Leonovus | Leonovus | LibertyX | Liquid Falcon | London Crypto Services Ltd | Lovdoc | lucidCircus | Lunar Digital Assets | LunarExpress | Luno | Luxe Equity | Macandro | Maclean Moore | MadHive | Maicoin | Manpower Staffing Services \(S\) Pte Ltd | Manulife/John Hancock | Marbrox | Market Protocol | MARS Technologies | Master Ventures | Maticz Technologies | MCCR Recruitment | MedBlock | Mediachain Labs | Medvice | MenuBuzz | Metal | meterqubes | Meterqubes Solutions LLC | MiiBits | Millennium Crypto Mining | Miracle Tele | Mishalov Enterprises LLC | MNPG | MNR Solutions Private Limited | Mobius | Modeneis | Modis IT | Monax | Monetum | moneytis | Monsanto | Moon Assist | Mosaic | MotusWare Pty Ltd | MPCX Platform Limited | Mr | Mr | mun | Neutral | New Economy Fund | New Era Tech | NextID Pte Ltd | Nextwin | nhsprofessionals | Ninja | Nitro Interactive Limited | Niyogin Fintech | none | NonStop Recruitment Schweiz AG | O&J Group | OCI | Odoo Customization | OEL Foundation | OKEX | OKEX Technology Company Limited | OKLink Technology Company Limited | OMINEX | OmniN0de | Omnitude | Onai | Open Search Network | Opentopic | OpptIn | OPSkins / WAX Token | Orbit Search | OTC Exchange Network | Otonomos | P2P Models | Pacific Block Technology Corp\. | Pave | Pfizer | Pfizer Inc\. | Phoenix Payments Ltd | PixelPlex | Planning korea | Plexus | Plexus Resource Solution | Plexus Resource Solutions | Plexus Resource Solutions | Plexus Resource Solutions | Plexus Resource Solutions | Plexus Resource Solutions | Plexus Resource Solutions | Plexus RS | PlexusRS | Poloniex | Polymath | Poolin | POSaBIT | Power Ledger | Pragmatic Coders | Priority Token | Private \(Boutique trading firm\) | Privax | Profile 29 | Project Hydro | Propine Technologies Pte Ltd | Protoblock | Pulsar Trading Captial | Pulsehyip | Pulsehyip | Pulsehyip | Q Ventures | QED-it | Qredo | Qualified Demand | Quant Network | quest global technologies | Quillhash Technologies | RADAR | RDA Recruitment Limited | Realm Labs | RealT Inc\. | Reckoon | RECRUITERS | Rehuman Inc\. | Reph Recruiting | Reserve Protocol | Rewards Blockchain | REX | Robot Vera | Rockchain | Rondo | Rowlingstone | Sakaeru Limited | Salamantex | Salamantex GmbH | Salt | Satoshi Systems Ltd | Sean Woods - Director | Searchie & Searchie | SecureBlocks | Selfkey Foundation | sellbitbuy | Sellbitbuy | SellBloc | SettleMint | SettleMint | SGS Consulting | Share&Charge | Shelf\.Network | Shift Markets | Shivom | SHIVOM | SHIVOM | SignedBlock | Signity Solutions | SIGNiX, Inc | Silverlink Technology | SimplyVital Health | Sinergia Gestão de Pessoas | Skillsearch Limited | SKT Themes | SLBK | SMART VALOR | SmartContract Thailand | Smoogs\.io | Soarlabs\.org | Social Impact | Socieum | Solarheap | Solve\.care | SONM USA | Source Technology | Spacesoft LLC | SparkPR | Spectrus Informatics Pvt Ltd | SplashBI | SportsCastr | SportVEST | SpotnEatsy Capital | Sym Social Inc\. | Synereo | TAIA | talentBLOCK | TalentXD | TAP | TapTrust | TBC US | TBD | TBD | Tech29 | TEKsystems Singapore | Tekton | Tencoins Ltd\. | Ternio | The Arcadia Group | The Bitcoin Boutique | The Happy Beavers | The Lion | The Merkle Labs | The Millennial Company | The Pillar Project and 2030 | The Simplify Market | The Vanbex Group | Thesis | Tides - Decentralized Health Insurance | Tierion | Tipstat | TMP Worldwide | TMP Worldwide | Token Foundry @ ConsenSys | TokenTax | Tontine Trust | TOP Network | TradeIX | TransferUp | Trinity Connected | TrueCover | TruStory | Tryshifu | Turing Talent | Turing Talent | Tusk Philanthropies | Tykn\.tech | U\.CASH | Ubitquity | ULab | UNISOT | United Blockchain Group | University of Hamburg | Untappt LLC | Uphold | Upvest | V Systems Limited | Vairus World Tech | Vareger | vasa | Vectorspace\.ai | Velmie | Velocium LTD | Velosys | VeloxChain | Venture Exchange - VNX | Verasity | Vereign AG | VeryFile Sagl | Vitwit | VoozoDealer | vrpfencingcontractors | VTNGLOBAL, INC\. | Wachsman PR | Wanchain | Wealthsimple | Web3 Foundation | Winning Team | Wipro | WKL consultancy | Wmachine | Wolf | Workagency | XEEDA | Xen | Xoken | XYZ Enterprises | Your Team in India | Zab Technologies: Blockchain Development Company | Zeme Eco Fuels and Alloys Ltd | Zimrii | Zinc | Zineum | Ztex | ZVChain Technology")
    find = r.findall(text)
    found_comp = [word for word, word_count in Counter(find).most_common(1)]
    if found_comp:
        return found_comp[0]
    return prev
text = " This job listing was recently removed Unfortunately, this job listing is no longer available, but we have more roles open that might interest you. Search blockchain jobs Bakkt Bringing trust and utility to digital assets Customer Experience Product Manager Atlanta \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00b7 Other \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00b7 Full-Time Date posted: 23 Oct 2019 Bakkt is hiring a full-time Customer Experience Product Manager in Atlanta. Bakkt - Bringing trust and utility to digital assets. Apply now Bakkt website View more jobs at Bakkt non-tech product product manager How did you hear about this opportunity? Please let Bakkt know you found this position on Cryptocurrency Jobs as a way to support us so we can keep providing you with quality jobs. Apply now Follow @jobsincrypto Subscribe to email updates \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00a9 2020 Cryptocurrency Jobs"

tagger = StanfordNERTagger('C:/Users/Leon/BlockchainOpportunityAnalysis/stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz',
'C:/Users/Leon/BlockchainOpportunityAnalysis/stanford-ner-4.0.0/stanford-ner.jar',
encoding='utf-8')
print(nlp_body(text,tagger))