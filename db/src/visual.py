import matplotlib.pyplot as plt
import numpy as np
import os
# from parse19 import parse, getData, getSpeaker
import json

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
        # return parse(out_dir)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    all_sessions, all_speaker, all_comments = getData('../data_out/')


    role_partz_map = {
    '11003761': '',
    '11003167': '',
    '11003440': '',
    '999990071': '',
    '11004622': '',
    '11003610': '',
    '11003168': '',

    }

    for x in all_speaker.values():
        if "rolle" in x.keys(): print(x['id'])

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