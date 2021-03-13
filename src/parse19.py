import xml.etree.cElementTree as ET
import unicodedata
import hashlib
import os

# https://www.bundestag.de/ajax/filterlist/de/services/opendata/543410-543410?limit=100&noFilterSet=true&offset=60
missing_count = {}
parent_map = {}

PARAGRAPH = 'p'
COMMENT = 'kommentar'
SPEACH = 'rede'
ROLL = 'rolle'
TOPIC = 'tagesordnungspunkt'
ANLAGE = 'anlage'
SESSION = 'sitzungsverlauf'
CONTENTS = 'inhaltsverzeichnis'
HEAD_DATA = 'kopfdaten'
OPENING_DATA = 'vorspann'

# Nice formatting
RED = '\033[1;31m'
GRN = '\033[1;32m'
YEL = '\033[1;33m'
BLU = '\033[1;34m'
GRY = '\033[1;90m'
NC = '\033[0m'  # No Color


def handeTagesordnung(topic):
    # tmp = parent_map[entry]

    res = []
    comments = {}
    for entry in topic:
        if entry.tag == PARAGRAPH:
            res.append(entry.text)
        elif entry.tag == COMMENT:
            com_id = str(int(hashlib.sha256(entry.text.encode('utf-8')).hexdigest(), 16) % 10**8)
            comments[com_id] = entry.text
            res.append('<C>' + com_id + '</C>')
        elif entry.tag == SPEACH:
            res.append(handleRede(entry))
        else:
            pass
            print(RED, entry.tag, entry.text, NC)

def handleRede(rede):
    speaker = getSpeaker(rede[0])
    talk = ''

    for i in range(1, len(rede)):
        if rede[i].tag == PARAGRAPH and len(rede[i]) == 0 and rede[i].text:
            talk += rede[i].text + "\n"
        if rede[i].tag == COMMENT:
            com_id = str(int(hashlib.sha256(rede[i].text.encode('utf-8')).hexdigest(), 16) % 10**8)
            talk += ' <C>' + com_id + '</C> '
    return (speaker, unicodedata.normalize("NFC", talk))

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
        print(speaker[0].attrib, speaker_dict, e)
    return speaker_dict

def handleMissing(missing):
    for x in missing:
        if not x[0].text in missing_count:
            missing_count[x[0].text] = 0
        missing_count[x[0].text] += 1
    return missing_count

def handleAnlage(attachment):
    if attachment[1][0].text == 'Entschuldigte Abgeordnete':
        handleMissing(attachment[1][1][2])
    for part in attachment:
        print(part.text)

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
    for entry in table:
        pass
        # print(entry.tag, entry.text)

if __name__ == '__main__':

    data_dir = 'data/pp19-data'
    prot_files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]

    # prot_files = ['19213-data.xml']
    for data_file in prot_files:
        print(data_file)
        root = ET.parse('data/pp19-data/' + data_file).getroot()
        parent_map = {c: p for p in root.iter() for c in p}

        for child in root:
            if child.tag == OPENING_DATA:
                for cc in child:
                    if cc.tag == HEAD_DATA:
                        prot_data(cc)
                    if cc.tag == CONTENTS:
                        contenstable(cc)
                    print(cc.tag)
            elif child.tag == SESSION:
                for cc in child:
                    if cc.tag == TOPIC:
                        handeTagesordnung(cc)
                        pass
                    if cc.tag == ANLAGE:
                        handleAnlage(cc)
