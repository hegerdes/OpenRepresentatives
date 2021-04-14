#!/usr/bin/env python3
import datetime
import ariadne
import re
from .const import COMMENT as CT
from .db_conn import db_conn, cache_conn

comment_pattern = re.compile("<C>\d{16}<\/C>")
comment_pattern_blank = re.compile(" <C>\d{16}<\/C>")

query_resolver = ariadne.ObjectType("Query")        # General query
talk_resolver = ariadne.ObjectType("Talk")          # For talk argument filed
mp_resolver = ariadne.ObjectType("MP")              # For talks filed
session_resolver = ariadne.ObjectType("Session")    # For talks field
date_scalar = ariadne.ScalarType("Date")            # Date de-seralise

@query_resolver.field('getMissing')
@session_resolver.field('missing')
def getMissingMPs(obj, info, session_id = None, date=None, mp_id=None, mp_name=None, party=None):
    query = 'SELECT distinct m.resid, m.f_name, m.s_name, role, party FROM parliaments p join missing m on p.resid = m.resid JOIN head h on h.headid = m.sessionid WHERE '
    params = []

    if obj:
        if 'id' in obj: session_id = obj['id']
        if 'date' in obj: date = obj['date']

    if session_id:
        query += 'm.sessionid = %s and '
        params.append(int(session_id))
    if date:
        query += 'h.date = %s and '
        params.append(date)
    if mp_id:
        query += 'p.resid = %s and '
        params.append(int(mp_id))
    if mp_name:
        query += 'RTRIM(LTRIM(CONCAT(UPPER(p.f_name) ,\' \' ,UPPER(p.s_name)))) LIKE %s and '
        params.append(mp_name.upper())
    if party:
        query += 'UPPER(party) LIKE %s and '
        params.append(party.upper())
    query += '1=1;'

    query_res = db_conn.fetchDB(query, params)
    if query_res == None or len(query_res) == 0:
        return []

    return [{'mp_id': x[0], 'f_name': x[1], 's_name': x[2], 'role': x[3], 'party':x[4]} for x in query_res]




@mp_resolver.field('missed')
def getMissedSessions(obj, info, date=None, mp_id=None, mp_name=None):
    all_sessions = {session['id']: session for session in resolv_sessions(obj,info)}
    query = 'SELECT sessionid, resid, f_name, s_name FROM missing WHERE '
    params = []

    if obj:
        if 'mp_id' in obj: mp_id = obj['mp_id']
        if 'f_name' in obj and 's_name' in obj: mp_name = obj['f_name'] + ' ' + obj['s_name']

    if date:
        query += 'date = %s and '
        params.append(date)
    if mp_id:
        query += 'resid = %s and '
        params.append(int(mp_id))
    if mp_name:
        query += 'RTRIM(LTRIM(CONCAT(UPPER(f_name) ,\' \' ,UPPER(s_name)))) LIKE %s and '
        params.append(mp_name.upper())
    query += '1=1;'

    query_res = db_conn.fetchDB(query, params)
    if query_res == None or len(query_res) == 0:
        return []
    return [all_sessions[x[0]] for x in query_res]


@query_resolver.field('getMP')
def resolveMP(obj, info, mp_id=None, name=None):
    res = resolveMPs(obj, info, mp_id=mp_id, name=name)
    return res[0] if len(res) > 0 else None

@query_resolver.field('getMPs')
def resolveMPs(obj, info, mp_id=None, name=None, party=None, role=None):
    query = 'SELECT resid, f_name, s_name, party, role FROM parliaments WHERE '
    params = []
    if mp_id:
        query += 'resid = %s and '
        params.append(int(mp_id))
    if party:
        query += 'UPPER(party) LIKE %s and '
        params.append(party.upper())
    if role:
        query += 'UPPER(role) LIKE %s and '
        params.append(role.upper())
    if name:
        query += 'RTRIM(LTRIM(CONCAT(UPPER(f_name) ,\' \' ,UPPER(s_name)))) LIKE %s and '
        params.append(name.upper())
    query += '1=1;'

    query_res = db_conn.fetchDB(query, params)
    if query_res == None or len(query_res) == 0:
        return []

    return [{'mp_id': x[0], 'f_name': x[1], 's_name': x[2], 'party': x[3], 'role': x[4]} for x in query_res]


@session_resolver.field('docs')
@query_resolver.field('getDocs')
def resolveDocs(obj, info, docname= None, date = None, session_id=None):
    query = 'SELECT d.sessionid , d.docname, h."date", d.url FROM docs d JOIN head h ON d.sessionid=h.headid WHERE '
    params = []
    if obj:
        if 'id' in obj: session_id = obj['id']

    # Use given docname or find doc name by sessionid/date
    docs = [docname] if docname else getDocName(session_id, date)
    for docname_res in docs:
        query += 'docname=%s or '
        params.append(docname_res)
    if len(params) == 0: return []
    query = query[:-3] + ';'

    query_res = db_conn.fetchDB(query, params)
    if query_res == None or len(query_res) == 0:
        return []

    out = {}
    for x in query_res:
    # Ony one result entry per session.
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

        query_res = db_conn.fetchDB(query, query_params)
        if query_res == None or len(query_res) == 0:
            return ''

        comments = [{'id': x[0], 'content': x[1], **id_map[str(x[0])]} for x in query_res]
        comments.sort(key=lambda x: x['start'])

        o_talk = obj['talk']
        for entry in comments:
             o_talk = o_talk.replace(entry['com_str'], '{} {} {}'.format(CT, entry['content'], CT))
        return o_talk

@session_resolver.field('talks')
@mp_resolver.field('talks')
@query_resolver.field('getTalks')
def resolve_talks(obj, info, session_id=None, talk_id=None, date=None, mp_id=None, mp_name=None):
    if obj:
        if 'mp_id' in obj: mp_id = obj['mp_id']
        if 'id' in obj: session_id = obj['id']

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
    if mp_name:
        query += 'UPPER(mp_name) LIKE %s and '
        params.append(mp_name.upper())
    query += '1=1;'

    query_res = db_conn.fetchDB(query, params)

    if query_res == None or len(query_res) == 0:
        return []
    return [{'talk_id': x[0], 'mp_id': x[1], 'name':x[2], 'session_id': x[3], 'date': x[4], 'talk': x[5]} for x in query_res]


@query_resolver.field('getSessions')
def resolv_sessions(obj, info, first=None, last=None):
    if first == None: first = 0     # Is periode 0 and session 0
    if last == None: last = 99999   # Is periode 99 and session 999

    query_res = db_conn.fetchDB('SELECT headid, "session", "period", publisher, "type", title, place, "date", url FROM head WHERE headid >= %s and headid <= %s ;', (first, last))
    if query_res == None or len(query_res) == 0:
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
    return fill_session_res(obj, info, query_res)[0]



def fill_session_res(obj, info, query_data):
    # Fields missing, content, talks, docs are done by own resolvers
    out = []
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
        })
    return out


@session_resolver.field('content')
@query_resolver.field('getContent')
def getContent(obj, info, session_id=None, date=None):
    if obj:
        if 'id' in obj: session_id = obj['id']

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

    query_res = db_conn.fetchDB(query, params)
    if query_res == None or len(query_res) == 0:
        return []
    return [x[0] for x in query_res]

def getDocName(session_id = None, date = None):
    # Gets all doc names by id/name. If both are None return all docnames
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

    if query_res == None or len(query_res) == 0:
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
