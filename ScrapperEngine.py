#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
import requests
import string
import re
import os
import shutil
import time


def isPunct(word):
  return len(word) == 1 and word in string.punctuation

def isNumeric(word):
  try:
    float(word) if '.' in word else int(word)
    return True
  except ValueError:
    return False

class ScrapperEngine:
    def __init__(self):
        #self.stopwords = set(nltk.corpus.stopwords.words())
        self.top_fraction = 1


    def substring(self, s, start, end):
        return s[start:end]

    def chunkstring(self, string, length):
        return (string[0 + i:length + i] for i in range(0, len(string), length))


def generateWordCloudText(keyword, rs_path, chunks, sid):
    print('START-ScrapperEngine-generateWordCloudText()')

    keywordjson = []
    keywordForURL = []

    dir_name = rs_path + "/keywordsJson/" + sid + "/"
    txtFiles = os.listdir(dir_name)

    print(len(txtFiles))
    for item in txtFiles:
        filePath = dir_name + item

        try:
            f = open(filePath)
            jsonextract = f.read()

            jsonextract = json.loads(jsonextract)
            resultJson = jsonextract["results"]
            titlesJson = jsonextract["docs"]


            for i in resultJson:
                keywordjson.append({"text": i["keyword"], "size": i["relevance"]})

            for i in titlesJson:
                keywordForURL.append({"origUrl": i["origUrl"], "id": i["id"], "ngrams": i["ngrams"]})

        except:
            pass


    fileName = rs_path + "/cloudJson/" + keyword + "_" + sid + ".txt"


    with open(fileName, "w") as outfile:
        json.dump(keywordjson, outfile)
        outfile.close()


    print('END-ScrapperEngine-generateWordCloudText()')



def readJsonFromNBN(keyword, rs_path, currentchunk, sid):
    print('START-ScrapperEnginer-readJsonFromNBN()')
    path1 = rs_path + "/keywordsJson/" + keyword + "_" + str(currentchunk) +  "_" + sid + ".txt"

    f = open(path1)
    print('---------reading Kewords JSON file-------')
    #print(f)
    keywordForURL = []

    try:
        jsonextract = f.read()
        jsonextract = json.loads(jsonextract)
        titlesJson = jsonextract["docs"]

        for i in titlesJson:
            temp = i["summary"]
            temp2 = ' '.join(temp)
            temp3 = clean_html(temp2)

            person = i["ents"]
            personList = person["pers"]
            personStr = ', '.join(personList)

            keywordForURL.append({"origUrl": i["origUrl"], "ngrams": i["ngrams"], "summary": temp3, "persons":personStr})
    except:
        print('Error in ScrapperEnginer-readJsonFromNBN(). Json file might missing for ' + path1)
        pass

    print('END-ScrapperEngine-readJsonFromNBN()')

    return keywordForURL

def readForAllJson(keyword, rs_path, sid, currBlock):
    print('START-ScrapperEnginer-readForAllJson()')
    dir_name = rs_path + "/keywordsJson/" + str(sid) + "/"

    print('---------dir name-----------')
    print(dir_name)
    keywordForURL = []
    try:
        txtFiles = os.listdir(dir_name)

        print(len(txtFiles))
        for item in txtFiles:
            filePath = dir_name + item
            print(filePath)

            try:
                f = open(filePath)
                print('---------reading Kewords JSON file-------')

                jsonextract = f.read()

                jsonextract = json.loads(jsonextract)
                titlesJson = jsonextract["docs"]

                for i in titlesJson:
                    temp = i["summary"]
                    temp2 = ' '.join(temp)
                    temp3 = clean_html(temp2)

                    person = i["ents"]
                    personList = person["pers"]
                    personStr = ', '.join(personList)

                    keywordForURL.append({"origUrl": i["origUrl"], "ngrams": i["ngrams"], "summary": temp3, "persons":personStr})
            except:
                print('no json found for ' + item)
                pass

    except:
        print('Error in ScrapperEnginer-readForAllJson(). Json file might missing for ' + str(sid))
        pass

    print('END-ScrapperEngine-readForAllJson()')

    return keywordForURL


def clean_html(html):
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()

def refreshSession(resource_path, sid):
    try:

        if sid is not None and sid != '':

            dir_name = resource_path + "/keywordsJson/" + sid

            if os.path.isdir(dir_name):
                print(dir_name)
                shutil.rmtree(dir_name)

    except OSError:
        pass

    ##remove session_keywords
    try:
        if sid is not None and sid != '':
            dir_name = resource_path + "/keywordsJson/session_keywords" + sid + ".txt"

            os.path.exists(dir_name)
            os.remove(dir_name)

    except OSError:
        pass


    try:

        dir_name = resource_path + "/cloudJson/"
        txtFiles = os.listdir(dir_name)

        endStr = ".txt"
        if sid is not None and sid != '':
            endStr = sid + ".txt"

        for item in txtFiles:
            if item.endswith(endStr):
                os.remove(os.path.join(dir_name, item))

    except OSError:
        pass

    try:
        dir_name = resource_path + "/searchresults/"
        txtFiles = os.listdir(dir_name)

        endStr = ".txt"
        if sid is not None and sid != '':
            endStr = sid + ".txt"

        for item in txtFiles:
            if item.endswith(endStr):
                os.remove(os.path.join(dir_name, item))

    except OSError:
        pass


def callService(searchterm, stringss, resource_path, currentchunk, sid):
    print('START-Scrapper Engine-callService()')

    p = {'urls': stringss, 'output': 'json'}

    folderName = resource_path + "/keywordsJson/" + sid + "/"
    if not os.path.exists(folderName):
        os.makedirs(folderName)

    r = requests.post("http://nerdbynature.net/nlp/kwgenerator.php", params=p)

    txt = writeIntoFolder(r, folderName, searchterm, currentchunk, stringss)
    print('END-ScrapperEngine-callService()')

    return txt


def writeIntoFolder(r, folderName, searchterm, currentchunk, stephanstring):
    t = time.time()
    fileName = folderName + searchterm + "_" + str(currentchunk) + "_" + str(t) + ".txt"

    print('writeIntoFolder: creating new keyword file-- ' + fileName)
    if r.text == '':
        print('--------------------------No data return from nerdbynature for-------------------')
        print(stephanstring)
    else :
        print(r.text[1:50])

    f = open(fileName, "w+")
    f.write(r.text)
    f.close()

    return r.text



def scrapingEngine(keyword, cbox1, cbox2, rs_path):
    print("calling scraping engine")



## can be used for testing, later it can be removed.
def main(argv):
    print("calling main function")


if __name__ == "__main__":
    main(sys.argv)

