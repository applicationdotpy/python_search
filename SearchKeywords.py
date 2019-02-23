#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
import re
#from ehp import Html

def searchResult(keyword, cbox1, cbox2, path, sid, dbox):

    numOfPage = 1
    if dbox is not None:
        numOfPage = int(dbox)

    print('number of pages-- ' + str(numOfPage))

    data = {}
    data[keyword] = []

    arr = ['org']
    if cbox1:
        arr1 = cbox1.split(',')
        for elem in arr1:
            arr.append(elem)

    if cbox2:
        arr2 = cbox2.split(',')
        for elem in arr2:
            if elem != '':
                arr.append(elem)



    try:

        print('###########################')

        for arrElem in arr:
            if arrElem == 'org':
                searchterm = keyword
            else:
                searchterm = keyword + "+" + arrElem

            resultcount = 0
            print("---------------" + searchterm)

            str1 = "https://www.google.de/search?q="
            jsonInner = {}
            jsonInner[arrElem] = []
            for index in range(0, numOfPage):

                str2 = "&start=" + str(resultcount)
                print(str1 + searchterm + str2)
                page = requests.get(str1 + searchterm + str2)


                print('------------inside-scraping---------------')
                reg = re.compile(".*&sa=")

                soup = BeautifulSoup(page.text)
                print(page.text)
                a = set()
                # Parsing web urls
                for item in soup.find_all('h3', attrs={'class': 'r'}):
                    print('-------iterating html elements-')

                    if not item.find('a'):
                        print('missing a tag')
                        continue

                    temp = item.a['href'][:7]
                    if temp != '/url?q=':
                        continue


                    print(temp)
                    line = (reg.match(item.a['href'][7:]).group())

                    if line[:-4] in a:
                        print('url already added')
                        continue

                    a.add(line[:-4])

                    print(line[:-4])
                    if 'youtube' not in line:
                        jsonInner[arrElem].append(line[:-4])


                resultcount += 10

            data[keyword].append(jsonInner)

        print(data)

        fileName = path + "/searchresults/" + keyword + "_" + sid + ".txt"
        print(fileName)
        with open(fileName, "w") as outfile:
            json.dump(data, outfile)
            outfile.close()
    except Exception as exp:
        print("error in searchresult method")
        print(exp)



