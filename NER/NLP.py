"""
Created on Wed Jun 17 2020
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
                s = [m.start(0) for m in punct.finditer(t)]
                org_name = t[s[0]+1:]

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
        sal_range_re = re.compile('\-|\–| to ')
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
    r = re.compile(r"(?i) ordered_list['|\-|.|,| ]| \.net['|\-|.|,| ]| crypto['|\-|.|,| ]| 3gpp['|\-|.|,| ]| 4gpp['|\-|.|,| ]| acceptance test['|\-|.|,| ]| agile['|\-|.|,| ]| Blockchain['|\-|.|,| ]| blockchain['|\-|.|,| ]| blockchain interoperability['|\-|.|,| ]| interoperability['|\-|.|,| ]| interoperable['|\-|.|,| ]| full time['|\-|.|,| ]| fulltime['|\-|.|,| ]| full\-time['|\-|.|,| ]| ai['|\-|.|,| ]| algorithms['|\-|.|,| ]| algorithm['|\-|.|,| ]| alteryx['|\-|.|,| ]| amelia['|\-|.|,| ]| aml['|\-|.|,| ]| anti money laundering['|\-|.|,| ]| financial exchanges['|\-|.|,| ]| digital asset exchange['|\-|.|,| ]| analytical['|\-|.|,| ]| analytical and problem solving['|\-|.|,| ]| laravel['|\-|.|,| ]| analytical generics['|\-|.|,| ]| android['|\-|.|,| ]| angular['|\-|.|,| ]| angularjs['|\-|.|,| ]| ansible['|\-|.|,| ]| appliation architecture['|\-|.|,| ]| application apis['|\-|.|,| ]| application development['|\-|.|,| ]| artificial intelligence['|\-|.|,| ]| asset management['|\-|.|,| ]| asset tokenization['|\-|.|,| ]| aws['|\-|.|,| ]| azure['|\-|.|,| ]| babel['|\-|.|,| ]| back end['|\-|.|,| ]| backend['|\-|.|,| ]| banking['|\-|.|,| ]| digital banking['|\-|.|,| ]| beacon['|\-|.|,| ]| beacon chain['|\-|.|,| ]| big data['|\-|.|,| ]| bigdata['|\-|.|,| ]| bigchain db['|\-|.|,| ]| bitcoin['|\-|.|,| ]| stable coin['|\-|.|,| ]| stablecoin['|\-|.|,| ]| middleware['|\-|.|,| ]| non custodial['|\-|.|,| ]| custodial['|\-|.|,| ]| scarcity token['|\-|.|,| ]| loans['|\-|.|,| ]| bitcoin 2\.0['|\-|.|,| ]| blockchain agnostic['|\-|.|,| ]| blockchain architecture['|\-|.|,| ]| blockchain based['|\-|.|,| ]| blockchain developer['|\-|.|,| ]| product manager['|\-|.|,| ]| senior consultant['|\-|.|,| ]| platform developer['|\-|.|,| ]| blockchain platforms['|\-|.|,| ]| blockchain research['|\-|.|,| ]| blockchain services['|\-|.|,| ]| blockstack['|\-|.|,| ]| business development['|\-|.|,| ]| business intelligence['|\-|.|,| ]| loyalty programs['|\-|.|,| ]| hedge funds['|\-|.|,| ]| hedge fund['|\-|.|,| ]| edtech['|\-|.|,| ]| legal tech['|\-|.|,| ]| cannabis['|\-|.|,| ]| online auctions['|\-|.|,| ]| c['|\-|.|,| ]| c\+\+['|\-|.|,| ]| capital markets['|\-|.|,| ]| cellular network['|\-|.|,| ]| chaincode['|\-|.|,| ]| chef['|\-|.|,| ]| ci cd['|\-|.|,| ]| circuit design['|\-|.|,| ]| clarity['|\-|.|,| ]| clarity smart language['|\-|.|,| ]| cloud['|\-|.|,| ]| cloud computing['|\-|.|,| ]| cloud experience['|\-|.|,| ]| cloud services['|\-|.|,| ]| cognitive automation['|\-|.|,| ]| cognitive systems['|\-|.|,| ]| collaboration['|\-|.|,| ]| communication generics['|\-|.|,| ]| interoperability platform['|\-|.|,| ]| interoperable  blockchain['|\-|.|,| ]| staking['|\-|.|,| ]| consensus['|\-|.|,| ]| consensus algorithms['|\-|.|,| ]| containerization['|\-|.|,| ]| containers['|\-|.|,| ]| continuous deployment['|\-|.|,| ]| continuous integration['|\-|.|,| ]| corda['|\-|.|,| ]| cosmos['|\-|.|,| ]| cosmos sdk['|\-|.|,| ]| couchdb['|\-|.|,| ]| crawling['|\-|.|,| ]| cross chain['|\-|.|,| ]| cross\-chain['|\-|.|,| ]| credential information['|\-|.|,| ]| crypto enthusiast['|\-|.|,| ]| crypto wallet['|\-|.|,| ]| cryptoasset['|\-|.|,| ]| cryptoassets['|\-|.|,| ]| cryptocurrencies['|\-|.|,| ]| cryptocurrency['|\-|.|,| ]| cryptocurrency for payments['|\-|.|,| ]| cryptographic principles['|\-|.|,| ]| cryptographic protocols['|\-|.|,| ]| cryptography['|\-|.|,| ]| protocol developer['|\-|.|,| ]| mobile payments['|\-|.|,| ]| mobile apps['|\-|.|,| ]| predictive analytics['|\-|.|,| ]| crowdfunding['|\-|.|,| ]| parachain['|\-|.|,| ]| voting['|\-|.|,| ]| backbone['|\-|.|,| ]| embedded['|\-|.|,| ]| css['|\-|.|,| ]| cyber['|\-|.|,| ]| cyber security['|\-|.|,| ]| dao['|\-|.|,| ]| dapps['|\-|.|,| ]| data & analytics['|\-|.|,| ]| data aggragation['|\-|.|,| ]| data analytics['|\-|.|,| ]| data science['|\-|.|,| ]| data structures['|\-|.|,| ]| data warehousing['|\-|.|,| ]| dataiku['|\-|.|,| ]| datarobot['|\-|.|,| ]| debugging testing generics['|\-|.|,| ]| decentralized applications['|\-|.|,| ]| decentralised['|\-|.|,| ]| decentralised autonomous organisations['|\-|.|,| ]| decentralised finance['|\-|.|,| ]| decentralised systems['|\-|.|,| ]| decentralized['|\-|.|,| ]| decentralized autonomous organizations['|\-|.|,| ]| decentralized finance['|\-|.|,| ]| decentralized systems['|\-|.|,| ]| decntralized reputation systems['|\-|.|,| ]| defi['|\-|.|,| ]| deliver production['|\-|.|,| ]| design patterns['|\-|.|,| ]| developing and deploying['|\-|.|,| ]| devops['|\-|.|,| ]| digital asset['|\-|.|,| ]| digital asset platform['|\-|.|,| ]| digital assets['|\-|.|,| ]| digital transofrmation['|\-|.|,| ]| disruptive['|\-|.|,| ]| disruptive solutions['|\-|.|,| ]| disruptive technologies['|\-|.|,| ]| distributed application['|\-|.|,| ]| distributed applications['|\-|.|,| ]| distributed ledger['|\-|.|,| ]| ledger technology['|\-|.|,| ]| ledger technologies['|\-|.|,| ]| online games['|\-|.|,| ]| gaming['|\-|.|,| ]| gambling['|\-|.|,| ]| distributed systems['|\-|.|,| ]| django['|\-|.|,| ]| advertising['|\-|.|,| ]| dlt['|\-|.|,| ]| dlt service['|\-|.|,| ]| docker['|\-|.|,| ]| rancher['|\-|.|,| ]| drizzle['|\-|.|,| ]| e\-commerce['|\-|.|,| ]| e commerce['|\-|.|,| ]| marketplace['|\-|.|,| ]| ecma script['|\-|.|,| ]| ecmascript['|\-|.|,| ]| ecr['|\-|.|,| ]| elastic search['|\-|.|,| ]| elasticsearch['|\-|.|,| ]| electromagnetic['|\-|.|,| ]| emerging technologies['|\-|.|,| ]| encryption['|\-|.|,| ]| encryption signatures['|\-|.|,| ]| enterprise blockchain software['|\-|.|,| ]| enterprise software['|\-|.|,| ]| erlang['|\-|.|,| ]| eth['|\-|.|,| ]| eth 2\.0['|\-|.|,| ]| ethereum['|\-|.|,| ]| ethereum 2\.0['|\-|.|,| ]| ethereumjs['|\-|.|,| ]| ethers\.js['|\-|.|,| ]| etl['|\-|.|,| ]| ewasm['|\-|.|,| ]| fabric['|\-|.|,| ]| finance['|\-|.|,| ]| financial['|\-|.|,| ]| financial application['|\-|.|,| ]| financial services['|\-|.|,| ]| financial solutions['|\-|.|,| ]| financial technology['|\-|.|,| ]| fintech['|\-|.|,| ]| fpga['|\-|.|,| ]| fpga design['|\-|.|,| ]| frameworks['|\-|.|,| ]| fraud['|\-|.|,| ]| fraud detection['|\-|.|,| ]| front end['|\-|.|,| ]| frontend['|\-|.|,| ]| full stack['|\-|.|,| ]| fullstack['|\-|.|,| ]| functional test['|\-|.|,| ]| test automation['|\-|.|,| ]| functional program['|\-|.|,| ]| compliance['|\-|.|,| ]| strategic planning['|\-|.|,| ]| risk management['|\-|.|,| ]| information technology['|\-|.|,| ]| ganache['|\-|.|,| ]| genetic['|\-|.|,| ]| geth['|\-|.|,| ]| parity['|\-|.|,| ]| besu24['|\-|.|,| ]| multigeth['|\-|.|,| ]| multi\-chain['|\-|.|,| ]| multi chain['|\-|.|,| ]| para\-chain['|\-|.|,| ]| para chain['|\-|.|,| ]| middleware['|\-|.|,| ]| graph theory['|\-|.|,| ]| nethermind['|\-|.|,| ]| forensic['|\-|.|,| ]| git['|\-|.|,| ]| github['|\-|.|,| ]| golang['|\-|.|,| ]| gpus['|\-|.|,| ]| gradle['|\-|.|,| ]| graphql['|\-|.|,| ]| hadoop['|\-|.|,| ]| hardware developer['|\-|.|,| ]| hardware engineer['|\-|.|,| ]| hash functions['|\-|.|,| ]| haskell['|\-|.|,| ]| hbase['|\-|.|,| ]| healthcare['|\-|.|,| ]| health care['|\-|.|,| ]| health industry['|\-|.|,| ]| health organizations['|\-|.|,| ]| high performance computing['|\-|.|,| ]| html['|\-|.|,| ]| html5['|\-|.|,| ]| hyperledger['|\-|.|,| ]| exchanges['|\-|.|,| ]| ico['|\-|.|,| ]| identity management['|\-|.|,| ]| identity managment['|\-|.|,| ]| identity protocols['|\-|.|,| ]| information systems['|\-|.|,| ]| infura['|\-|.|,| ]| instanbul['|\-|.|,| ]| intellectual curiosity['|\-|.|,| ]| intellij['|\-|.|,| ]| internet of things['|\-|.|,| ]| investment funds['|\-|.|,| ]| iot['|\-|.|,| ]| ipfs['|\-|.|,| ]| j2ee['|\-|.|,| ]| java['|\-|.|,| ]| javascript['|\-|.|,| ]| jira['|\-|.|,| ]| jquery['|\-|.|,| ]| js frameworks['|\-|.|,| ]| jscript['|\-|.|,| ]| json['|\-|.|,| ]| json\-rpc['|\-|.|,| ]| kafka['|\-|.|,| ]| kanban['|\-|.|,| ]| kendo ui['|\-|.|,| ]| kmi['|\-|.|,| ]| kotlin['|\-|.|,| ]| automated testing['|\-|.|,| ]| quality engineer['|\-|.|,| ]| sofware engineer['|\-|.|,| ]| sofware developer['|\-|.|,| ]| kovan['|\-|.|,| ]| kubernetes['|\-|.|,| ]| kyc['|\-|.|,| ]| know your customer['|\-|.|,| ]| threat modeling['|\-|.|,| ]| layer 2['|\-|.|,| ]| layer\-2['|\-|.|,| ]| large scale deployment['|\-|.|,| ]| lending platforms['|\-|.|,| ]| libra network['|\-|.|,| ]| lightning network['|\-|.|,| ]| linux['|\-|.|,| ]| lisp['|\-|.|,| ]| litecoin['|\-|.|,| ]| logic circuit['|\-|.|,| ]| machine learning['|\-|.|,| ]| mainnet['|\-|.|,| ]| matlab['|\-|.|,| ]| maven['|\-|.|,| ]| merkle tree['|\-|.|,| ]| patricia tree['|\-|.|,| ]| metamask['|\-|.|,| ]| micro services['|\-|.|,| ]| microservices['|\-|.|,| ]| monero['|\-|.|,| ]| mongo['|\-|.|,| ]| mongo db['|\-|.|,| ]| mongodb['|\-|.|,| ]| mqtt['|\-|.|,| ]| multi currency['|\-|.|,| ]| multi currency wallet['|\-|.|,| ]| multithreading['|\-|.|,| ]| mysql['|\-|.|,| ]| natural language procesing['|\-|.|,| ]| network security['|\-|.|,| ]| nlg['|\-|.|,| ]| nlp['|\-|.|,| ]| nlu['|\-|.|,| ]| node js['|\-|.|,| ]| node\.js['|\-|.|,| ]| nodejs['|\-|.|,| ]| nodeops['|\-|.|,| ]| nosql['|\-|.|,| ]| npm['|\-|.|,| ]| numpy['|\-|.|,| ]| object model['|\-|.|,| ]| object oriented['|\-|.|,| ]| object oriented design['|\-|.|,| ]| object oriented programming['|\-|.|,| ]| off chain['|\-|.|,| ]| off\-chain['|\-|.|,| ]| open source technologies['|\-|.|,| ]| open source tools['|\-|.|,| ]| opencl['|\-|.|,| ]| opensource['|\-|.|,| ]| p2p['|\-|.|,| ]| parallel programming['|\-|.|,| ]| patrecia trees['|\-|.|,| ]| peer to peer['|\-|.|,| ]| peer\-to\-peer['|\-|.|,| ]| collectible asset['|\-|.|,| ]| digital collectible['|\-|.|,| ]| pgp['|\-|.|,| ]| pharma['|\-|.|,| ]| pharmaceutical['|\-|.|,| ]| civictech['|\-|.|,| ]| polygot['|\-|.|,| ]| pos['|\-|.|,| ]| postgres['|\-|.|,| ]| pow['|\-|.|,| ]| augmented reality['|\-|.|,| ]| virtual reality['|\-|.|,| ]| virtual reality['|\-|.|,| ]| smart blem solving generics['|\-|.|,| ]| proof of stake['|\-|.|,| ]| proof of work['|\-|.|,| ]| protocols['|\-|.|,| ]| public blockhain['|\-|.|,| ]| public key encryption['|\-|.|,| ]| public keys['|\-|.|,| ]| puppet['|\-|.|,| ]| python['|\-|.|,| ]| quantum computing['|\-|.|,| ]| quasar['|\-|.|,| ]| quorum['|\-|.|,| ]| r3 corda['|\-|.|,| ]| rabbit mq['|\-|.|,| ]| rdbms['|\-|.|,| ]| react['|\-|.|,| ]| react\.js['|\-|.|,| ]| prediction market['|\-|.|,| ]| prediction markets['|\-|.|,| ]| real estate['|\-|.|,| ]| realestate['|\-|.|,| ]| remix['|\-|.|,| ]| repuation systems['|\-|.|,| ]| restful apis['|\-|.|,| ]| ripple['|\-|.|,| ]| rootstock['|\-|.|,| ]| ropsten['|\-|.|,| ]| rpc['|\-|.|,| ]| rsk['|\-|.|,| ]| ruby['|\-|.|,| ]| rust['|\-|.|,| ]| sass['|\-|.|,| ]| scala['|\-|.|,| ]| scikit['|\-|.|,| ]| scripting['|\-|.|,| ]| scrum['|\-|.|,| ]| code review['|\-|.|,| ]| sdk['|\-|.|,| ]| sdlc['|\-|.|,| ]| security and  identity management['|\-|.|,| ]| security with identity management['|\-|.|,| ]| serenity['|\-|.|,| ]| server side language['|\-|.|,| ]| smart contract['|\-|.|,| ]| smart grids['|\-|.|,| ]| side\-chain['|\-|.|,| ]| side chain['|\-|.|,| ]| smt checker['|\-|.|,| ]| social good['|\-|.|,| ]| social impact['|\-|.|,| ]| social network['|\-|.|,| ]| solidity['|\-|.|,| ]| solr['|\-|.|,| ]| spark['|\-|.|,| ]| spring boot['|\-|.|,| ]| sql['|\-|.|,| ]| trading['|\-|.|,| ]| staker['|\-|.|,| ]| standards protocols['|\-|.|,| ]| startup['|\-|.|,| ]| stellar['|\-|.|,| ]| stellar core['|\-|.|,| ]| sto['|\-|.|,| ]| subscription based['|\-|.|,| ]| substrate['|\-|.|,| ]| supply chain['|\-|.|,| ]| supply chains['|\-|.|,| ]| swift['|\-|.|,| ]| systems implementation['|\-|.|,| ]| tableau['|\-|.|,| ]| tcl['|\-|.|,| ]| tdd['|\-|.|,| ]| tendermint['|\-|.|,| ]| teneo['|\-|.|,| ]| terraform['|\-|.|,| ]| test driven development['|\-|.|,| ]| testnet['|\-|.|,| ]| tokenization['|\-|.|,| ]| tokenomics['|\-|.|,| ]| trinity['|\-|.|,| ]| truffle['|\-|.|,| ]| typescript['|\-|.|,| ]| ui ux['|\-|.|,| ]| unit and functional test['|\-|.|,| ]| unit test['|\-|.|,| ]| user facing['|\-|.|,| ]| utility token['|\-|.|,| ]| validator['|\-|.|,| ]| vector analysis['|\-|.|,| ]| verilog['|\-|.|,| ]| vhdl['|\-|.|,| ]| viper['|\-|.|,| ]| visualization['|\-|.|,| ]| vyper['|\-|.|,| ]| waffle['|\-|.|,| ]| wallet['|\-|.|,| ]| wasm['|\-|.|,| ]| web applications['|\-|.|,| ]| web\-2['|\-|.|,| ]| web2['|\-|.|,| ]| web 2['|\-|.|,| ]| web\-3['|\-|.|,| ]| web3['|\-|.|,| ]| web 3['|\-|.|,| ]| web3\.py['|\-|.|,| ]| webassembly['|\-|.|,| ]| webpack['|\-|.|,| ]| websocket['|\-|.|,| ]| wireframes['|\-|.|,| ]| wireframs['|\-|.|,| ]| workfusion['|\-|.|,| ]| z\-cash['|\-|.|,| ]| zcash['|\-|.|,| ]| zero knowledge['|\-|.|,| ]| zero knowledge proof['|\-|.|,| ]| zkp['|\-|.|,| ]| zokrates['|\-|.|,| ]| zookeeper")    
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
    tokenized_text = word_tokenize(re_text)
    classified_text = tagger.tag(tokenized_text)
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
        if extract_dates(find_date):
            date_time = extract_dates(find_date)[0]
            date = date_time.strftime("%e %b %Y")

    re_date = re.compile(r'20[0-9][0-9]') 
    find_date = re_date.findall(re_text[:40])
    indices = [m.start(0) for m in re_date.finditer(re_text)]
    if find_date:
        fd = re_text[:indices[0]+4]
        date_loc_1 = fd[:indices[0]-1].rfind(' ')
        date_loc = fd[:date_loc_1].rfind(' ')
        find_date = re_text[date_loc:indices[0]+4]

        if extract_dates(find_date):
            date_time = extract_dates(find_date)[0]
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

def index_json(file_path,stanfordnlp,ner):
    """Get retrive data from json files"""
    tagger = StanfordNERTagger(stanfordnlp,ner,encoding='utf-8')

    with open(file_path,"r") as json_file:
        job = json.loads(json_file.read())

        if job['Language'] == 'English':
            pred = job
            
                        if 'LinkedIn' in job['Title']:
                title_loc, title_org = linkedin_title(job['Title'],tagger)
                title_city = True
                t_org = True
            else:
                title_loc, title_org,title_city,t_org = nlp_title(job['Title'],tagger)

            text_loc, text_org,text_sal, text_date, b_city,remote = nlp_body(job['Body'],tagger)

            com = re.compile(',')
            if (text_loc == 'Remote' and remote) or title_loc == 'Remote':
                location = 'Remote'
            elif title_city:
                location = title_loc
            else:
                location = text_loc
            text_l = text_loc.split(',')
            bod_l = title_loc.split(',')
            if text_l[0] == bod_l[0]:
                if len(text_loc) > len(title_loc):
                    location = text_loc
                else:
                    location = title_loc
            
            if 'US' in location:
                location = location.replace('US','United States') 
                state_r = re.compile('AL|AK|AZ|AR|CA|CO|CT|DC|DE|FL|GA|HI|ID|IL|IN|IA|KS|'+
' KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|'+
' PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY')
                if state_r.findall(location):
                    s = ' '+state_r.findall(location)[0]
                    s = s+ ' '
                    location = location.replace(state_r.findall(location)[0],check_state_body(s)) 
            
            if title_org != 'Not Found':
                org = title_org
            else:
                org = text_org

            pred['Location'] = location
            pred['Company Name'] = org
            pred['Salary'] = text_sal
            pred['PostedDate'] = text_date
            json_str = json.dumps(pred, indent = 4) + "\n" 

            with open(file_path+'nlp', "w") as w:
                w.write(json_str)
            
if __name__ == "__main__":
    file_path =  sys.argv[1]
    stanfordnlp = sys.argv[2]
    ner = sys.argv[3]
    index_json(file_path,stanfordnlp,ner)
