import sys
import gzip
import json

## FastText
#!pip install fasttext
import fasttext
# download this pretrained model
model = fasttext.load_model('fast_text_model/lid.176.ftz')

#!pip install pycountry
from pycountry import languages

def get_lang(text):
    '''
    This function uses the pretrained model from FastText
    to detect the language of a document.
    It returns a tuple in the form of (('__label__en',), array([0.26207453]))
    '''
    predicted_lang = model.predict(text)
    # only keep the language code such as 'en' from the output of the prediction
    ft_predict = predicted_lang[0][0][9:]

    # We need to convert the ISO 639 codes to find full name of the language for each symbol.
    # From the 46 common languages we aimed to detect, they all have two letter codes.
    if len(ft_predict) != 2:
        ft_names = 'nan'

    else:
        # Convert to full name in English
        lang_name = languages.get(alpha_2=ft_predict).name
        # We only keep the full name of the language
        if '(' in lang_name:
            ft_names= re.sub("[(\[].*?[\)]", "", lang_name)[:-1]
        else:
            ft_names = lang_name
    return ft_names

if __name__ == '__main__':

    Json_path = sys.argv[1]
    #  with gzip.GzipFile(Json_path,"r") as json_file:
    with open(Json_path,"r") as json_file:
        job = json.load(json_file)
        text = job['Body']
        job['Language'] = get_lang(text)

    json_str = json.dumps(job, indent = 4) + "\n"

    with open(Json_path+'new_lang', 'w') as outfile:
        outfile.write(json_str)
