import time
import psycopg2
from const import DBRETRY
from db_conn import conn, createConnection


def resolv_sessionDemo(obj, info):
    return {'id': 1, 'title': 'Hi there', 'type': 'Session', 'palce': 'berlin'}


def resolv_sessions(obj, info, first=None, last=None):
    print('obj',obj)
    print('info',info)
    print('First: {}, Last: {}'.format(first,last))

    query_res = fetchDB(('SELECT headid, "session", "period", publisher, "type", title, place, "date", url FROM head;', (None,)))
    if query_res == None:
        return {}
    return fillres(info, query_res)


def resolv_session(obj, info, sessionID):
    query_res = fetchDB(('SELECT headid, "session", "period", publisher, "type", title, place, "date", url FROM head WHERE session=%s;', (sessionID,)))
    if query_res == None:
        return {}
    return fillres(info, query_res)[0]


def fillres(query_request, query_data):
    out = []
    for data in query_data:
        out.append({
        'id': data[0],
        'title': 'Plenarprotokoll {}/{}'.format(data[2], data[1]),
        'type': 'Bundestagsitzung:' + data[4],
        'periode': data[2],
        'place': data[6],
        'publisher': data[3],
        'date': data[7].strftime('%Y-%m-%d'),
        'url': data[8],
        'docs': None,
        'talks': None,
        'content': getContent(data[0]),
        'missing': None
        })
    return out

def getContent(sessionID):
    query_res = fetchDB((('SELECT topics FROM "content" WHERE sessionID=%s'), (sessionID,)))
    if query_res == None:
        return {}
    return [x[0] for x in query_res]


def fetchDB(query):
    for i in range(DBRETRY):
        if i == 2:
            print('DB connection broken. Aborting')
            raise psycopg2.Error('Can not connect to DB')
        try:
            cur = conn.cursor()
            cur.execute(*query)
            db_res = cur.fetchall()
            cur.close()
            return db_res
        except psycopg2.Error:
            print('DB connection broken. Retry...')
            createConnection()
            time.sleep(0.5)
    return


