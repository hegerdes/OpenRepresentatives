#!/usr/bin/python3

import requests
import re
import os

periode = 19
base_url = 'https://www.bundestag.de'
url = base_url + '/ajax/filterlist/de/services/opendata/543410-543410?limit=10&noFilterSet=true&offset='

def getFirst():
    res = requests.get(url + '0')

    start, ende = getStartEnde(res)
    return (int(res.text[start[0]+61:ende[0]-5]) - periode * 1000)//10 + 1

def getStartEnde(text):
    start = [m.start() for m in re.finditer('href', text.text)]
    ende = [m.start() for m in re.finditer('.xml', text.text)]
    return (start, ende)



def getListXML():
    urls = []
    for i in range (getFirst()):
        res = requests.get(url + str(i*10))

        start, ende = getStartEnde(res)
        for j in range(len(start)):
            urls.append(base_url + res.text[start[j]+6:ende[j]+4])
    return urls

def downloadXMLs(dw_list):
    for xmlfile in dw_list:
        if os.path.isfile('../data/pp19-data/' + xmlfile[-14:]): continue
        print('Downloading:', xmlfile)
        with open('../data/pp19-data/' + xmlfile[-14:], 'wb') as fp:
            fp.write(requests.get(xmlfile).content)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    downloadXMLs(getListXML())