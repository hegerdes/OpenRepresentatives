import matplotlib.pyplot as plt
import numpy as np
import os
from parse19 import parse, getData, getSpeaker, saveData
import json


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    all_sessions, all_speaker, all_comments = getData('../data_out/')
    all_sessions, all_speaker, all_comments = parse('../data/pp19-data')
    saveData('../data_out/', all_sessions, all_speaker, all_comments)


    role_party_map = {
        11001938: 'CDU/CSU',
        11004092: 'CDU/CSU',
        11003896: 'SPD',
        2837598228124174: 'CDU/CSU',
        11003545: '',
        11002280: '',
        11003732: '',
        11003589: '',
        11004359: '',
        11003865: '',
        11004287: '',
        11004305: '',
        11003440: '',
        11004247: '',
        11003527: '',
        11003638: '',
        11003734: '',
        11003847: '',
        999999986755: '',
        11003870: '',
        11002733: '',
        11003628: '',
        11003033: '',
        11004011: '',
        11004445: '',
        11003636: '',
        11002630: '',
        11001478: '',
        11004622: '',
        11003213: '',
        999990073: '',
        999990075: '',
        11004809: '',
        11002617: '',
        11003142: '',
        999990072: '',
        999990071: '',
        11003625: '',
        999990074: '',
        11004323: '',
        11002742: '',
        11003510: '',
        11004174: '',
        11000616: '',
        11003574: '',
        11003761: '',
        11003586: '',
        11003167: '',
        999990006: '',
        11003168: '',
        11003655: '',
        999990050: '',
        11004038: '',
        11003587: '',
        999990076: '',
        11003612: '',
        999990077: '',
        11003525: '',
        11003162: '',
        11002754: '',
        11003650: '',
        999990078: '',
        11004187: '',
        11003259: '',
        999990079: '',
        999990080: '',
        999990083: '',
        11003231: '',
        11003566: '',
        11002140: '',
        11003572: '',
        11003031: '',
        999990090: '',
        999990091: '',
        999990093: '',
        999990094: '',
        999990095: '',
        11003023: '',
        11001294: '',
        999990098: '',
        999990099: '',
        999990100: '',
        999990102: '',
        999990103: '',
        11003702: '',
        999990106: '',
        11003610: '',


    }

    for x in all_speaker.values():
        if "rolle" in x.keys() and role_party_map.get(x['id'],'') == '': print(x)

    # print('SpeakerLen', len(all_speaker), all_speaker)
    # missing = {}
    # for s in all_sessions.values():
    #     for person in s['attatchments']['missing']:
    #         for k,v in all_speaker.items():
    #             nach, vor = person.split(',')
    #             if v['nachname'] == nach.strip() and v['vorname'] == vor.strip() :
    #                     if v['id'] in missing:
    #                         missing[v['id']]['count'] += 1
    #                     else:
    #                         missing[v['id']] = {'name': vor.strip() + ' ' + nach, 'count': 1}

    # fig, ax = plt.subplots()
    # count = [i['count'] for i in missing.values() if i['count'] > 10]
    # names = [i['name'] for i in missing.values() if i['count'] > 10]

    # ax.set_xticks(range(len(names)))
    # ax.set_xticklabels(names, rotation='vertical')


    # plt.bar(np.arange(len(names)), count, align='center', alpha=0.6)
    # plt.tight_layout()
    # plt.show()