
# Language Detector
Using Fasttext and pycountry we detect the language of job postings from JSON files.

## Getting Started

### Libraries Required 
*fasttext

*pycountry

### Installing
Use pip to install fasttext then download the pretrained model called fast_text_model/lid.176.ftz

Use pip to also install pycountry


## Running the program

To call the program, the format is: python lang_detect.py file_path

The program requires you to imput the path to a JSON file and then it will determine the language of the file based on the text inside the ['Body'] of the file. The output will be a new JSON with 'new_lang' appeneded to the end. Everthing else is the same other than the language


## Performance

From running on the wikiepdia text we saw an accuracy of 91.5125% with fasttext. This can be reviewed in lang_detect_eval.py

