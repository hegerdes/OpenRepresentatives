#!/usr/bin/env python3
import xml.etree.cElementTree as ET
from functools import cache
from datetime import date
import unicodedata
import hashlib
import json
import re
from download19 import getListXML, downloadXMLs
# import download19
import os


# https://www.bundestag.de/ajax/filterlist/de/services/opendata/543410-543410?limit=100&noFilterSet=true&offset=60
# Namentliche Abstimmungen: https://www.bundestag.de/abstimmung
DOC_BASE_URL = "https://dip21.bundestag.de/dip21/btd/{}/{}/{}.pdf"
parent_map = {}


PARAGRAPH       = 'p'
ROLL            = 'rolle'
SPEACH          = 'rede'
TABLE           = 'table'
ANLAGE          = 'anlagen'
COMMENT         = 'kommentar'
INFO_BLOCK      = 'ivz-block'
HEAD_DATA       = 'kopfdaten'
COMMENT_NAME    = 'name'
OPENING_DATA    = 'vorspann'
SESSEIO_START   = 'sitzungsbeginn'
SESSION         = 'sitzungsverlauf'
TOPIC           = 'tagesordnungspunkt'
CONTENTS        = 'inhaltsverzeichnis'

# Nice formatting
RED = '\033[1;31m'
GRN = '\033[1;32m'
YEL = '\033[1;33m'
BLU = '\033[1;34m'
GRY = '\033[1;90m'
NC  = '\033[0m'  # No Color



def handleSessionstart(session):
    comments = {}
    welcome = ['']
    start = 0

    while True:
        if session[start].tag == COMMENT_NAME or ('klasse' in session[start].attrib and session[start].attrib['klasse'] == 'N'):
            praesident = normalize(session[start].text)
            break
        start += 1
        if start == len(session):
            praesident = 'Präsident None: '
            break

    for i in range(start, len(session)):
        if session[i].tag == PARAGRAPH and session[i].text:
            if 'klasse' in session[i].attrib and session[i].attrib['klasse'] == 'redner':
                speaker = getSpeaker(session[i])
                welcome.append('{} {} ({}):'.format(speaker['vorname'], speaker['nachname'], speaker['fraktion']))
            else:
                welcome[-1] += normalize(session[i].text)
        elif session[i].tag == COMMENT and session[i].text:
            com_id = hash_calc(session[i].text)
            comments[com_id] = {'content':normalize(session[i].text[1:-1]), 'type':COMMENT}
            welcome[-1] += ' <C>' + com_id + '</C> '
        elif session[i].tag == COMMENT_NAME and session[i].text:
            if 'Präsident' in session[i].text:
                welcome.append(praesident)
            else:
                welcome.append(normalize(session[i].text))


    # No actual welcome speach given
    if len(welcome[-1]) == 0:
        return
    welcome = [re.sub(r"\s\s+" , " ", x) for x in welcome]
    praesident = re.sub(r"\s\s+" , " ", praesident)
    return {'topic': 'start', 'talks': [{'name': praesident, 'talk': welcome, 'com': list(comments.keys())}], 'comments': comments}, praesident + ' ', comments


def handeTagesordnung(topic, praesident='Präsident None: '):
    res = []
    comments = {}
    old_speaker = praesident
    curr_speaker = praesident

    for entry in topic:
        if entry.tag == PARAGRAPH and entry.text and len(entry.text) > 1:
            if len(res) > 0 and type(res[-1]) == dict:
                if curr_speaker == old_speaker:
                    res[-1]['talk'][0] += ' ' + normalize(entry.text)
                else:
                    old_speaker = curr_speaker
                    res.append({'name':curr_speaker, 'talk': [normalize(entry.text)], 'com': []})
            else:
                res.append({'name':praesident, 'talk': [normalize(entry.text)], 'com': []})
        elif entry.tag == COMMENT:
            com_id = hash_calc(entry.text)
            comments[com_id] = {'content':normalize(entry.text[1:-1]), 'type':COMMENT}
            if len(res) > 0:
                res[-1]['talk'][0] += '<C>' + com_id + '</C> '
                res[-1]['com'].append(com_id)
        elif entry.tag == SPEACH:
            rede_res = handleRede(entry, praesident)
            if (rede_res):
                old_speaker, talk, com, talk_id = rede_res
                res.append({'talkID': talk_id, 'speaker': old_speaker, 'talk': talk, 'com': list(com.keys())})
            comments = {**comments, **com}
        elif entry.tag == COMMENT_NAME:
            curr_speaker = entry.text

    return {'topic': topic.attrib['top-id'], 'talks':res, 'comments': comments}


