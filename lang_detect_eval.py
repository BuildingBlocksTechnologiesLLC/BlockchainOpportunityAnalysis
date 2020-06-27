import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
import re

# Loading data from wili 2018 for testing the model
# data source: https://zenodo.org/record/841984#.XvUNopNKhYh
labels_file = 'test_set_wili-2018/labels.csv'
x_train_file = 'test_set_wili-2018/x_train.txt'
y_train_file = 'test_set_wili-2018/y_train.txt'

# lists of common languages we want to detect: 46 languages
langs = ["Gujarati", "Malayalam", "Albanian", "Punjabi", "Telugu", "Arabic", "Bulgarian", "Bengali", "Macedonian",
      "Tamil", "Tagalog", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Finnish",
      "French", "German", "Greek", "Hebrew", "Hindi", "Hungarian", "Indonesian", "Italian", "Japanese", "Korean",
      "Latvian", "Lithuanian", "Norwegian", "Persian", "Polish", "Portuguese", "Romanian", "Russian", "Slovak",
      "Spanish", "Swedish", "Thai", "Turkish", "Ukrainian", "Urdu", "Vietnamese"]

# all langauges and their encodings in wili 2018, around 250+ languages
labels_df = pd.read_csv(labels_file, sep=';')
labels_df

# change the inconsistency between the encoding in wili 2018 and common encoding
## Greek - modern Greek
## Chinese - multiple Chinese encoding
## Norwegian - Norwegian Nynorsk
labels_df['English'].replace({"Wu Chinese": "Chinese", "Cantonese": "Chinese", "Standard Chinese": 'Chinese',
                              'Hakka Chinese': 'Chinese', 'Literary Chinese': 'Chinese', 'Modern Greek': 'Greek',
                             'Norwegian Nynorsk': 'Norwegian'}, inplace=True)

lang_labels = list(labels_df[labels_df['English'].isin(langs)]['Label'])

lang_names = list(labels_df[labels_df['English'].isin(langs)]['English'])

def read_file(x_file, y_file):
    y_df = pd.read_csv(y_file, header=None)
    # y_df has only one column; name it 'Label'
    y_df.columns = ['Label']

    # Read contents of 'x_file' into a list of strings
    with open(x_file, encoding='utf8') as f:
        x_pars = f.readlines()

    # Remove all whitespace characters (such as '\n') from the beginning and the end of the strings
    x_pars = [t.strip() for t in x_pars]
    # Convert the list into a dataframe, with one column: 'Par'
    x_df = pd.DataFrame(x_pars, columns=['Par'])
    # Just keep paragraphs of languages in lang_labels (and remove other languages)
    x_df = x_df[y_df['Label'].isin(lang_labels)]
    # Just keep languages in lang_labels
    y_df = y_df[y_df['Label'].isin(lang_labels)]

    return (x_df, y_df)

# training set contains 24,000 rows of documents
x_train, y_train = read_file(x_train_file, y_train_file)

y_tr_new = y_train.merge(labels_df, on = "Label", how = "left")
y_tr_new = y_tr_new['English']


x_train_reindex = x_train.reset_index()

# FastText
#!pip install fasttext
import fasttext
# download this pretrained model
model = fasttext.load_model('fast_text_model/lid.176.ftz')

ft_predict = []
# using fastTest's pretrained model to detect documents in the training set
for i in range(len(x_train_reindex)):
    sentences = x_train_reindex['Par'][i]
    predicted_lang = model.predict(sentences)
    print(predicted_lang)
    ft_predict.append(predicted_lang[0][0][9:])


#!pip install pycountry
from pycountry import languages

# Convert the two letter encoding from fastText to full name in English
ft_names = []
for i in range(len(ft_predict)):
    if len(ft_predict[i]) != 2:
        ft_names.append('nan')
    else:
        lang_name = languages.get(alpha_2=ft_predict[i]).name
        if '(' in lang_name:
            ft_names.append(re.sub("[(\[].*?[\)]", "", lang_name)[:-1])
        else:
            ft_names.append(lang_name)


# evaluate the fastText model based on accuracy
acc = accuracy_score(y_tr_new, ft_names)
print("Accuracy: ", acc)

# Accuracy:  0.915125
