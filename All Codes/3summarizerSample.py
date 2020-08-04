import csv
import datetime
import spacy
spacy.load('en_core_web_sm')
import heapq
import json
import pickle
import random
import re
import string
from collections import Counter
from pprint import pprint

import matplotlib
import matplotlib.pyplot as plt
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import pandas as pd

from nltk import ne_chunk
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from spacy import displacy
import os
from os import path

##### CHECK NECESSARY DIRECTORIES #####
if(not path.exists("summaries")):
    os.mkdir("summaries")


if(not path.exists("transcriptions")):
   print('Run second script before this one')
   exit()

##### DEFINE STOP WORDS #####
stop_words = set(
    stopwords.words('english') +
    ['i', 'he', 'me', 'she', 'it', 'them', 'her', 'him'])

##### MODEL TRAIN FUNCTIONS AND THEIR CALLS #####
def new_sp_model():
    TRAIN_DATA = [(u"my no is 8874672257", {
        "entities": [(9, 19, "PHONE")]
    }), (u"is your phone 7903390453", {
        "entities": [(14, 24, "PHONE")]
    }), (u"your phone number is 8318788891", {
        "entities": [(17, 27, "PHONE")]
    }), (u"here is my no 9003387921", {
        "entities": [(14, 24, "PHONE")]
    }), (u"here is my number 9600644223", {
        "entities": [(14, 24, "PHONE")]
    }),
        (u"my email is shivipandey11@gmail.com", {
            "entities": [(12, 34, "EMAIL")]
        }),
        (u"is your email id rules@yahoo.com", {
            "entities": [(17, 33, "EMAIL")]
        }),
        (u"your email is sourav@rediff.com", {
            "entities": [(14, 32, "EMAIL")]
        }),
        (u"here is email bcb@mail.com", {
            "entities": [(14, 27, "EMAIL")]
        }),
        (u"here my email id hello@find.in", {
            "entities": [(17, 31, "EMAIL")]
        })]
    nlp = spacy.blank('en')
    optimizer = nlp.begin_training()
    for i in range(20):
         random.shuffle(TRAIN_DATA)
         for text, annotations in TRAIN_DATA:
             nlp.update([text], [annotations], sgd=optimizer)
    #TO Optimize the summarizer depending upon the needs of the buisness partners
    batches = spacy.util.minibatch(TRAIN_DATA)
    for batch in batches:
        texts, annotations = zip(*batch)
        nlp.update(texts, annotations)
    nlp.to_disk("/newmod")
    print("Model Trained")



new_sp_model()


##### NECESSARY FUNCTIONS HERE #####


## CALLED BY EXTRACTIVE_SUMMARY() ##
def weighted_freq(sent):
    word_frequencies = {}
    for word in sent:
        if word not in word_frequencies.keys():
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1

    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / maximum_frequncy)

    return word_frequencies


## CALLED BY EXTRACTIVE_SUMMARY() ##
def sent_score_calc(text, word_frequencies):
    sentence_list = nltk.sent_tokenize(text)
    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word]
                else:
                    sentence_scores[sent] += word_frequencies[word]
    return sentence_scores

## CALLED BY CONTEXT_JSON() ##

def return_context(docu):

    nlp = spacy.load('en_core_web_sm')
    doc = nlp(docu)
    fin_dic = {}
    for ent in doc.ents:
        fin_dic[ent.text] = ent.label_
    return json.dumps(fin_dic, sort_keys=True)


## CALLED BY EACH FILE ##
def extractive_summary(f, docu):
    max_freq = weighted_freq(docu)
    sent_scores = sent_score_calc(f, max_freq)
    no_of_lines = len(docu.split('.'))
    summary_sentences = heapq.nlargest(int(no_of_lines / 3),
                                       sent_scores,
                                       key=sent_scores.get)
    #summary_sentences =sorted(sent_scores, key=sent_scores.get, reverse=True)[:int(no_of_lines/2)]  SUMMARY OF EACH LINE CAN BE GENERATED

    summary = ' '.join(i.capitalize() for i in summary_sentences)
    #print(summary)
    fileName = docu
    return summary


## CALLED BY EACH FILE ##
def context_json(p,fileName):
    dic = json.loads(return_context(p))
    d_final = {'persons': [], 'phone': [], 'emails': [], 'date': []}
    d_final['phone'].extend(re.findall(r'\d{10}', p))
    d_final['emails'].extend(re.findall(r'\S+@\S+', p))

    for a in dic:
        if dic[a] == 'PERSON':
            d_final['persons'].append(a)
        if dic[a] == 'DATE':
            d_final['date'].append(a)
    l = []
    for a in d_final:
        l.append(d_final[a])

    pd.DataFrame({k: pd.Series(l) for k, l in d_final.items()}).to_csv("summaries/"+fileName[:-4]+'output.csv',columns = ['persons','phone','emails','date'])
    # print(json.dumps(d_final))
    return json.dumps(d_final)


##### OPEN AND SUMMARISE TEXT FILES #####

for fileName in os.listdir("transcriptions/"):
    fileExactLocation = "transcriptions/"+fileName
    if(path.exists("summaries/" + fileName)):
        print(fileName+" already summarized. Moving to next. \n")
        continue
    print("Current File: "+fileName+"\n")

    f = open(fileExactLocation, 'r').read().lower()
    
    f = re.sub(r'\s+', ' ', f)
    no_of_lines = len(open(fileExactLocation, 'r').readlines())
    

    print("Original Size(in chars): "+ str(len(f)))
    print("\n")
    summaryText = extractive_summary(" ".join(f.split("\n")), docu=f)
                                     
    print("Summary Size(in chars): "+ str(len(summaryText)))
    summaryFile = "summaries/" + fileName
    sf = open(summaryFile, 'w+')
    sf.write(summaryText)
    sf.close()
    
    context_json(f,fileName)

    print("\n"+fileName+" summarized")
