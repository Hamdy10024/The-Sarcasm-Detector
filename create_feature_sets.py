"""
This file is responsible to take the raw sentences as input and then extract
features from them.
These feature are then stored as a numpy array in to file, that can be easily
consumed by the model.
This file needs two files with positive and regular data that is cleaned and
pre-processed. The names of the files should be 'negproc.npy' and 'posproc.npy'

set1 : the features written as comments.
set2 : set1 + pos_vector + boolean if capital words are more than threshold.
set3 : set1 + pos_vector + number of capital words.
"""

import numpy as np
from textblob import TextBlob
import nltk
import string
import exp_replace
import random

# Read the data from numpy files into arrays
sarcastic_data = np.load('posproc.npy')
regular_data = np.load('negproc.npy')

featuresets = []
classes = ["SARCASTIC", "REGULAR"]


def extractFeatures():
    """
    This method drives the feature extraction which are stored in featuresets
    array.
    :return:
    """
    # We have 4 times more Regular data as Positive data. Hence we only take
    # every 4th sentence from the Regular data.
    print("Extracting features for negative set")
    for x in regular_data[::4]:
        features = extractFeatureOfASentence(x)
        featuresets.append([features, [0, 1]])

    print("Extracting features for positive set")
    for x in sarcastic_data:
        features = extractFeatureOfASentence(x)
        featuresets.append([features, [1, 0]])

    # Shuffle the featuresets so that thy are not in any paticular order
    random.shuffle(featuresets)
    featuresets1 = np.array(featuresets)

    # Save the features into a numpy file.
    np.save('featuresets3', featuresets1)


def extractFeatureOfASentence(sen):
    """
    This method extracts features of a single sentence.
    We have following list of features being extracted.
    1. Full sentence Polarity
    2. Full sentence Subjectivity
    3. Half sentence Polarity (1/2 and 2/2)
    4. Half sentence Subjectivity (1/2 and 2/2)
    5. Difference between polarities of two halves
    6. Third sentence Polarity (1/3, 2/3 and 3/3)
    7. Third sentence Subjectivity (1/3, 2/3 and 3/3)
    8. Difference between max and min polarity of the thirds.
    9. Fourth sentence Polarity (1/4, 2/4, 3/4 and 4/4)
    10. Fourth sentence Subjectivity (1/4, 2/4, 3/4 and 4/4)
    11. Difference between max and min polarities of the fourths.

    Like this we extract 23 features of a single sentence.
    :param sen:
    :return:
    """
    features = []
    # adding capitalization feature
    counter = 0
    threshold = 4
    sentence_plain = sen.decode('UTF-8')
    for j in range(len(sentence_plain)):
        counter += int(sentence_plain[j].isupper())
    features.append(counter)
    # end of adding capitalization  feature
    # Tokenize the sentence and then convert everthing to lower case.
    tokens = nltk.word_tokenize(exp_replace.replace_emo(str(sen)))
    tokens = [(t.lower()) for t in tokens]
    # Adding pos_feature
    pos_vector = posvector(tokens)
    for j in range(len(pos_vector)):
        features.append(pos_vector[j])
    # End of adding pos_feature

    # Extract features of full sentence.
    fullBlob = TextBlob(joinTokens(tokens))
    features.append(fullBlob.sentiment.polarity)
    features.append(fullBlob.sentiment.subjectivity)
    # Extract features of halves.
    size = len(tokens) // 2
    parts = []
    i = 0
    while i <= len(tokens):
        if i == size:
            parts.append(tokens[i:])
            break
        else:
            parts.append(tokens[i:i + size])
            i += size
    for x in range(0, len(parts)):
        part = parts[x]
        halfBlob = TextBlob(joinTokens(part))
        features.append(halfBlob.sentiment.polarity)
        features.append(halfBlob.sentiment.subjectivity)
    features.append(np.abs(features[-2] - features[-4]))

    # Extract features of thirds.
    size = len(tokens) // 3
    parts = []
    i = 0
    while i <= len(tokens):
        if i == 2 * size:
            parts.append(tokens[i:])
            break
        else:
            parts.append(tokens[i:i + size])
            i += size

    ma = -2
    mi = 2
    for x in range(0, len(parts)):
        part = parts[x]
        thirdsBlob = TextBlob(joinTokens(part))
        pol = thirdsBlob.sentiment.polarity
        sub = thirdsBlob.sentiment.subjectivity
        if pol > ma:
            ma = pol
        if pol < mi:
            mi = pol
        features.append(pol)
        features.append(sub)
    features.append(np.abs(ma - mi))

    # Extract features of fourths.
    size = len(tokens) // 4
    parts = []
    i = 0
    while i <= len(tokens):
        if i == 3 * size:
            parts.append(tokens[i:])
            break
        else:
            parts.append(tokens[i:i + size])
            i += size
    ma = -2
    mi = 2
    for x in range(0, len(parts)):
        part = parts[x]
        fourthsBlob = TextBlob(joinTokens(part))
        pol = fourthsBlob.sentiment.polarity
        sub = fourthsBlob.sentiment.subjectivity
        if pol > ma:
            ma = pol
        if pol < mi:
            mi = pol
        features.append(pol)
        features.append(sub)
    features.append(np.abs(ma - mi))

    return features


def joinTokens(t):
    """
    This method joins tokes into a single text avoiding punctuations and
    special characters as required by the textblob api.
    :param t:
    :return:
    """
    s = ""
    for i in t:
        if i not in string.punctuation and not i.startswith("'"):
            s += (" " + i)
    return s.strip()


def posvector(sentence):

    pos_vector = nltk.pos_tag(sentence)
    vector = np.zeros(4)

    for j in range(len(sentence)):
        pos = pos_vector[j][1]
        if pos[0:2] == 'NN':
            vector[0] += 1
        elif pos[0:2] == 'JJ':
            vector[1] += 1
        elif pos[0:2] == 'VB':
            vector[2] += 1
        elif pos[0:2] == 'RB':
            vector[3] += 1

    return vector


if __name__ == '__main__':
    extractFeatures()
