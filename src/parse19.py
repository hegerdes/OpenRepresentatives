import xml.etree.cElementTree as ET


tree = ET.parse('data/19013-data.xml')
root = tree.getroot()

# https://www.bundestag.de/ajax/filterlist/de/services/opendata/543410-543410?limit=100&noFilterSet=true&offset=60

def handeTagesordnung(top):
    for entry in top:
        if entry.tag == 'rede':
            handleRede(entry)

def handleRede(rede):
    speaker = getSpeaker(rede[0])
    # print(speaker, rede[1].text[:20], len(rede))

    talk = ''
    for i in range(1, len(rede)):
        if rede[i].tag == 'p' and len(rede[i]) == 0:
            talk += rede[i].text + '\n'
    print(talk)

def getSpeaker(speaker):
    speaker_dict = {}

    for entry in speaker[0][0]:
        if entry.tag == 'rolle':
            speaker_dict[entry.tag] = entry[0].text
            continue
        speaker_dict[entry.tag] = entry.text

    speaker_dict['id'] = int(speaker[0].attrib['id'])
    return speaker_dict


for child in root:
    for cc in child:
        if cc.tag == 'tagesordnungspunkt':
            handeTagesordnung(cc)
            pass
        # print(cc.tag, cc.attrib)

