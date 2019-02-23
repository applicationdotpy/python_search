# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 15:29:45 2018

@author: thomas.helmis
"""

import nltk
import operator

from nltk.corpus import wordnet as wn
from PyDictionary import PyDictionary


def getSynonyms(strInput,intLevel):
    currentLevel = 1
    "Returns a distinct list with second level synonyms of given word."
    output = []
    outputdict = {}
    dictionary = PyDictionary()

    output = dictionary.synonym(strInput)
    
    while currentLevel < intLevel:
        
        for value in output:
            try:
                output = output + dictionary.synonym(value)
                #output = list(sum(output,[]))
            except Exception:
                pass
                #print(Exception)
        currentLevel = currentLevel +1

    for value in output:
        try:
            nltksource = wn.synset(strInput + '.n.01')
            nltktarget = wn.synset(value + '.n.01')
            
            outputdict[value] = nltksource.path_similarity(nltktarget)
            
            print("nltkValue for " + strInput + " and " + value + ": " + str(nltksource.path_similarity(nltktarget)))
        except Exception:
            pass
        
    print(outputdict)
    return list(set(output))


if __name__ == "__main__":
    print(getSynonyms("car",2))