#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask import Flask, render_template, redirect, make_response, session
import ScrapperEngine as se
from flask import request
import json
import os
import ScrapperMain as sm
import random
import sys
import codecs
import traceback
import time
import concurrent.futures


application = Flask(__name__, static_url_path='')
application.secret_key = '2017201820192020'
resource_path = os.path.join(application.root_path, 'searchsmart')
#reload(sys)

@application.route('/')
def index():
    print('--------------------------')
    lastsession = request.cookies.get('sessionID')
    sessionID = random.randint(100, 99999999)
    print('creating new session---- ' + str(sessionID))

    resp = make_response(render_template('landing.html', sessionID=sessionID))

    resp.set_cookie('sessionID', str(sessionID))
    resp.set_cookie('numchunks', '0')
    resp.set_cookie('block', '0')
    resp.set_cookie('numblocks', '0')

    print('lastsesison--' )
    print(lastsession)

    #se.refreshSession(resource_path, lastsession)

    print('in index :num of blocks----------------------')
    print(request.cookies.get('numchunks'))

    return resp


def replace_trash(unicode_string):
    new_string = ''
    if unicode_string is None or unicode_string == '':
        return new_string

    for i in range(0, len(unicode_string)):
        try:
            val = ord(unicode_string[i])

            if val > 128:
                if val == 228:
                    new_string = new_string + unicode_string[i].replace(unicode_string[i], 'a')
                elif val == 196:
                    new_string = new_string + unicode_string[i].replace(unicode_string[i], 'A')
                elif val == 246:
                    new_string = new_string + unicode_string[i].replace(unicode_string[i], 'o')
                elif val == 214:
                    new_string = new_string + unicode_string[i].replace(unicode_string[i], 'O')
                elif val == 252:
                    new_string = new_string + unicode_string[i].replace(unicode_string[i], 'u')
                elif val == 220:
                    new_string = new_string + unicode_string[i].replace(unicode_string[i], 'U')
                elif val == 223:
                    new_string = new_string + unicode_string[i].replace(unicode_string[i], 'ss')
                else:
                    new_string = new_string + unicode_string[i].replace(unicode_string[i], '')
            else:
                new_string = new_string + unicode_string[i]
        except:
            pass

    return new_string


@application.route('/scraper/')
def my_link():
    return 'Clicked.'


def ascii_encode_dict(data):
    ascii_encode = lambda x: x.encode('ascii')
    return dict(map(ascii_encode, pair) for pair in data.items())

@application.route('/result/')
def result():
    print('result')
    return application.send_static_file('search.html')


