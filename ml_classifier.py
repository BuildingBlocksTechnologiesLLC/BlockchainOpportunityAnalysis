# load dependencies
import pickle
import numpy as np
import pandas as pd
import os, json
from sklearn import preprocessing
import time
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# load the model from disk
filename = 'svm_classifier.sav'
loaded_model = pickle.load(open(filename, 'rb'))
# load the trained dictionary for vocab
with open('vocab.pickle', 'rb') as handle:
    vocab = pickle.load(handle)

'''
Open files and create dataframe with the wanted features
'''
def open_file(path):
    df = pd.DataFrame(columns=['title_loc','title_org', 'salary', 'body'])
    with open(path ,"r") as json_file:
        job = json.load(json_file)

        # include NER entities
        if "CompanyName" in job:
            title_loc = job['Location']
            title_org = job['CompanyName']
            salary = job['Salary']
            body = job['Body']
            df.loc[0] = [title_loc, title_org, salary, body]
    return df


'''
preprocess the testing set for model prediction of the classifier
'''

def prediction(career_df):
    career_df = career_df.replace({'title_loc' : 'Not Found', 'title_org' : 'Not Found', 'salary' : 'Not Found'}, 0)
    career_df.loc[~career_df["title_loc"].isin([0]), "title_loc"] = 1
    career_df.loc[~career_df["title_org"].isin([0]), "title_org"] = 1
    career_df.loc[~career_df["salary"].isin([0]), "salary"] = 1

    import preprocessing as prep
    # function to perform lemmatize and stem preprocessing steps on the data set.
    preprocessor = prep.Preprocessor(career_df['body'])
    preprocessor.preprocess(lemmatize=True, stopwords=[], min_token_length=3)
    preprocessor.get_bigrams_from_preprocessed()
    preprocessed_text = preprocessor.preprocessed_text_

    body_list = []
    for i, arr in enumerate(preprocessed_text):
        l = ' '.join(preprocessed_text[i])
        body_list.append(l)

    vectorizer2 = TfidfVectorizer(vocabulary= vocab)
    x_test_tfidf = vectorizer2.fit_transform(body_list)
    x_test_tfidf = x_test_tfidf.toarray()
    shape = x_test_tfidf.shape[0]
    salary = np.array(career_df["salary"]).reshape(shape, 1)
    feature_matrix_1 = np.hstack((x_test_tfidf, salary))
    title_loc = np.array(career_df["title_loc"]).reshape(shape, 1)
    title_org = np.array(career_df["title_org"]).reshape(shape, 1)
    feature_matrix_2 = np.hstack((title_loc, title_org))
    X_test = np.hstack((feature_matrix_1, feature_matrix_2))

    predict = loaded_model.predict(X_test)
    return predict


'''
overwrite the same json file and add one entity for the indicator of job_posting
'''
def output(path, predict):
    with open(path,"r") as json_file:
        job = json.load(json_file)
        new = {}
        with open(path, "w") as outfile:
            if predict[0] == 1:
                new['job_posting'] = 'True'
            else:
                new['job_posting'] = 'False'
            job.update(new)
            json_str = json.dumps(job, indent = 4) + "\n"
            outfile.write(json_str)


if __name__ == "__main__":
    # file path
    predict_path = 'Data/Jobs/careers/swazm_BC8818A7EC327C93BC7FFDFA6FE94327_'
    career_df = open_file(predict_path)

    # prediction
    predict = prediction(career_df)
    output(predict_path, predict)
