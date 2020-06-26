import sys
import gzip
import json


def get_lang(text):

    return ''

if __name__ == '__main__':
    
    Json_path = sys.argv[1]
    with open(Json_path,"r") as json_file:
        job = json.load(json_file)
        text = job['Body']
        job['Language'] = get_lang(text) 

    json_str = json.dumps(job, indent = 4) + "\n"   

    with open(Json_path+'new_lang', 'w') as outfile:
        outfile.write(json_str)