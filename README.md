# BlockchainOpportunityAnalysis

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

### Programs

NLP.py - Currently runs on all of the gzipped data and outputs JSONs of predicted NER
NLP_acc.py - Takes in JSON with labeled data and Outputs JSON with predicted data. Also prints out accuracy of the NER
sample_jobs.py - Samples a specific number of jobs from available postings

#### Note for using NLP.py and NLP_acc.py

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

### Accuracy

Accuracy was calculated through counting how many predicted subjects were the same as the labeled subjects. This was then divided by the total number of postings there were.
Current accuracy on a representative sample from 6/30/2020:
* Total location Accuracy: 0.7223427331887202
* Total company Accuracy: 0.8394793926247288
* Date Accuracy: 0.9891540130151844
* Salary Accuracy: 0.9718004338394793
* No Not Found, Date Accuracy: 0.9122807017543859
* No Not Found, Salary Accuracy: 0.7560975609756098

## Research

### Spacy

### StanfordNLP

## Misc

### Built With

* Python