def handleRede(rede, praesident='Präsident None: '):
    comments = {}
    talk = ['']
    for entry in rede:
        if entry.tag == PARAGRAPH and entry.attrib['klasse'] == 'redner':
            speaker = getSpeaker(entry)
            break

    praes_interupt = False
    other_speaker = speaker
    for i in range(1, len(rede)):
        if rede[i].tag == PARAGRAPH:
            if 'klasse' in rede[i].attrib and rede[i].attrib['klasse'] == 'redner':
                if getSpeaker(rede[i])['id'] != other_speaker['id'] or praes_interupt:
                    praes_interupt = False
                    other_speaker = getSpeaker(rede[i])
                    try:
                        if 'fraktion' in other_speaker.keys():
                            talk.append('{} {} ({}): '.format(other_speaker['vorname'], other_speaker['nachname'], other_speaker['fraktion']))
                        else:
                            talk.append('{} {} ({}): '.format(other_speaker['vorname'], other_speaker['nachname'], other_speaker['rolle']))
                    except KeyError: #Redner is labeld wrong
                        if rede[i][0].text: talk.append(rede[i][0].text)
            elif 'klasse' in rede[i].attrib and rede[i].attrib['klasse'] in ('AL_Partei', 'AL_Namen'):
                continue
            elif rede[i].text:
                if len(talk[-1]) > 0 and talk[-1][-1] != ' ':
                    talk[-1] += ' '
                talk[-1] += rede[i].text
        if rede[i].tag == COMMENT:
            com_id = hash_calc(rede[i].text)
            comments[com_id] = {'content':normalize(rede[i].text[1:-1]),'type': COMMENT}
            talk[-1] += ' <C>' + com_id + '</C> '
        if rede[i].tag == COMMENT_NAME and rede[i].text:
            if 'räsident' in rede[i].text:
                talk.append(praesident)
                praes_interupt = True
            elif len(rede[i].text.strip()) > 1:
                talk.append(rede[i].text + ' ')
            pass

    # No actual talk given
    if len(talk[-1]) == 0:
        return
    return (speaker, [normalize(x) for x in talk], comments, int(rede.attrib['id'][2:]))

def getSpeaker(speaker):
    speaker_dict = {}

    for entry in speaker[0][0]:
        if entry.tag == ROLL and entry[0].text:
            speaker_dict[entry.tag] = normalize(entry[0].text)
            continue
        if entry.text:
            speaker_dict[entry.tag] = normalize(entry.text)
    try: # speaker has no id ->Minister
        speaker_dict['id'] = int(speaker[0].attrib['id'])
    except ValueError:
        speaker_dict['id'] = int(hash_calc(speaker_dict['vorname'] + speaker_dict['nachname']))
    return speaker_dict

def handleAnlage(attachment):
    out = {'talks': [], 'missing': [], 'announce': [],'pub': [],'questions': [],'votes': [] }
    for anlage in attachment[1:]:
        for anlage_con in anlage:
            if 'anlagen-typ' in anlage_con.attrib.keys():
                if anlage_con.attrib['anlagen-typ'] == 'Entschuldigte Abgeordnete':
                    out['missing'] = (handleMissing(anlage_con[1][2]))
                elif anlage_con.attrib['anlagen-typ'] == 'Liste der entschuldigten Abgeordneten':
                    for par_att in anlage_con:
                        if par_att.tag == PARAGRAPH and 'klasse' in anlage_con.attrib.keys() and anlage_con.attrib['klasse'] == 'J':
                            out['missing'] = (handleMissing(par_att[0][0][1:]))
                elif anlage_con.attrib['anlagen-typ'] == "" and anlage_con[0].text == 'Entschuldigte Abgeordnete':
                    out['missing'] = (handleMissing(anlage_con[1][2]))
                elif anlage_con.attrib['anlagen-typ'] in ('Zu Protokoll gegebene Reden', 'Zu Protokoll gegebene Rede'):
                    out['talks'].append(' '.join([normalize(x.text) for x in anlage_con if x.tag == PARAGRAPH and x.text]))
                elif 'Erklärung nach' in anlage_con.attrib['anlagen-typ'] or 'Erklärungen nach' in anlage_con.attrib['anlagen-typ'] or 'Neudruck ' in anlage_con.attrib['anlagen-typ']:
                    out['announce'].append(' '.join([normalize(x.text) for x in anlage_con if x.tag == PARAGRAPH and x.text]))
                elif anlage_con.attrib['anlagen-typ'] in ('Amtliche Mitteilungen ohne Verlesung', 'Amtliche Mitteilung ohne Verlesung', 'Amtliche Mitteilung ohne Verlesung', 'Änderungsantrag', 'Erklärung'):
                    out['pub'].append(' '.join([normalize(x.text) for x in anlage_con if x.tag == PARAGRAPH and x.text]))
                elif 'Schriftliche Antworten auf Fragen der' in anlage_con.attrib['anlagen-typ']:
                    out['questions'].append('\n'.join([normalize(x.text) for x in anlage_con if x.tag == PARAGRAPH and x.text]))
                elif anlage_con.attrib['anlagen-typ'] in ('Ergebnis', 'Ergebnisse'):
                    out['votes'].append(handle_vote(anlage_con))
                elif 'Namensverzeichnis' in anlage_con.attrib['anlagen-typ']:
                    pass # ignore
                else:
                    print('Did not parse attachment:', anlage_con.tag, anlage_con.attrib)
    return out

