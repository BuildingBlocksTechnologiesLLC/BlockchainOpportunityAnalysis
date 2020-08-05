# laod dependencies
import pickle
import numpy as np
import pandas as pd
import os, json
from sklearn import preprocessing
import time
import re
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from sklearn.feature_extraction.text import TfidfTransformer

'''
Open files and create dataframe with the wanted features
'''
def open_file(path, domain):
    json_files = [pos_json for pos_json in os.listdir(path + domain)]
    df = pd.DataFrame(columns=['title_loc','title_org', 'salary', 'body'])
    posting = []
    for index, js in enumerate(json_files):
        with open(os.path.join(path + domain, js)) as json_file:
            if js != '.DS_Store':
                job = json.load(json_file)

                # include NER entities
                if "CompanyName" in job:
                    posting.append(js)
                    title_loc = job['Location']
                    title_org = job['CompanyName']
                    salary = job['Salary']
                    body = job['Body']
                    df.loc[index] = [title_loc, title_org, salary, body]
                else:
                    continue
    return df, posting


'''
preprocess the testing set for model prediction of the classifier
'''
def prediction(career_df,loaded_model):
    career_df = career_df.replace({'title_loc' : 'Not Found', 'title_org' : 'Not Found', 'salary' : 'Not Found'}, 0)
    career_df.loc[~career_df["title_loc"].isin([0]), "title_loc"] = 1
    career_df.loc[~career_df["title_org"].isin([0]), "title_org"] = 1
    career_df.loc[~career_df["salary"].isin([0]), "salary"] = 1

    body_list = career_df['body'].tolist()
    count_vect = CountVectorizer(max_features=100)
    x_train_counts = count_vect.fit_transform(body_list)

    tfidf_transformer = TfidfTransformer()
    x_test_tfidf = tfidf_transformer.fit_transform(x_train_counts)
    x_test_tfidf = x_test_tfidf.toarray()

    shape = x_test_tfidf.shape[0]
    salary = np.array(career_df["salary"]).reshape(shape, 1)
    feature_matrix_1 = np.concatenate([x_test_tfidf, salary], axis=1)
    title_loc = np.array(career_df["title_loc"]).reshape(shape, 1)
    title_org = np.array(career_df["title_org"]).reshape(shape, 1)
    feature_matrix_2 = np.hstack((title_loc, title_org))
    X_test = np.hstack((feature_matrix_1, feature_matrix_2))

    prediction = loaded_model.predict(X_test)
    return prediction


'''
overwrite the same json file and add one entity for the indicator of job_posting
'''
def output(path, domain, posting, prediction):
    for index, js in enumerate(posting):
        with open(path +domain+'/'+js,"r") as json_file:
            job = json.load(json_file)
            new = {}
            with open(path +domain+'/'+ js, "w") as outfile:
                if prediction[index] == 1:
                    new['job_posting'] = 'True'
                else:
                    new['job_posting'] = 'False'
                job.update(new)
                json_str = json.dumps(job, indent = 4) + "\n"
                outfile.write(json_str)


if __name__ == "__main__":
    #load trained model
    filename = 'svm_classifier.sav'
    loaded_model = pickle.load(open(filename, 'rb'))

    #file path
    predict_path = 'Data/Jobs/'

    # domain of the files
    domain = 'careers'
    career_df, posting = open_file(predict_path, domain)

    # prediction
    prediction = prediction(career_df)
    output(predict_path,domain, posting, prediction)
