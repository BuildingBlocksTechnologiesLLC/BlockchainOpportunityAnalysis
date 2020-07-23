import re
from geotext import GeoText
import nltk
from nltk.corpus import stopwords
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import numpy as np
import os
import json 
import gzip
import re
import string
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
    print(loc.cities)
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



def remove_keywords(text):
    r = re.compile(r"(?i) ordered_list['|\-|.|,| ]| \.net['|\-|.|,| ]| 3gpp['|\-|.|,| ]| 4gpp['|\-|.|,| ]| acceptance test['|\-|.|,| ]| agile['|\-|.|,| ]| Blockchain['|\-|.|,| ]| blockchain['|\-|.|,| ]| blockchain interoperability['|\-|.|,| ]| interoperability['|\-|.|,| ]| interoperable['|\-|.|,| ]| full time['|\-|.|,| ]| fulltime['|\-|.|,| ]| full\-time['|\-|.|,| ]| ai['|\-|.|,| ]| algorithms['|\-|.|,| ]| algorithm['|\-|.|,| ]| alteryx['|\-|.|,| ]| amelia['|\-|.|,| ]| aml['|\-|.|,| ]| anti money laundering['|\-|.|,| ]| financial exchanges['|\-|.|,| ]| digital asset exchange['|\-|.|,| ]| analytical['|\-|.|,| ]| analytical and problem solving['|\-|.|,| ]| laravel['|\-|.|,| ]| analytical generics['|\-|.|,| ]| android['|\-|.|,| ]| angular['|\-|.|,| ]| angularjs['|\-|.|,| ]| ansible['|\-|.|,| ]| appliation architecture['|\-|.|,| ]| application apis['|\-|.|,| ]| application development['|\-|.|,| ]| artificial intelligence['|\-|.|,| ]| asset management['|\-|.|,| ]| asset tokenization['|\-|.|,| ]| aws['|\-|.|,| ]| azure['|\-|.|,| ]| babel['|\-|.|,| ]| back end['|\-|.|,| ]| backend['|\-|.|,| ]| banking['|\-|.|,| ]| digital banking['|\-|.|,| ]| beacon['|\-|.|,| ]| beacon chain['|\-|.|,| ]| big data['|\-|.|,| ]| bigdata['|\-|.|,| ]| bigchain db['|\-|.|,| ]| bitcoin['|\-|.|,| ]| stable coin['|\-|.|,| ]| stablecoin['|\-|.|,| ]| middleware['|\-|.|,| ]| non custodial['|\-|.|,| ]| custodial['|\-|.|,| ]| scarcity token['|\-|.|,| ]| loans['|\-|.|,| ]| bitcoin 2\.0['|\-|.|,| ]| blockchain agnostic['|\-|.|,| ]| blockchain architecture['|\-|.|,| ]| blockchain based['|\-|.|,| ]| blockchain developer['|\-|.|,| ]| product manager['|\-|.|,| ]| senior consultant['|\-|.|,| ]| platform developer['|\-|.|,| ]| blockchain platforms['|\-|.|,| ]| blockchain research['|\-|.|,| ]| blockchain services['|\-|.|,| ]| blockstack['|\-|.|,| ]| business development['|\-|.|,| ]| business intelligence['|\-|.|,| ]| loyalty programs['|\-|.|,| ]| hedge funds['|\-|.|,| ]| hedge fund['|\-|.|,| ]| edtech['|\-|.|,| ]| legal tech['|\-|.|,| ]| cannabis['|\-|.|,| ]| online auctions['|\-|.|,| ]| c['|\-|.|,| ]| c\+\+['|\-|.|,| ]| capital markets['|\-|.|,| ]| cellular network['|\-|.|,| ]| chaincode['|\-|.|,| ]| chef['|\-|.|,| ]| ci cd['|\-|.|,| ]| circuit design['|\-|.|,| ]| clarity['|\-|.|,| ]| clarity smart language['|\-|.|,| ]| cloud['|\-|.|,| ]| cloud computing['|\-|.|,| ]| cloud experience['|\-|.|,| ]| cloud services['|\-|.|,| ]| cognitive automation['|\-|.|,| ]| cognitive systems['|\-|.|,| ]| collaboration['|\-|.|,| ]| communication generics['|\-|.|,| ]| interoperability platform['|\-|.|,| ]| interoperable  blockchain['|\-|.|,| ]| staking['|\-|.|,| ]| consensus['|\-|.|,| ]| consensus algorithms['|\-|.|,| ]| containerization['|\-|.|,| ]| containers['|\-|.|,| ]| continuous deployment['|\-|.|,| ]| continuous integration['|\-|.|,| ]| corda['|\-|.|,| ]| cosmos['|\-|.|,| ]| cosmos sdk['|\-|.|,| ]| couchdb['|\-|.|,| ]| crawling['|\-|.|,| ]| cross chain['|\-|.|,| ]| cross\-chain['|\-|.|,| ]| credential information['|\-|.|,| ]| crypto enthusiast['|\-|.|,| ]| crypto wallet['|\-|.|,| ]| cryptoasset['|\-|.|,| ]| cryptoassets['|\-|.|,| ]| cryptocurrencies['|\-|.|,| ]| cryptocurrency['|\-|.|,| ]| cryptocurrency for payments['|\-|.|,| ]| cryptographic principles['|\-|.|,| ]| cryptographic protocols['|\-|.|,| ]| cryptography['|\-|.|,| ]| protocol developer['|\-|.|,| ]| mobile payments['|\-|.|,| ]| mobile apps['|\-|.|,| ]| predictive analytics['|\-|.|,| ]| crowdfunding['|\-|.|,| ]| parachain['|\-|.|,| ]| voting['|\-|.|,| ]| backbone['|\-|.|,| ]| embedded['|\-|.|,| ]| css['|\-|.|,| ]| cyber['|\-|.|,| ]| cyber security['|\-|.|,| ]| dao['|\-|.|,| ]| dapps['|\-|.|,| ]| data & analytics['|\-|.|,| ]| data aggragation['|\-|.|,| ]| data analytics['|\-|.|,| ]| data science['|\-|.|,| ]| data structures['|\-|.|,| ]| data warehousing['|\-|.|,| ]| dataiku['|\-|.|,| ]| datarobot['|\-|.|,| ]| debugging testing generics['|\-|.|,| ]| decentralized applications['|\-|.|,| ]| decentralised['|\-|.|,| ]| decentralised autonomous organisations['|\-|.|,| ]| decentralised finance['|\-|.|,| ]| decentralised systems['|\-|.|,| ]| decentralized['|\-|.|,| ]| decentralized autonomous organizations['|\-|.|,| ]| decentralized finance['|\-|.|,| ]| decentralized systems['|\-|.|,| ]| decntralized reputation systems['|\-|.|,| ]| defi['|\-|.|,| ]| deliver production['|\-|.|,| ]| design patterns['|\-|.|,| ]| developing and deploying['|\-|.|,| ]| devops['|\-|.|,| ]| digital asset['|\-|.|,| ]| digital asset platform['|\-|.|,| ]| digital assets['|\-|.|,| ]| digital transofrmation['|\-|.|,| ]| disruptive['|\-|.|,| ]| disruptive solutions['|\-|.|,| ]| disruptive technologies['|\-|.|,| ]| distributed application['|\-|.|,| ]| distributed applications['|\-|.|,| ]| distributed ledger['|\-|.|,| ]| ledger technology['|\-|.|,| ]| ledger technologies['|\-|.|,| ]| online games['|\-|.|,| ]| gaming['|\-|.|,| ]| gambling['|\-|.|,| ]| distributed systems['|\-|.|,| ]| django['|\-|.|,| ]| advertising['|\-|.|,| ]| dlt['|\-|.|,| ]| dlt service['|\-|.|,| ]| docker['|\-|.|,| ]| rancher['|\-|.|,| ]| drizzle['|\-|.|,| ]| e\-commerce['|\-|.|,| ]| e commerce['|\-|.|,| ]| marketplace['|\-|.|,| ]| ecma script['|\-|.|,| ]| ecmascript['|\-|.|,| ]| ecr['|\-|.|,| ]| elastic search['|\-|.|,| ]| elasticsearch['|\-|.|,| ]| electromagnetic['|\-|.|,| ]| emerging technologies['|\-|.|,| ]| encryption['|\-|.|,| ]| encryption signatures['|\-|.|,| ]| enterprise blockchain software['|\-|.|,| ]| enterprise software['|\-|.|,| ]| erlang['|\-|.|,| ]| eth['|\-|.|,| ]| eth 2\.0['|\-|.|,| ]| ethereum['|\-|.|,| ]| ethereum 2\.0['|\-|.|,| ]| ethereumjs['|\-|.|,| ]| ethers\.js['|\-|.|,| ]| etl['|\-|.|,| ]| ewasm['|\-|.|,| ]| fabric['|\-|.|,| ]| finance['|\-|.|,| ]| financial['|\-|.|,| ]| financial application['|\-|.|,| ]| financial services['|\-|.|,| ]| financial solutions['|\-|.|,| ]| financial technology['|\-|.|,| ]| fintech['|\-|.|,| ]| fpga['|\-|.|,| ]| fpga design['|\-|.|,| ]| frameworks['|\-|.|,| ]| fraud['|\-|.|,| ]| fraud detection['|\-|.|,| ]| front end['|\-|.|,| ]| frontend['|\-|.|,| ]| full stack['|\-|.|,| ]| fullstack['|\-|.|,| ]| functional test['|\-|.|,| ]| test automation['|\-|.|,| ]| functional program['|\-|.|,| ]| compliance['|\-|.|,| ]| strategic planning['|\-|.|,| ]| risk management['|\-|.|,| ]| information technology['|\-|.|,| ]| ganache['|\-|.|,| ]| genetic['|\-|.|,| ]| geth['|\-|.|,| ]| parity['|\-|.|,| ]| besu24['|\-|.|,| ]| multigeth['|\-|.|,| ]| multi\-chain['|\-|.|,| ]| multi chain['|\-|.|,| ]| para\-chain['|\-|.|,| ]| para chain['|\-|.|,| ]| middleware['|\-|.|,| ]| graph theory['|\-|.|,| ]| nethermind['|\-|.|,| ]| forensic['|\-|.|,| ]| git['|\-|.|,| ]| github['|\-|.|,| ]| golang['|\-|.|,| ]| gpus['|\-|.|,| ]| gradle['|\-|.|,| ]| graphql['|\-|.|,| ]| hadoop['|\-|.|,| ]| hardware developer['|\-|.|,| ]| hardware engineer['|\-|.|,| ]| hash functions['|\-|.|,| ]| haskell['|\-|.|,| ]| hbase['|\-|.|,| ]| healthcare['|\-|.|,| ]| health care['|\-|.|,| ]| health industry['|\-|.|,| ]| health organizations['|\-|.|,| ]| high performance computing['|\-|.|,| ]| html['|\-|.|,| ]| html5['|\-|.|,| ]| hyperledger['|\-|.|,| ]| exchanges['|\-|.|,| ]| ico['|\-|.|,| ]| identity management['|\-|.|,| ]| identity managment['|\-|.|,| ]| identity protocols['|\-|.|,| ]| information systems['|\-|.|,| ]| infura['|\-|.|,| ]| instanbul['|\-|.|,| ]| intellectual curiosity['|\-|.|,| ]| intellij['|\-|.|,| ]| internet of things['|\-|.|,| ]| investment funds['|\-|.|,| ]| iot['|\-|.|,| ]| ipfs['|\-|.|,| ]| j2ee['|\-|.|,| ]| java['|\-|.|,| ]| javascript['|\-|.|,| ]| jira['|\-|.|,| ]| jquery['|\-|.|,| ]| js frameworks['|\-|.|,| ]| jscript['|\-|.|,| ]| json['|\-|.|,| ]| json\-rpc['|\-|.|,| ]| kafka['|\-|.|,| ]| kanban['|\-|.|,| ]| kendo ui['|\-|.|,| ]| kmi['|\-|.|,| ]| kotlin['|\-|.|,| ]| automated testing['|\-|.|,| ]| quality engineer['|\-|.|,| ]| sofware engineer['|\-|.|,| ]| sofware developer['|\-|.|,| ]| kovan['|\-|.|,| ]| kubernetes['|\-|.|,| ]| kyc['|\-|.|,| ]| know your customer['|\-|.|,| ]| threat modeling['|\-|.|,| ]| layer 2['|\-|.|,| ]| layer\-2['|\-|.|,| ]| large scale deployment['|\-|.|,| ]| lending platforms['|\-|.|,| ]| libra network['|\-|.|,| ]| lightning network['|\-|.|,| ]| linux['|\-|.|,| ]| lisp['|\-|.|,| ]| litecoin['|\-|.|,| ]| logic circuit['|\-|.|,| ]| machine learning['|\-|.|,| ]| mainnet['|\-|.|,| ]| matlab['|\-|.|,| ]| maven['|\-|.|,| ]| merkle tree['|\-|.|,| ]| patricia tree['|\-|.|,| ]| metamask['|\-|.|,| ]| micro services['|\-|.|,| ]| microservices['|\-|.|,| ]| monero['|\-|.|,| ]| mongo['|\-|.|,| ]| mongo db['|\-|.|,| ]| mongodb['|\-|.|,| ]| mqtt['|\-|.|,| ]| multi currency['|\-|.|,| ]| multi currency wallet['|\-|.|,| ]| multithreading['|\-|.|,| ]| mysql['|\-|.|,| ]| natural language procesing['|\-|.|,| ]| network security['|\-|.|,| ]| nlg['|\-|.|,| ]| nlp['|\-|.|,| ]| nlu['|\-|.|,| ]| node js['|\-|.|,| ]| node\.js['|\-|.|,| ]| nodejs['|\-|.|,| ]| nodeops['|\-|.|,| ]| nosql['|\-|.|,| ]| npm['|\-|.|,| ]| numpy['|\-|.|,| ]| object model['|\-|.|,| ]| object oriented['|\-|.|,| ]| object oriented design['|\-|.|,| ]| object oriented programming['|\-|.|,| ]| off chain['|\-|.|,| ]| off\-chain['|\-|.|,| ]| open source technologies['|\-|.|,| ]| open source tools['|\-|.|,| ]| opencl['|\-|.|,| ]| opensource['|\-|.|,| ]| p2p['|\-|.|,| ]| parallel programming['|\-|.|,| ]| patrecia trees['|\-|.|,| ]| peer to peer['|\-|.|,| ]| peer\-to\-peer['|\-|.|,| ]| collectible asset['|\-|.|,| ]| digital collectible['|\-|.|,| ]| pgp['|\-|.|,| ]| pharma['|\-|.|,| ]| pharmaceutical['|\-|.|,| ]| civictech['|\-|.|,| ]| polygot['|\-|.|,| ]| pos['|\-|.|,| ]| postgres['|\-|.|,| ]| pow['|\-|.|,| ]| augmented reality['|\-|.|,| ]| virtual reality['|\-|.|,| ]| virtual reality['|\-|.|,| ]| smart blem solving generics['|\-|.|,| ]| proof of stake['|\-|.|,| ]| proof of work['|\-|.|,| ]| protocols['|\-|.|,| ]| public blockhain['|\-|.|,| ]| public key encryption['|\-|.|,| ]| public keys['|\-|.|,| ]| puppet['|\-|.|,| ]| python['|\-|.|,| ]| quantum computing['|\-|.|,| ]| quasar['|\-|.|,| ]| quorum['|\-|.|,| ]| r3 corda['|\-|.|,| ]| rabbit mq['|\-|.|,| ]| rdbms['|\-|.|,| ]| react['|\-|.|,| ]| react\.js['|\-|.|,| ]| prediction market['|\-|.|,| ]| prediction markets['|\-|.|,| ]| real estate['|\-|.|,| ]| realestate['|\-|.|,| ]| remix['|\-|.|,| ]| repuation systems['|\-|.|,| ]| restful apis['|\-|.|,| ]| ripple['|\-|.|,| ]| rootstock['|\-|.|,| ]| ropsten['|\-|.|,| ]| rpc['|\-|.|,| ]| rsk['|\-|.|,| ]| ruby['|\-|.|,| ]| rust['|\-|.|,| ]| sass['|\-|.|,| ]| scala['|\-|.|,| ]| scikit['|\-|.|,| ]| scripting['|\-|.|,| ]| scrum['|\-|.|,| ]| code review['|\-|.|,| ]| sdk['|\-|.|,| ]| sdlc['|\-|.|,| ]| security and  identity management['|\-|.|,| ]| security with identity management['|\-|.|,| ]| serenity['|\-|.|,| ]| server side language['|\-|.|,| ]| smart contract['|\-|.|,| ]| smart grids['|\-|.|,| ]| side\-chain['|\-|.|,| ]| side chain['|\-|.|,| ]| smt checker['|\-|.|,| ]| social good['|\-|.|,| ]| social impact['|\-|.|,| ]| social network['|\-|.|,| ]| solidity['|\-|.|,| ]| solr['|\-|.|,| ]| spark['|\-|.|,| ]| spring boot['|\-|.|,| ]| sql['|\-|.|,| ]| trading['|\-|.|,| ]| staker['|\-|.|,| ]| standards protocols['|\-|.|,| ]| startup['|\-|.|,| ]| stellar['|\-|.|,| ]| stellar core['|\-|.|,| ]| sto['|\-|.|,| ]| subscription based['|\-|.|,| ]| substrate['|\-|.|,| ]| supply chain['|\-|.|,| ]| supply chains['|\-|.|,| ]| swift['|\-|.|,| ]| systems implementation['|\-|.|,| ]| tableau['|\-|.|,| ]| tcl['|\-|.|,| ]| tdd['|\-|.|,| ]| tendermint['|\-|.|,| ]| teneo['|\-|.|,| ]| terraform['|\-|.|,| ]| test driven development['|\-|.|,| ]| testnet['|\-|.|,| ]| tokenization['|\-|.|,| ]| tokenomics['|\-|.|,| ]| trinity['|\-|.|,| ]| truffle['|\-|.|,| ]| typescript['|\-|.|,| ]| ui ux['|\-|.|,| ]| unit and functional test['|\-|.|,| ]| unit test['|\-|.|,| ]| user facing['|\-|.|,| ]| utility token['|\-|.|,| ]| validator['|\-|.|,| ]| vector analysis['|\-|.|,| ]| verilog['|\-|.|,| ]| vhdl['|\-|.|,| ]| viper['|\-|.|,| ]| visualization['|\-|.|,| ]| vyper['|\-|.|,| ]| waffle['|\-|.|,| ]| wallet['|\-|.|,| ]| wasm['|\-|.|,| ]| web applications['|\-|.|,| ]| web\-2['|\-|.|,| ]| web2['|\-|.|,| ]| web 2['|\-|.|,| ]| web\-3['|\-|.|,| ]| web3['|\-|.|,| ]| web 3['|\-|.|,| ]| web3\.py['|\-|.|,| ]| webassembly['|\-|.|,| ]| webpack['|\-|.|,| ]| websocket['|\-|.|,| ]| wireframes['|\-|.|,| ]| wireframs['|\-|.|,| ]| workfusion['|\-|.|,| ]| z\-cash['|\-|.|,| ]| zcash['|\-|.|,| ]| zero knowledge['|\-|.|,| ]| zero knowledge proof['|\-|.|,| ]| zkp['|\-|.|,| ]| zokrates['|\-|.|,| ]| zookeeper")
    return r.sub(' ',text)