def handle_vote(results):
    head = ' '.join([normalize(x.text) for x in results if x.tag == PARAGRAPH and x.text])
    head = head.replace('*', '\n* Anmerkung:')
    res = []
    for item in results:
        if item.tag == TABLE:
            for entry in item:
                if entry.tag in ("thead", "tbody"):
                    res.append([normalize(x.text) for x in entry[0] if x.tag in ('th', 'td')])

    res = [dict(zip(res[i], res[i+1])) for i in range(0, len(res), 2)]

    return {"voteTopic": head, "results": res}


def prot_data(data):
    meta_data = {}
    meta_data['plenarprotokollNum'] = data[0][1].text
    meta_data['periode'] = data[0][0].text
    meta_data[data[1].tag] = data[1].text
    meta_data[data[2].tag] = data[2].text
    meta_data[data[3].tag] = data[3][0].text
    meta_data[data[4][0].tag] = data[4][0].text
    split_date = [int(i) for i in data[4][1].attrib['date'].split('.')]
    meta_data[data[4][1].tag] = date(split_date[-1], split_date[1], split_date[0] )
    return meta_data

def contenstable(table):
    tables = []
    for entry in table:
        if entry.tag == INFO_BLOCK:
            tables.append(handleTableBlock(entry))
        # Maybe handle ivz-eintrag that are not in a ivz-block
        # These are minor topics
    return tables


def handleTableBlock(block):
    p_pattern = re.compile(r'\d+(\/\d+)')
    block_out = {}
    block_out['title'] = block[0].text.replace(':','')
    block_out['topics'] = []
    block_out['docs'] = []
    block_out['doc_urls'] = []
    for i in range(1, len(block)):
        if block[i].tag == PARAGRAPH:
            block_out['docs'].append(block[i].text)
        elif block[i][0].text and len(re.sub(r'\s+',' ',block[i][0].text)) > 1:
            if 'Drucksache' in block[i][0].text:
                for match in p_pattern.findall(block[i][0].text):
                    block_out['docs'].append('19' + match)
                    block_out['doc_urls'].append(DOC_BASE_URL.format('19', match[1:].rjust(5, '0')[:3], '19' + match[1:].rjust(5, '0')))
            block_out['topics'].append(block[i][0].text)
    return block_out

def handleMissing(missing):
    return [normalize(x[0].text) for x in missing]

@cache
def normalize(input, type='NFC'):
    return re.sub(r'\.(?! )', '. ', re.sub(r' +', ' ', unicodedata.normalize(type, input)))

@cache
def hash_calc(input):
    return str(int(hashlib.sha256(input.encode('utf-8')).hexdigest(), 16) % 10**16).ljust(16,'0')

def getXMLFileList(datapath):
    try:
        downloadXMLs(getListXML(), datapath)
        return [f for f in os.listdir(datapath) if os.path.isfile(os.path.join(datapath, f)) and f[-3:] == 'xml']
    except FileNotFoundError:
        print('File not found. Please check')
        exit(0)

