#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import webbrowser
import ScrapperEngine as se
import SearchKeywords as sk
from flask import request
import time

#Initialize configuration
def __init__(self):
    pass

def main(argv):
    print("Calling main")

    sk.searchResult("consulting")

def invokeSearch(keyword, cbox1, cbox2, path, sid, dbox):
    #print('invoke search result for search term-- ' + keyword)

    t0 = time.time()
    sk.searchResult(keyword, cbox1, cbox2, path, sid, dbox)

    t1 = time.time()

    print('Time taken by google search result -- ' + str(t1 - t0))


def callService(searchterm, stephanstring, resource_path, currentchunk, sid):
    print('Scrapper Main-callService')
    resp = se.callService(searchterm, stephanstring, resource_path, currentchunk, sid)
    return resp


def do_some_work(x, str1, str2, str3, str4, resource_path):
    print("Waiting " + str(x))
    if(x == 1):
        print("Redirecting to progress page")

        url=request.base_url + 'analysis/?key1=' + str1 + '&key2=' + str2 + '&key3=' + str3 + '&key4=' + str4
        print(url)

        webbrowser.open_new_tab('www.google.com')
        webbrowser.open_new_tab(url)

    else:
        print(resource_path)
        print("invoking search engine")
        invokeSearch(str1, str2, str3, resource_path)

def runThread(searchTerm, textData, textData2, textData3, resource_path):
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    do_some_work(1, searchTerm, textData, textData2, textData3, resource_path)
    do_some_work(2, searchTerm, textData, textData2, textData3, resource_path)

    #tasks = [asyncio.ensure_future(do_some_work(1, searchTerm, textData, textData2, textData3, resource_path)),
    #         asyncio.ensure_future(do_some_work(2, searchTerm, textData, textData2, textData3, resource_path))]

    print("before starting thread")
    #loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == "__main__":
    main(sys.argv)

