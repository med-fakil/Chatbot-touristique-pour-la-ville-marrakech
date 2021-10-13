import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model

model = load_model('chatbot_model.h5')
import json
import random
from flask import session

intents = json.loads(open('job_intents.json', encoding='utf-8').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return (np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    #ERROR_THRESHOLD = 0.15
    results = [[i, r] for i, r in enumerate(res)]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    if results[0][1]>0.40:
        for r in results:
            return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    else:
        return_list.append({"intent": "nonanswer", "probability": str(0)})

    return return_list


def getResponse(ints, intents_json):
    hotel = ["almas", "sofitel", "ibis", "Moroccan", "Racine", "Labranda", "berostar", "Atlas", "Resort", "Oberoi","Fairmont", "Flashback", "Préstigia", "golf"]
    places = ["Tiskiwin","Marrakesh","Said","Berber","Ourika","Oukaimeden","Takerkoust","Jemaa","Bahia","Koutoubia","Medina","Menara"]
    L = ["downtown_places","list_places_souk","list_places_natural","list_places_museum","list_places","greeting", "goodbye", "thanks", "noanswer", "name", "listes_hotels", "options", "3stars", "4stars","5stars", "downtown_hotels", "aeroport_hotels", "hotels_services","listes_hotels_piscine"]
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']

    if tag in hotel :
        session["name"] = tag

    if tag in places:
        session["name"] = tag

    if tag in L:
        session["name"] = ""
        for i in list_of_intents:
            if (i['tag'] == tag):
                result = random.choice(i['responses'])
                break
            else:
                result = "You must ask the right questions 😕"
    else:
        for i in list_of_intents:
            if (i['tag'] == tag and i['name'] == session["name"]):
                result = random.choice(i['responses'])
                break
            else:
                result = "You must ask the right questions 😕️"

    return result, tag, session["name"]




def chatbot_response(msg):
    ints = predict_class(msg, model)
    res, tag, name = getResponse(ints, intents)
    return res, tag, name
