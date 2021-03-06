# BlockchainOpportunityAnalysis
Last edited: November 11 2020 by John-Paul Besong

As a service to the emergent Blockchain technology community, and in an effort to aid in the growth of that community, this project seeks to achieve the following:
* Provide an interactive visualization of the blockchain space for concretely summarizing skills, locations, verticals, salaries, opportunities and other related meta data.
* Present the interactive visualization publicly in a format that can be explored by technologists seeking to enter or expand their presence in the space.

# Named Entity Recognition

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Prerequisites
### Libraries
* GeoText
* nltk
* StanfordCoreNLP
* Numpy
* datefinder
* BeautifulSoup

### Programs

NLP.py - Currently runs on JSON file and outputs JSONs of predicted NER. Takes in three inputs to be run: path to JSON file, path to english.all.3class.distsim.crf.ser.gz which should be under classifiers in stanford-ner-4.0.0, and path to stanford-ner.jar which is under stanford-ner-4.0.0. Download files from stanford-ner-4.0.0 folder

notes:
            Date, Location and Salary Capabilities enhanced. Needs to be perfected through extrenuous testing and weeding out bad data. Location and Salary capabilities worked on in Location.py & Salary.py


NLP_acc.py - Takes in JSON with labeled data and Outputs JSON with predicted data. Also prints out accuracy of the NER on labeled data.
sample_jobs.py - Samples a specific number of jobs from available postings
Statistics.py - Stemming and Stop Words. Takes in a JSON file path and currently doesn't output anything


Location.py - Takes string locations as input from NLP.py and returns JSON object of formatted location. 
    City, State, Country format for each location. Abbreviations should be lengthened. 
    -
    notes:
    Can identify american cities but needs to work on identifying foreign cities and states
    New York City metro anomalie because not in city list
    
Salary.py - Takes string salary information from NLP.py and returns and cleaned up version if necessary to suit standard format
e.x $200k or $120K - $140K 

notes:
        Salaries still have some anomalies 
        Salary might come up as millions but this is a mistake by the crawler
        Need to work on identifying currency depending on location
        


#### Note for using NLP_acc.py

Currently the paths used in the programs are specific to my computer, I will change them to be an input during this sprint.

## Process

### Heuristics 

#### General

Looking for company names in titles usually came after 'at' in most posting. I also looked for common company endings such as LLC, Ltd etc.

Location was found through the geotext library in general.

For salary, it was usually preceded by compenseation, salary, estimate. 

For date, it was usually preceded by date posted if it was a date or included the word ago if it was in the form of x 'month/days' ago

#### Linkedin

Linkedin titles contained both company and location ususally from looking for 'hiring' and 'in'. 'hiring' was usually preceded by the company name and 'in' was usually followed by the location. 

#### Choosing company

In order to determine a company name from the body, the most common named was used do to the company name being used the most often.

### Accuracy

Accuracy was calculated through counting how many predicted subjects were the same as the labeled subjects. This was then divided by the total number of postings there were.
Current accuracy on a representative sample from 6/30/2020:
* Total location Accuracy: 0.8980477223427332
* Total company Accuracy: 0.9240780911062907
* Date Accuracy: 0.9869848156182213
* Salary Accuracy: 0.9501084598698482
* No Not Found, Date Accuracy: 0.9122807017543859
* No Not Found, Salary Accuracy: 0.7560975609756098

## Research

### Spacy

* Really fast at running
* Performance varies due to false positives or missing up
* Built to work with Python so easier to work with


### StanfordNLP

* Good accuracy at finding organizations and locations
* Somewhat slow 
* Works best with Java but Python port works well currently
* Requires NLTK to work 

## Misc

### Built With

* Python
