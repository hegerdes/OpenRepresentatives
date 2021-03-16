import xml.etree.cElementTree as ET
import unicodedata
import hashlib
import re
import download19
import os


# https://www.bundestag.de/ajax/filterlist/de/services/opendata/543410-543410?limit=100&noFilterSet=true&offset=60
parent_map = {}

PARAGRAPH       = 'p'
ROLL            = 'rolle'
SPEACH          = 'rede'
ANLAGE          = 'anlagen'
COMMENT         = 'kommentar'
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
    welcome = ['']
    comments = {}

    if session[0].tag == COMMENT_NAME:
        praesident = normalize(session[0].text) + ' '
    else:
         praesident = 'Präsident None: '

    welcome[-1] = praesident
    for i in range(1, len(session)):
        if session[i].tag == PARAGRAPH and session[i].text:
            if 'klasse' in session[i].attrib and session[i].attrib['klasse'] == 'redner':
                speaker = getSpeaker(session[i])
                welcome.append('{} {} ({}):'.format(speaker['vorname'], speaker['nachname'], speaker['fraktion']))
            else:
                welcome[-1] +=  ' ' + normalize(session[i].text)
        elif session[i].tag == COMMENT and session[i].text:
            com_id = str(hash_calc(session[i].text))
            comments[com_id] = {'content':normalize(session[i].text), 'type':COMMENT}
            welcome[-1] += ' <C>' + com_id + '</C> '
        elif session[i].tag == COMMENT_NAME and session[i].text:
            if 'Präsident' in session[i].text:
                welcome.append(praesident)
            else:
                welcome.append(normalize(session[i].text))
        else:pass
    return praesident, {'talks': welcome, 'com': comments}


def handeTagesordnung(topic, praesident='Präsident None: '):
    skip = False
    res = []
    comments = {}
    pres_comment = ""

    for entry in topic:
        if skip and entry.tag == PARAGRAPH and entry.text:
            com_id = str(hash_calc(entry.text))
            comments[com_id] = {'content':pres_comment + ' ' + normalize(entry.text),'type': PARAGRAPH}
            res.append('<TC>' + com_id + '</TC>')
        elif entry.tag == PARAGRAPH and entry.text:
            if len(res) > 0 and type(res[-1]) == str and entry.text:
                res[-1] +=  ' ' + normalize(entry.text)
            else:
                res.append(praesident + normalize(entry.text))
            skip = False
        elif entry.tag == COMMENT:
            com_id = str(hash_calc(entry.text))
            comments[com_id] = {'content':normalize(entry.text), 'type':COMMENT}
            if len(res) > 0 and type(res[-1]) == str:
                res[-1] = res[-1] + ' <C>' + com_id + '</C> '
            else:
                res.append('<C>' + com_id + '</C>')
            skip = False
        elif entry.tag == SPEACH:
            res.append(handleRede(entry, praesident))
            # print(handleRede(entry))
            skip = False
        elif entry.tag == COMMENT_NAME:
            pres_comment = entry.text
            skip = True
        else:
            pass
            # print(RED, entry.tag, entry.text, NC)

    tmp = []
    for x in res:
        if type(x) == str:
             tmp.append(re.sub(' +', ' ', x))
        else:
            tmp.append(x)
    res = tmp
    return {'talks':res, 'com': comments}


def handleRede(rede, praesident='Präsident None: '):
    comments = {}
    talk = ['']
    for i in range(len(rede)):
        if rede[i].tag == PARAGRAPH and rede[i].attrib['klasse'] == 'redner':
            speaker = getSpeaker(rede[i])
            break

    other_speaker = speaker
    for i in range(1, len(rede)):
        if rede[i].tag == PARAGRAPH and rede[i].text:
            if 'klasse' in rede[i].attrib and rede[i].attrib['klasse'] == 'redner':
                if getSpeaker(rede[i]) != other_speaker['id']:
                    other_speaker = getSpeaker(rede[i])
                    if 'fraktion' in other_speaker.keys():
                        talk.append('{} {} ({}): '.format(other_speaker['vorname'], other_speaker['nachname'], other_speaker['fraktion']))
                    else:
                        talk.append('{} {} ({}): '.format(other_speaker['vorname'], other_speaker['nachname'], other_speaker['rolle']))
            else:
                talk[-1] += rede[i].text
        if rede[i].tag == COMMENT:
            com_id = str(hash_calc(rede[i].text))
            comments[com_id] = {'content':normalize(rede[i].text),'type': COMMENT}
            talk[-1] += ' <C>' + com_id + '</C> '
        if rede[i].tag == COMMENT_NAME and rede[i].text:
            if 'Präsident' in rede[i].text:
                talk.append(praesident)
            elif len(rede[i].text.strip()) > 1:
                talk.append(rede[i].text + ' ')
            pass
            # print(RED+  'NAME' + NC, rede[i].text[:20])
    out = [normalize(x) for x in talk]
    return (speaker, out)

