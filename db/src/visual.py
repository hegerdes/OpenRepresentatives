import matplotlib.pyplot as plt
import numpy as np
import os
from .parse19 import parse, getData, getSpeaker
import json


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    all_sessions, all_speaker, all_comments = getData('../data_out/')


    print('SpeakerLen', len(all_speaker), all_speaker)
    missing = {}
    for s in all_sessions.values():
        for person in s['attatchments']['missing']:
            for k,v in all_speaker.items():
                nach, vor = person.split(',')
                if v['nachname'] == nach.strip() and v['vorname'] == vor.strip() :
                        if v['id'] in missing:
                            missing[v['id']]['count'] += 1
                        else:
                            missing[v['id']] = {'name': vor.strip() + ' ' + nach, 'count': 1}

    fig, ax = plt.subplots()
    count = [i['count'] for i in missing.values() if i['count'] > 10]
    names = [i['name'] for i in missing.values() if i['count'] > 10]

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation='vertical')


    plt.bar(np.arange(len(names)), count, align='center', alpha=0.6)
    plt.tight_layout()
    plt.show()