@application.route('/analysis/', methods=['POST', 'GET'])
def analysis():
    print('---Inside analysis----')

    cbox2 = request.form.get('cbox2')
    print(cbox2)
    key1 = request.args.get('key1')
    key2 = request.args.get('key2')
    key3 = request.args.get('key3')

    if(key1 is None):
      return 'No keyword'
    print('--------------Called Analysis cockpit----------------------------')

    innerKey = ['org']
    ext = key2.split(',')
    key3ext = key3.split(',')

    if key2 != '':
        innerKey = innerKey + ext

    if key3 != '':
        innerKey = innerKey + key3ext

    print(innerKey)

    linkresults = []
    blockedArr = ['researchgate']

    path = resource_path + "/searchresults/" + key1 + "_" + request.cookies.get("sessionID") + ".txt"
    links = []
    try:
        links = json.load(open(path))
    except:
        print('json file not found')
        pass

    print('--------')
    print(links)

    if links is not None and len(links) > 0:
        for i in range(0, len(innerKey)):
            linkresults = linkresults + links[key1][i][innerKey[i]]

    p = 0

    print('Total size of urls list before filteritng- ' + str(len(linkresults)))

    finalList = []
    for res in linkresults:
        for blckLink in blockedArr:
            if blckLink in res:
                print('removed blocked url-' + res)
                break
            else:
                finalList.append(res)

    print('Total size of urls list after filteritng- ' + str(len(finalList)))

    link_length = len(finalList)

    urlscount = 30           #if greater than this, call NBN in these number of threads
    chunkcount = 5          #if chunks cound are greater than this, run chunk in sequences. it signifies number of threads

    totalchunks = 1
    if link_length > urlscount :
        print('Number of urls is greater than ' + str(urlscount))
        totalchunks, mod = divmod(link_length,  urlscount)

        if mod > 0 :
            totalchunks = totalchunks + 1

    print('----------------------------number of THREAD in total number of BLOCKS------------------------')
    print('Numer of URLs in each chunks-- ' + str(urlscount))
    print('Total chunks-- ' + str(totalchunks))

    totalBlocks = 1
    if totalchunks > chunkcount:
        totalBlocks, modblock = divmod(totalchunks, chunkcount)

        if modblock > 0:
            totalBlocks = totalBlocks + 1

    print('Total blocks-- ' + str(totalBlocks))


    nerdsArr = []
    nextend = 0
    for c in range(0, totalchunks):
        nextstart = nextend
        nextend = (c + 1) * urlscount

        if nextend > link_length:
            nextend = link_length

        print(str(nextstart) + ' --------- ' + str(nextend))
        stringss = '['
        for k in range(nextstart, nextend):
            stringss = stringss + '"' + finalList[k] + '",'


        #remove last comma
        stringss = stringss[:-1]
        stringss = stringss + ']'
        nerdsArr.append(stringss)


    blockArr=[]
    blockArr = split_list(nerdsArr, chunkcount)
    print('----Total hit for NBN---' + str(len(blockArr)))
    print(blockArr[0])
    num_Blocks = int(request.cookies.get('numblocks'))
    print('current block number----' + str(num_Blocks))

    #############################################start process in chunks
    currentblock = 0

    #################################################
    t0 = time.time()

    block = int(request.cookies.get('block'))
    if block is None or block == 0:
        print('for block 0')
        callInChunks(blockArr[0], key1, totalchunks, currentblock)
        currentblock = block + 1
    else:
        print('Running for block- ' + str(block))
        if currentblock <= num_Blocks and block < num_Blocks:
            callInChunks(blockArr[block], key1, totalchunks, currentblock)

        currentblock = block + 1


    t1 = time.time()

    print('Time taken by fetch data -- ' + str(t1-t0))

    #####################################################
    finalStatus = 'In Progress'
    status = 0
    if num_Blocks > 0:
        status = float(currentblock / totalBlocks) * 100

    if status > 0:
        status = int(status)
        if status >= 99:
            status = 100

        finalStatus = 'Completed : ' + str(status) + ' %'
    print('current completion status---------------- ' + finalStatus)


    #####################################################

    temp1 = ''
    if len(ext) > 0:

        temp1 = ', '.join(ext)

    temp2 = ''
    if len(key3ext) > 0:
        temp2 = ', '.join(key3ext)

    dataArr = []
    lines = []

    print(len(lines))

    #data = se.readJsonFromNBN(key1, resource_path, currentchunk, request.cookies.get('sessionID'))

    data = se.readForAllJson(key1, resource_path, request.cookies.get('sessionID'), currentblock)

    if len(lines) <= 0:
        print('----------------session data is blank-------')
        lines = data
    else:
        print('appended in original data')
        for d in data :
            lines.append(d)

    print(len(lines))


    path2 = resource_path + "/keywordsJson/session_keywords" + request.cookies.get('sessionID') + ".txt"


    try:
        if(len(lines) > 0):
            with open(path2, 'w') as file:
                file.write(json.dumps(lines))
    except:
        print(traceback.format_exc())
        print('file not found for block------' + str(currentblock))
        pass

    links = []
    ngrams = []


    keywordForURL = []
    totalURLs = len(lines)
    print('---------------size of final data-----' + str(totalURLs))
    for i in lines:
        links.append(i["origUrl"])
        ngramList = i["ngrams"]

        keyList = []
        ar = 0
        for k in ngramList:
            keyList.append(k)
            ar = ar + 1
            if ar > 10:
                break

        ngrams.append(keyList)

        keys = ', '.join(keyList)

        jsonInner = {}
        jsonInner[i["origUrl"]] = []

        jsonInner[i["origUrl"]].append(keys)

        keywordForURL.append(jsonInner)


    if status == 100:
        print('redirecting to 2')
        resp = make_response(render_template('analysiscockpit2.html', data=keywordForURL, searchterm=key1,
                               otherkeys='Y', searchterm1=temp1,
                                otherkeys2 = 'Y', searchterm2 = temp2, progress=finalStatus, urlcounts=str(totalURLs)))
        resp.set_cookie('sessionID', request.cookies.get('sessionID'))
        resp.set_cookie('numchunks', str(totalchunks))
        resp.set_cookie('block', str(currentblock))
        resp.set_cookie('numblocks', str(totalBlocks))

    else:
        resp = make_response(render_template('analysiscockpit.html', data=keywordForURL, searchterm=key1,
                               otherkeys='Y', searchterm1=temp1,
                                otherkeys2 = 'Y', searchterm2 = temp2, progress=finalStatus, urlcounts=str(totalURLs)))
        resp.set_cookie('sessionID', request.cookies.get('sessionID'))
        resp.set_cookie('numchunks', str(totalchunks))
        resp.set_cookie('block', str(currentblock))
        resp.set_cookie('numblocks', str(totalBlocks))



    return resp

