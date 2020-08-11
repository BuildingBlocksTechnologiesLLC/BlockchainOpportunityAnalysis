import os
import sys

if __name__ == "__main__":
    file_path =  sys.argv[1]
    stanfordnlp = os.path.abspath("stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz")
    stanfordner = os.path.abspath("stanford-ner-4.0.0/stanford-ner.jar")
    lang_detect = os.path.abspath("lang_detect.py")

    os.system('python lang_detect.py '+file_path)
    os.system('python NLP.py '+file_path+' '+stanfordnlp+' '+stanfordner)
    os.system('python ml_classifier.py ' + file_path+'nlp')
#C:/Users/Leon/Data/Jobs/dice/0EF0C801B58186F0A53370366E92089E_
#C:/Users/Leon/Data/Jobs/linkedin/C30CBE1458C0E7EA1DBF201D62ECCC33_
#C:/Users/Leon/Data/Jobs/glassdoor/0B1A36D88FFF51944CA51A4A3B0A1C60_
