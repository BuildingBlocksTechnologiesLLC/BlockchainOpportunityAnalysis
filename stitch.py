import os
import sys

if __name__ == "__main__":
    file_path =  sys.argv[1]
    stanfordnlp = os.path.abspath("stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz")
    stanfordner = os.path.abspath("stanford-ner-4.0.0/stanford-ner.jar")
    lang_detect = os.path.abspath("lang_detect.py")

    os.system('python lang_detect.py '+file_path)
    os.system('python NLP.py '+file_path+' '+stanfordnlp+' '+stanfordner)
#C:/Users/Leon/BlockchainOpportunityAnalysis/1A59381DB3930572751963C81E2B6E2D_