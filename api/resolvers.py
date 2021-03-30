from db_conn import conn

def resolv_sessions(obj, info):
    cur = conn.cursor()
    cur.execute('SELECT headid, "session", "period", publisher, "type", title, place, "date", url FROM head;', (None,))
    query_res = cur.fetchall()
    cur.close()
    print('obj',obj)
    print('info',info)

    # print(query_res)
def resolv_session(obj, info, sessionID):
    cur = conn.cursor()
    cur.execute('SELECT headid, "session", "period", publisher, "type", title, place, "date", url FROM head WHERE session=%s;', (sessionID,))
    query_res = cur.fetchall()
    cur.close()
    return {'id': sessionID, 'title': query_res[0][8], 'type': query_res[0][4], 'palce': query_res[0][6]}

def resolv_sessionDemo(obj, info):
    return {'id': 1, 'title': 'Hi there', 'type': 'Session', 'palce': 'berlin'}