def split_list(the_list, chunk_size):
    result_list = []
    result_list.append(the_list[:1])
    the_list = the_list[1:len(the_list)]
    while the_list:
        result_list.append(the_list[:chunk_size])
        the_list = the_list[chunk_size:]
    return result_list

def callInChunks(nerdsArr, key1, totalchunks, currentblock):
    path2 = resource_path + "/keywordsJson/session_keywords" + request.cookies.get('sessionID') + ".txt"
    with concurrent.futures.ThreadPoolExecutor(max_workers=totalchunks) as executor:
        for ind in range(0, len(nerdsArr)):
            future = executor.submit(callNerdByNature, key1, nerdsArr[ind], resource_path, ind,
                                     request.cookies.get('sessionID'))

        executor.shutdown()
        print('-------Threads completed-------')


def callNerdByNature(key1, url, resource_path, currentchunk, sid):

    sm.callService(key1, url, resource_path, currentchunk, sid)

@application.route("/cloud/", methods=['GET', 'POST'])
def cloud():
    print('cloud')
    keyword = request.args.get('key1')
    print('-------------cloud--------------------------------' + request.cookies.get("sessionID"))

    chunks = request.cookies.get('numchunks')
    se.generateWordCloudText(keyword, resource_path, int(chunks), request.cookies.get('sessionID'))

    path1 = resource_path + "/cloudJson/" + keyword + "_" + request.cookies.get("sessionID") + ".txt"
    text = open(path1).read()

    if request.method == "GET":
        return text

    return render_template("analysiscockpit.html")



@application.route('/callSS/', methods=['POST', 'GET'])
def callSS():
    print('callSS')
    key1 = request.args['value']

    print(key1)
    if(key1 is None):
      return 'No keyword'

    return render_template('landing.html', data=key1)


def loadJsonFile(keyword, path):
    searchresultsJson = open(path, "r")

    json_data = json.loads(searchresultsJson.read())

    elements = json_data[keyword]

    size = len(elements)
    print(size)

    for elem in elements:
        urls = []
        nextKey = list(elem)

    return elements


@application.route('/', methods=['POST'])
def invokeSearch():

    print(sys.getdefaultencoding())

    searchTerm = request.form["searchterm"]
    if (searchTerm is None or len(searchTerm) < 3):
        return render_template('landing.html', result="Please enter at least 3 letters word.")

    print('---------------invoke search----------------------')
    #searchTerm = replace_trash(searchTerm)
    print('searching for ' +searchTerm)


    print(request.cookies.get('sessionID'))
    print(request.form["sessionID"])

    #cbox = ''     #first checkebox- smart forsight
    #cbox = request.form['cbox']

    dbox = request.form['dbox']             #number of records

    search_addition3 = ['checked']
        #['Crop production', 'Animal production', 'Hunting', 'Agriculture', 'Forestry', 'Logging', 'Poaching', 'Fishing', 'Aquaculture']

    dboxVal = 0
    if dbox is not None:
        dboxVal = int(dbox)

    if dboxVal == 0:
        cbox = ''


    textData2 = ''
    textData = ''
    print('##########################')
    sm.invokeSearch(searchTerm, textData, textData2, resource_path, request.cookies.get('sessionID'), dbox)


    url = request.base_url + 'analysis/?key1=' + searchTerm \
          + '&key2=' + str(textData) + '&key3=' + str(textData2)

    return redirect(url)


if __name__ == '__main__':
    print('in main')

    print(sys.getdefaultencoding())

    application.run(debug=True, threaded=True)