def merge_dicts(dict1, dict2):
    pass
    for v2, k2 in dict2.items():
        if v2 in dict1:
            if 'rolle' in k2:
                if k2['rolle'] == 'Alterspräsident':
                    dict1[10000000] = {**k2, 'id': 10000000}
                    print('here')
                elif 'rolle' not in dict1[v2]:
                    dict1[v2] = {**dict1[v2], 'rolle':k2['rolle']}
                elif 'rolle' in dict1[v2] and dict1[v2]['rolle'].split(';')[-1] != k2['rolle']:
                    dict1[v2]['rolle'] += ';' + k2['rolle']
                else: dict1[v2] = {**dict1[v2], **k2}
        else:
            dict1[v2] = k2
    return dict1


def parse(datapath):
    all_sessions = {}
    all_speaker = {}
    all_comments = {}
    prot_files = None
    print('Checking files...')
    # Check if one file or data dir
    prot_files = [os.path.basename(datapath)] if os.path.isfile(datapath) and datapath[-3:] == 'xml' else getXMLFileList(datapath)

    if not prot_files:
        print('No files found! Downloading')
        downloadXMLs(getListXML(), outdir=datapath)
        prot_files = getXMLFileList(datapath)

    urls = {url[-14:]: url for url in getListXML()}
    for data_file in prot_files:
        all_sessions[data_file] = {}
        all_sessions[data_file]['topics'] = []
        print('Parsing', data_file + '...')
        root = ET.parse(os.path.join(datapath, data_file)).getroot()
        parent_map = {c: p for p in root.iter() for c in p}

        praesident = 'Präsident None: '
        for child in root:
            if child.tag == OPENING_DATA:
                for cc in child:
                    if cc.tag == HEAD_DATA:
                        all_sessions[data_file]['head'] = prot_data(cc)
                    if cc.tag == CONTENTS:
                        all_sessions[data_file]['contents'] = contenstable(cc)
            elif child.tag == SESSION:
                for cc in child:
                    if cc.tag == SESSEIO_START:
                        session_res = handleSessionstart(cc)
                        if session_res:
                            start, praesident, comm = session_res
                            all_sessions[data_file]['topics'].append(start)
                            all_comments = {**all_comments, **comm}
                    if cc.tag == TOPIC:
                        topic = handeTagesordnung(cc, praesident)
                        tmp = {speach['speaker']['id']: speach['speaker'] for speach in topic['talks'] if 'speaker' in speach}
                        all_speaker = merge_dicts(all_speaker, tmp)
                        all_comments = {**all_comments, **topic['comments']}
                        all_sessions[data_file]['topics'].append(topic)
            elif child.tag == ANLAGE:
                all_sessions[data_file]['attatchments'] = handleAnlage(child)
        all_sessions[data_file]['head']['url'] = urls[data_file]

    return all_sessions, all_speaker, all_comments


def getData(out_dir):
    try:
        all_sessions, all_speaker, all_comments = (None, None, None)
        with open(out_dir + 'content_out_tmp.json', 'r', encoding='utf8') as fp:
            all_sessions = json.load(fp)
        with open(out_dir + 'comments_out_tmp.json', 'r', encoding='utf8') as fp:
            all_comments = json.load(fp)
        with open(out_dir + 'speaker_out_tmp.json', 'r', encoding='utf8') as fp:
            all_speaker = json.load(fp)
        return all_sessions, all_speaker, all_comments
    except Exception:
        print('Can not load files. Parsing...')
        return parse(out_dir)

def saveData(out_dir, all_sessions, all_speaker, all_comments, indent=2):
    print('Saving parsed files as json to:', os.path.abspath(out_dir))
    with open(out_dir + 'content_out_tmp.json', 'w', encoding='utf8') as fp:
        json.dump(all_sessions, fp, ensure_ascii=False, default=str, indent=indent)

    with open(out_dir + 'comments_out_tmp.json', 'w', encoding='utf8') as fp:
        json.dump(all_comments, fp, ensure_ascii=False, default=str, indent=indent)

    with open(out_dir + 'speaker_out_tmp.json', 'w', encoding='utf8') as fp:
        json.dump(all_speaker, fp, ensure_ascii=False, default=str, indent=indent)



if __name__ == '__main__':

    # ToDo: Get vote results
    # Scrape Bundestag
    # https://www.bundestag.de/apps/na/na/abstimmungenForMdb.form?vaid=1970&offset=20

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    data_dir = '../data/pp19-data/'
    out_dir = '../data_out/'
    # data_dir = '../data/pp19-data/19219-data.xml'
    all_sessions, all_speaker, all_comments,  = parse(data_dir)
    saveData(out_dir, all_sessions, all_speaker, all_comments)
