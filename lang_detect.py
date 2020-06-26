import sys
import gzip
import json
import langid

def get_lang(text):

    return ''

if __name__ == '__main__':
    
    Json_path = sys.argv[1]

    with gzip.GzipFile(Json_path,"r") as json_file:
        job = json.loads(json_file.read().decode('utf-8'))
        text = job['Body']
        language = get_lang(text)
        job['Language'] = language 

    json_str = json.dumps(job, indent = 4) + "\n"               
    json_bytes = json_str.encode('utf-8')         

    with gzip.GzipFile(Json_path[:-3]+'new_lang_.gz', 'w') as fout:   
        fout.write(json_bytes)      
