import sys
from textblob import TextBlob
import spacy
import fasttext

if __name__ == '__main__':
    Json_path = sys.argv[1]
    b = TextBlob("bonjour")
    print(b.detect_language())