def getSpeaker(speaker):
    speaker_dict = {}

    for entry in speaker[0][0]:
        if entry.tag == ROLL:
            speaker_dict[entry.tag] = entry[0].text
            continue
        speaker_dict[entry.tag] = entry.text
    try:
        speaker_dict['id'] = int(speaker[0].attrib['id'])
    except ValueError as e:
        speaker_dict['id'] = hash_calc(speaker_dict['vorname'] + speaker_dict['nachname'])
    return speaker_dict

def handleMissing(missing):
    missing_count = {}
    for x in missing:
        if not x[0].text in missing_count:
            missing_count[x[0].text] = 0
        missing_count[x[0].text] += 1
    return missing_count

def handleAnlage(attachment):
    out = {'reden': [], 'missing': [], 'announce': [],'pub': [],'questions': [] }
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
                    out['reden'].append(' '.join([normalize(x.text) for x in anlage_con if x.tag == PARAGRAPH and x.text]))
                elif 'Erklärung nach' in anlage_con.attrib['anlagen-typ'] or 'Erklärungen nach' in anlage_con.attrib['anlagen-typ'] or 'Neudruck eines Redebeitrages' in anlage_con.attrib['anlagen-typ']:
                    out['announce'].append(' '.join([normalize(x.text) for x in anlage_con if x.tag == PARAGRAPH and x.text]))
                elif anlage_con.attrib['anlagen-typ'] in ('Amtliche Mitteilungen ohne Verlesung', 'Amtliche Mitteilung ohne Verlesung', 'Amtliche Mitteilung ohne Verlesung', 'Änderungsantrag', 'Erklärung'):
                    out['pub'].append(' '.join([normalize(x.text) for x in anlage_con if x.tag == PARAGRAPH and x.text]))
                elif 'Schriftliche Antworten auf Fragen der' in anlage_con.attrib['anlagen-typ']:
                    out['questions'].append('\n'.join([normalize(x.text) for x in anlage_con if x.tag == PARAGRAPH and x.text]))
                elif 'Namensverzeichnis' in anlage_con.attrib['anlagen-typ']:
                    pass
                else:
                    print(anlage_con.tag, anlage_con.text, anlage_con.attrib)

    return out

def prot_data(data):
    meta_data = {}
    meta_data['PlenarprotokollNum'] = data[0][1].text
    meta_data['Periode'] = data[0][0].text
    meta_data[data[1].tag] = data[1].text
    meta_data[data[2].tag] = data[2].text
    meta_data[data[3].tag] = data[3][0].text
    meta_data[data[4][0].tag] = data[4][0].text
    meta_data[data[4][1].tag] = data[4][1].attrib['date']
    return meta_data

def contenstable(table):
    tables = []
    for entry in table:
        if entry.tag == 'ivz-block':
            tables.append(handleTableBlock(entry))
    return tables


def handleTableBlock(block):
    block_out = {}
    block_out['title'] = block[0].text
    block_out['topics'] = []
    block_out['docs'] = []
    for i in range(1, len(block)):
        if block[i].tag == PARAGRAPH:
            block_out['docs'].append(block[i].text)
        elif block[i][0].text and len(re.sub('\s+',' ',block[i][0].text)) > 1:
            if 'Drucksache' in block[i][0].text:
                block_out['docs'].append(block[i][0].text)
            block_out['topics'].append(block[i][0].text)
    return block_out

def normalize(input, type='NFC'):
    return unicodedata.normalize(type, input)

def hash_calc(input):
    return int(hashlib.sha256(input.encode('utf-8')).hexdigest(), 16) % 10**8

if __name__ == '__main__':
    data_dir = 'data/pp19-data'
    prot_files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    urls = {url[-14:]: url for url in download19.getListXML()}


    prot_files = ['19213-data.xml']
    all_sessions = {}
    for data_file in prot_files:
        all_sessions[data_file] = {}
        all_sessions[data_file]['topics'] = []
        print('Parsing', data_file + '...')
        root = ET.parse('data/pp19-data/' + data_file).getroot()
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
                        praesident, start = handleSessionstart(cc)
                        all_sessions[data_file]['topics'].append(start)
                    if cc.tag == TOPIC:
                        all_sessions[data_file]['topics'].append(handeTagesordnung(cc, praesident))
            elif child.tag == ANLAGE:
                all_sessions[data_file]['attatchments'] = handleAnlage(child)
        all_sessions[data_file]['head']['url'] = urls[data_file]

    import json
    # print(all_sessions)

    with open('data.json', 'w') as fp:
        json.dump(all_sessions, fp)