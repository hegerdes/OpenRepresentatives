#!/usr/bin/env python3
import json
import datetime
import ariadne
import re
from .const import COMMENT as CT
from .db_conn import db_conn, cache_conn

comment_pattern = re.compile("<C>\d{16}<\/C>")
comment_pattern_blank = re.compile(" <C>\d{16}<\/C>")

query_resolver = ariadne.ObjectType("Query")
talk_resolver = ariadne.ObjectType("Talk")
session_resolver = ariadne.ObjectType("Session")
date_scalar = ariadne.ScalarType("Date")


@session_resolver.field('docs')
@query_resolver.field('getDocs')
def resolveDocs(obj, info, docname= None, date = None, session_id=None):
    query = 'SELECT d.sessionid , d.docname, h."date", d.url FROM docs d JOIN head h ON d.sessionid=h.headid WHERE '
    params = []
    if obj:
        session_id = obj['id']

    # Use given docname find doc name by sessionid/date
    docs = [docname] if docname else getDocName(session_id, date)
    for docname_res in docs:
        query += 'docname=%s or '
        params.append(docname_res)
    if len(params) == 0: return []
    query = query[:-3] + ';'

    query_res = db_conn.fetchDB(query, params)
    if query_res == None:
        return []

    out = {}
    for x in query_res:
        if x[1] in out and x[0] not in out[x[1]]['session_ids']:
            out[x[1]]['session_ids'].append(x[0])
        else:
            out[x[1]] = {'session_ids': [x[0]], 'docname': x[1], 'date': x[2], 'url': x[3]}

    return list(out.values())



@talk_resolver.field('talk')
def resultTalk(obj, info, with_comments=True):
    query = 'SELECT commentid, "content" FROM "comments" where '
    if not with_comments:
        return comment_pattern_blank.sub('', obj['talk'])
    else:
        id_map = {}
        query_params = []
        matches = comment_pattern.finditer(obj['talk'])

        # Find start and end index for every match
        for x in matches:
            com_hash = obj['talk'][x.start() + 3:x.end() -4]
            id_map[com_hash] = {'start': x.start(), 'end': x.end(), 'com_str': obj['talk'][x.start():x.end()]}
            query += 'commentid=%s or '
            query_params.append(int(com_hash))
        if len(query_params) == 0: return obj['talk']
        query = query[:-3] + ';'

        query_res = db_conn.fetchDB(query, tuple(query_params))
        if query_res == None:
            return ''

        comments = [{'id': x[0], 'content': x[1], **id_map[str(x[0])]} for x in query_res]
        comments.sort(key=lambda x: x['start'])

        o_talk = obj['talk']
        for entry in comments:
             o_talk = o_talk.replace(entry['com_str'], '{} {} {}'.format(CT, entry['content'], CT))
        return o_talk


@query_resolver.field('getTalks')
def resolve_talks(obj, info, session_id=None, talk_id=None, date=None, mp_id=None, mp_name=None):
    query = 'SELECT talkid, speakerid, speakername, sessionid, "date", talk FROM talks WHERE '
    params = []
    if session_id:
        query += 'sessionid = %s and '
        params.append(int(session_id))
    if talk_id:
        query += 'talkid = %s and '
        params.append(int(talk_id))
    if date:
        query += 'date = %s and '
        params.append(date)
    if mp_id:
        query += 'speakerid = %s and '
        params.append(int(mp_id))
    if mp_id:
        query += 'mp_name = %s and '
        params.append(mp_name)
    query += '1=1;'

    query_res = db_conn.fetchDB(query, tuple(params))

    if query_res == None:
        return []
    return [{'talk_id': x[0], 'mp_id': x[1], 'name':x[2], 'session_id': x[3], 'date': x[4], 'talk': x[5]} for x in query_res]


@query_resolver.field('getSessions')
def resolv_sessions(obj, info, first=None, last=None):
    print('First: {}, Last: {}'.format(first,last))

    if first == None: first = 0     # Is periode 0 and session 0
    if last == None: last = 99999   # Is periode 99 and session 999

    query_res = db_conn.fetchDB('SELECT headid, "session", "period", publisher, "type", title, place, "date", url FROM head WHERE headid >= %s and headid <= %s ;', (first, last))
    if query_res == None:
        return {}
    return fill_session_res(obj, info, query_res)

@query_resolver.field('getSession')
def resolv_session(obj, info, session_id=None, date=None):
    query = 'SELECT headid, "session", "period", publisher, "type", title, place, "date", url FROM head WHERE '
    if session_id:
        query = (query + 'headid=%s;', (session_id,))
    else:
        query = (query + 'date=%s;', (date,))
    query_res = db_conn.fetchDB(*query)

    if query_res == None or len(query_res) == 0:
        return {}
    print(session_id, query_res)
    return fill_session_res(obj, info, query_res)[0]



def fill_session_res(obj, query_request, query_data):
    out = []
    # TODO: Check for only requestet params
    #print('Request', query_request.context.json['query'], '\nobj:', obj)
    for data in query_data:
        out.append({
        'id': data[0],
        'title': 'Plenarprotokoll {}/{}'.format(data[2], data[1]),
        'type': 'Bundestagsitzung:' + data[4],
        'periode': data[2],
        'place': data[6],
        'publisher': data[3],
        'date': data[7],
        'url': data[8],
        'talks': resolve_talks(obj, query_request, session_id=data[0]),
        'content': getContent(obj, query_request,session_id=data[0]),
        'missing': getMissing(obj, query_request, session_id=data[0])
        # docs is done by own resolver
        })
    return out

@query_resolver.field('getMissing')
def getMissing(obj, info, session_id=None, date=None, mp_id=None, mp_name=None):
    query_res = db_conn.fetchDB('select sessionid, resid, f_name, s_name FROM missing WHERE sessionid=%s;', (session_id,))
    if query_res == None:
        return []
    return [{'session_id': x[0], 'mp_id': x[1], 'name': x[2] + " " + x[3] } for x in query_res]

@query_resolver.field('getContent')
def getContent(obj, info, session_id=None, date=None):
    query= 'SELECT topics FROM "content" WHERE '
    params = []
    if session_id ==None and date == None:
        raise ValueError('Need at least one argument')

    if session_id:
        query += 'sessionid = %s and '
        params.append(int(session_id))
    if date:
        query += 'date = %s and '
        params.append(date)
    query += '1=1;'

    query_res = db_conn.fetchDB(query, tuple(params))
    if query_res == None:
        return []
    return [x[0] for x in query_res]

def getDocName(session_id = None, date = None):
    # Gets all doc names by id/name. If both none return all docnames
    query = 'SELECT docname FROM docs WHERE '
    params = []
    if session_id:
        query += 'sessionid=%s and '
        params.append(session_id)
    if date:
        query += 'date=%s and '
        params.append(date)
    query += '1=1;'
    query_res = db_conn.fetchDB(query, params)

    if query_res == None:
        return []

    return [x[0] for x in query_res]



@date_scalar.serializer
def serialize_date(value):
    return value.isoformat()

@date_scalar.value_parser
def parse_datetime_value(value):
    try:
        return datetime.date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f'"{value}" is not a valid ISO 8601 string')