def nlp_title(text):
    """
    Retrieve information from title line
    """
    loc = []
    name = []
    org_name = 'Not Found'
    location = 'Not Found'
    prev = ''


    find_at = re.compile(r' at ',re.IGNORECASE)
    punct = re.compile(r'\||\,|\-|\.|\/|\:|\;|\\|\–')
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
    if org_name == 'Not Found':      
        abbr_re = re.compile(r'(?i)[ |, |,]Inc|[ |, |,]LLC|[ |, |,]Co |[ |, |,]Ltd|\.com|\.org|\.net')
        abb = abbr_re.findall(text)
        abbrev = [m.start(0) for m in abbr_re.finditer(text)]
        if abbrev:
            if punct.findall(text[:abbrev[0]]):
                t = text[:abbrev[0]+len(abb[0])]
                s = [m.start(0) for m in punct.finditer(t)]
                org_name = t[s[0]+1:]

    r = re.compile('[A-Z][A-Z]')
    if r.findall(location):
        location = regex_location(location)
    if name and org_name == 'Not Found':
        org_name = name[-1]
    
    return location.strip(), org_name.strip()

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
    l = re_text[:(len(re_text)*8)//10].rfind(' ')
    re_text = re_text[:]
    tokenized_text = word_tokenize(re_text)
    classified_text = tagger.tag(tokenized_text)
    loc = []
    name = []
    loc_re =  re.compile('location[:| | :]',re.IGNORECASE)
    loc_ind = [m.start(0) for m in loc_re.finditer(re_text)]
    location = 'Not Found'
    date_remove = re.compile('date',re.IGNORECASE)
    city = False
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
            state_loc_2 = re_text[:state_loc_1].rfind(' ')
            state_loc = re_text[:state_loc_2].rfind(' ')
            location = regex_location(re.sub(date_remove, '', re_text[state_loc:s_ind[0]+4]))
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

    if location == 'Not Found':
        location = decide_loc(np.array(loc))
    

        

    return location
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
            l_t = text[i+4:].index(' ')
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
'''
text ="This job listing was recently removed Unfortunately, this job listing is no longer available, but we have more roles open that might interest you. Search blockchain jobs block.one Designs free market systems to secure life, liberty, and property Web Project Manager Hong Kong \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00b7 Marketing \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00b7 Full-Time Date posted: 6 Dec 2019 block.one is hiring a full-time Web Project Manager in Hong Kong. block.one - Designs free market systems to secure life, liberty, and property. Apply now block.one website View more jobs at block.one project management wordpress How did you hear about this opportunity? Please let block.one know you found this position on Cryptocurrency Jobs as a way to support us so we can keep providing you with quality jobs. Apply now Follow @jobsincrypto Subscribe to email updates \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00a9 2020 Cryptocurrency Jobs"
'''

text = " Posted: April 21, 2020 $52,680 to $108,287 Yearly Full-Time Interested in helping us change the world of finance and payments forever? The Stellar Development Foundation (SDF) is looking for a talented and experienced Business Development and Partnerships expert to join our team. In this role, you'll be engaging directly with the global network of Stellar users as a primary point of contact for the SDF. You'll be providing support to strategic ecosystem initiatives, vetting potential projects and businesses, and take a key role in helping define the SDF's strategy around interfacing with our large and growing ecosystem. Most importantly, you will be growing the world of blockchain and supporting the SDF mission of creating equitable access to the global financial system. You will: Serve as a primary point of contact for business inquiries exploring Stellar as a blockchain solution for their business or project Take the lead on strategic collaborations, serving as the liaison between partners and the SDF while providing project management and/or business development support as required Develop and maintain relationships with key contributors to the Stellar ecosystem by providing ongoing support and maintaining open and positively managed lines of communication Work with the grants, community and marketing teams to support the launch and execution of new programs and initiatives for engaging with our global partners Propose new ways in which the Foundation can provide systemic support and opportunities for the ecosystem of companies building on Stellar Represent\u00c3\u0082\u00c2\u00a0the Foundation at select conferences and events throughout the world Requirements: You have 3+ years of experience working in partnerships or customer success You have a deep understanding and experience in blockchain You have experience with payments or in the financial technology space You're willing to travel 25% of the time You have significant experience working with external stakeholders to execute projects and/or business negotiations You thrive in an environment where you're an active participant in cross-functional projects You're a natural at strategic and analytical thinking, and you know how to solve a host of problems on your feet You've managed many projects from start to finish, including setting the initial vision, driving execution, \u00c3\u0082\u00c2\u00a0and reporting on the ultimate outcomes You're an exceptional writer and have excellent verbal communication skills You have a high degree of technical aptitude and you have a passion for Stellar's technology You have a strong interest in cryptocurrency, blockchain, and financial inclusion You thrive in a collaborative team environment with multiple stakeholders while having a high degree of accountability and autonomy You're flexible and comfortable working in a fast paced and dynamic environment Bonus points if: You have additional experience in project management, business development, or entrepreneurship You've lived or worked abroad at some point in your career You can speak more than one language fluently You're curious and tenacious, with an infectiously positive attitude and an unwavering commitment to being successful About Stellar Stellar is a decentralized, fast, scalable, and uniquely sustainable network for financial products and services. It is both a cross-currency transaction system and a platform for digital asset issuance, designed to connect the world's financial infrastructure. Dozens of financial institutions worldwide issue assets and settle payments on the Stellar network, which has grown to over 4 million accounts.\u00c3\u0082\u00c2\u00a0\u00c3\u0082\u00c2\u00a0\u00c3\u0082\u00c2\u00a0 About the Stellar Development Foundation The Stellar Development Foundation (SDF) is a non-profit organization that supports the development and growth of Stellar, an open-source network that connects the world's financial infrastructure. Founded in 2014, the Foundation helps maintain Stellar's codebase, supports the technical and business communities building on the network, and serves as a voice to regulators and institutions. The Foundation seeks to create equitable access to the global financial system, using the Stellar network to unlock the world's economic potential through blockchain technology. We look forward to hearing from you! SDF is committed to diversity in its workforce and is proud to be an equal opportunity employer. SDF does not make hiring or employment decisions on the basis of race, color, religion, creed, gender, national origin, age, disability, veteran status, marital status, pregnancy, sex, gender expression or identity, sexual orientation, citizenship, or any other basis protected by applicable local, state or federal law. Stellar Development Foundation Address San Francisco, CA USA "
print(find_sal(text))

"""
tokenized_text = word_tokenize(text)
tagger = StanfordNERTagger('C:/Users/Leon/BlockchainOpportunityAnalysis/stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz',
'C:/Users/Leon/BlockchainOpportunityAnalysis/stanford-ner-4.0.0/stanford-ner.jar',
encoding='utf-8')
stop_words = set(stopwords.words('english'))   
filtered_sentence = [w for w in tokenized_text if not w in stop_words] 

classified_text = tagger.tag(filtered_sentence)

r = re.compile(r'\\u')
s_text = r.sub('',text)
text = (text.encode('ascii', 'ignore')).decode("utf-8")

regex = re.compile('[^a-zA-Z\-\|\,0-9\+]')
re_text = regex.sub(' ',text)

re_text = remove_keywords(re_text)
l = re_text[:(len(re_text)*8)//10].rfind(' ')
re_text = re_text[:]
tokenized_text = word_tokenize(re_text)
classified_text = tagger.tag(tokenized_text)
loc = []
name = []
loc_re =  re.compile('location[:| | :]',re.IGNORECASE)
loc_ind = [m.start(0) for m in loc_re.finditer(re_text)]
location = 'Not Found'
date_remove = re.compile(r'(?i) date | nice | manage ')
city = False
if loc_ind:
    location = regex_location(re.sub(date_remove, '', re_text[loc_ind[0]:loc_ind[0]+60]))

if location == 'Not Found':
    state_r = re.compile(' AL | AK | AZ | AR | CA | CO | CT | DC | DE | FL | GA | HI | ID | IL | IN | IA | KS |'+
' KY | LA | ME | MD | MA | MI | MN | MS | MO | MT | NE | NV | NH | NJ | NM | NY | NC | ND | OH | OK | OR |'+
' PA | RI | SC | SD | TN | TX | UT | VT | VA | WA | WV | WI | WY ')
    states = state_r.findall(re_text)
    s_ind = [m.start(0) for m in state_r.finditer(re_text)]
    print(states)
    print(re_text)
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
        print(cc)
        n = word_tokenize(' '.join(cc))

        if not GeoText(' '.join(cc)).cities :
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
"""
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



#print(remove_keywords(text))
'''
punct = re.compile(r'\,|\-|\.|\/|\:|\;|\\|\||\–')
abbr_re = re.compile(r'(?i)[ |, |,]Inc|[ |, |,]LLC|[ |, |,]Co|[ |, |,]Ltd|.com|.org|.net')
abb = abbr_re.findall(text)
abbrev = [m.start(0) for m in abbr_re.finditer(text)]
if abbrev:
    if punct.findall(text[:abbrev[0]]):
        t = text[:abbrev[0]+len(abb[0])]
        s = [m.start(0) for m in punct.finditer(t)]

        org_name = t[s[0]+1:]
'''
