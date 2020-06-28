"""
Created on Wed Jun 24 2020
"""
import numpy as np
import os
import json 
import gzip
import re
import string
import datetime

def get_listings(entry):
    """Get file names that are jobs listings"""
    sub_entries = os.listdir('C:/Users/Leon/Data/Jobs/'+entry)
    entries = []
    for i in sub_entries:
        if i[-4:] == '_.gz':
            entries.append(i)
    return entries

def index_json(filenames,site,count):
    """Get retrive data from json files"""
    for f in filenames[:count]:
        with gzip.GzipFile('C:/Users/Leon/Data/Jobs/'+site+'/'+f,"r") as json_file:
            job = json.loads(json_file.read().decode('utf-8'))
            data = {}
            data['Salary'] = ''
            data['Location'] = ''
            data['Date Posted'] = ''
            data['Company name'] = ''
            data['Body'] = job['Body']
            data['Url'] = job['Url']
            data['Title'] = job['Title']
            data['Site'] = site
            json_str = json.dumps(data, indent = 4) + "\n"   
            with open(f[:-3]+'train', "w") as w:
                w.write(json_str)
            

def get_jobs(site_dict,count):
    """Retrive entities for each job posting if it is available"""
    keys = site_dict.keys()
    for k in keys:
        index_json(site_dict[k],k,count[k])

if __name__ == "__main__":

    entries = os.listdir('C:/Users/Leon/Data/Jobs')
    site_dict = {}
    jobs = 0
    for e in entries:
        site_dict[e] = get_listings(e)
        print(e,len(site_dict[e]))
        jobs += len(site_dict[e])


    count = {}
    for e in entries:
        count[e] = int(500*len(site_dict[e])/jobs)
    get_jobs(site_dict,count)
    print(count)

