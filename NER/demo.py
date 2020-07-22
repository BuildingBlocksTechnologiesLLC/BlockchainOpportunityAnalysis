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
'''
text ="This job listing was recently removed Unfortunately, this job listing is no longer available, but we have more roles open that might interest you. Search blockchain jobs block.one Designs free market systems to secure life, liberty, and property Web Project Manager Hong Kong \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00b7 Marketing \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00b7 Full-Time Date posted: 6 Dec 2019 block.one is hiring a full-time Web Project Manager in Hong Kong. block.one - Designs free market systems to secure life, liberty, and property. Apply now block.one website View more jobs at block.one project management wordpress How did you hear about this opportunity? Please let block.one know you found this position on Cryptocurrency Jobs as a way to support us so we can keep providing you with quality jobs. Apply now Follow @jobsincrypto Subscribe to email updates \u00c3\u0083\u0082\u00c3\u0082\u00c2\u00a9 2020 Cryptocurrency Jobs"
'''

text = "Full Stack Engineer New York, NY / Engineering / Full-Time Apply for this job Blockstack is a decentralized computing platform. It\u2019s the easiest way to build decentralized apps that can scale. More info here. Blockstack PBC, a public benefit corp, has a mission to enable an open, decentralized internet which will benefit all internet users by giving them more control over information and computation. Blockstack PBC has raised $75M in capital to develop core protocols and developer tools for the ecosystem. Being a Public Benefit Corp also means we have goals beyond profit, and that allows us to focus on universal human rights and sharing the value created in our ecosystem. Blockstack PBC is headquartered in New York City, with a globally distributed team located across the United States, Canada, and Europe. Blockstack is looking for experienced full-stack engineers to help build our browser and developer tools for decentralized apps. This is a role for engineers who can collaborate with a team and work independently to architect and deliver feature upgrades and improvements on the platform. In this role you will build features such as multiplayer storage and other critical features for our developer community. This person must be comfortable working in diverse development ecosystems and a have worked independently in a rapidly scaling startup.\u00c3\u0083\u0082\u00c3\u0082\u00c2\u00a0OSS experience is preferred as we are an open source project. The position will be based in our NYC office. What you'll do: \u2022 Implement Blockstack feature upgrades, improvements, and architectural builds\u00c3\u0083\u0082\u00c3\u0082\u00c2\u00a0 \u2022 Collaborate with a team to ship major product builds\u00c3\u0083\u0082\u00c3\u0082\u00c2\u00a0 \u2022 Deliver on rapid implementation schedules to build web functionality that is fast, scalable, and upholds smart development goals and principles What we're looking for: \u2022 Demonstrable full stack experience (3+ years of professional experience) \u2022 Proficient in at least one frontend framework like React, Angular, Vue etc \u2022 Proficient in at least one backend environment like NodeJS or frameworks like Express or Ruby on Rails \u2022 Good understanding and comfort with SQL(MySQL, Postgres etc) and No-SQL storage(Mongo, Redis etc) system \u2022 Opinionated stance on an entire full-stack using on which you can build with confidence, high-quality and high-velocity \u2022 Experience with building tests (unit, integration, end-to-end), Open source experience, cloud platforms like GCP, AWS etc. \u2022 Experience with blockchains and dapp platforms \u2022 Experience on remote teams \u2022 Experience building 2+ web apps from scratch (and launching) \u2022 Experience \u201cleading the charge\u201d on starting a new project and building it out SPAs. \u2022 Excellent communication and collaboration skills Benefits & Perks: \u2022 Equity and Stacks tokens (STX - are the native token of the Blockstack computing network) \u2022 Remote workers can expense co-working spaces \u2022 An annual $1,200 budget for learning and development stipend \u2022 Daily lunch (even if you\u2019re remote!) \u2022 Flexible vacation policy \u2022 Family-Friendly health benefits \u2022 Free life and disability insurance \u2022 Health and dependent care (FSA) \u2022 Up to 16 weeks of paid parental leave \u2022 Pre-tax commuter benefits \u2022 401k with 3% match \u2022 Your choice of technical setup and equipment Company Highlights: \u2022 Public Benefit Corporation on a mission to enable an secure and private decentralized internet which will benefit all internet users: Blockstack Source Code \u2022 Remote first team with HQ in New York City \u2022 $75M total raised. $23M from first ever SEC qualified token offering in the U.S. \u2022 8,000 + active developers and enthusiasts in the community \u2022 400+ apps launched on Blockstack \u2022 Work alongside leading PHD experts in computing Blockstack PBC is proud to be an equal opportunity employer and deeply cares about building a diverse team. Blockstack PBC is committed to building an inclusive environment for people of all backgrounds. We do not discriminate on the basis of race, color, gender, sexual orientation, gender identity or expression, religion, disability, national origin, protected veteran status, age, or any other status protected by law. Please note that benefits vary by country, the ones shown above are for our full time U.S. based employees. Benefit information for non-US based positions will be provided to individuals who interview for those roles. Apply for this job Blockstack Home PageJobs powered by"
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
print(confirm_remote(text))

print(location)


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
