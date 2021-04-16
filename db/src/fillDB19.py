import psycopg2
from .parse19 import parse, getData, getSpeaker, getXMLFileList
import os
import dotenv
import re
import time
from .visual import *


DOC_BASE_URL = "https://dip21.bundestag.de/dip21/btd/{}/{}/{}.pdf"

# ```SQL commands for table creation:

table_check = """SELECT *
FROM INFORMATION_SCHEMA.tables where table_schema='public';
"""
head = """
CREATE TABLE head (
    headID INT NOT NULL,
    session INT NOT NULL,
    period INT NOT NULL,
    publisher VARCHAR(64) DEFAULT 'Deutscher Bundestag',
    type VARCHAR(64) DEFAULT 'Stenografischer Bericht',
    title VARCHAR(64) DEFAULT '',
    place VARCHAR(64) DEFAULT 'Berlin',
    date DATE,
    url VARCHAR(512) DEFAULT '',
    PRIMARY KEY (headID)
);
"""


content = """
CREATE TABLE content (
    contentID BIGINT NOT NULL,
    sessionID INT NOT NULL,
    title VARCHAR(1024) NOT NULL,
    topics VARCHAR(16384) NOT NULL,
    PRIMARY KEY (contentID),
    FOREIGN KEY (sessionID) REFERENCES head(headID)
);
"""

parla = """
CREATE TABLE parliaments (
    resID BIGINT NOT NULL,
    f_name VARCHAR(64),
    s_name VARCHAR(64),
    party VARCHAR(64),
    role VARCHAR(128) DEFAULT 'none',
    PRIMARY KEY (resID)
);
"""

docs = """
CREATE TABLE docs (
    docID SERIAL,
    contentID INT,
    sessionID INT,
    docName VARCHAR(16) NOT NULL,
    PRIMARY KEY (docID),
    url VARCHAR(512),
    FOREIGN KEY (sessionID) REFERENCES head(headID),
    FOREIGN KEY (contentID) REFERENCES content(contentID)
);
"""

missing = """
CREATE TABLE missing (
    missingID SERIAL,
    resID BIGINT NOT NULL,
    sessionID INT NOT NULL,
    f_name VARCHAR(64) NOT NULL,
    s_name VARCHAR(64) NOT NULL,
    PRIMARY KEY (missingID),
    FOREIGN KEY (resID) REFERENCES parliaments(resID),
    FOREIGN KEY (sessionID) REFERENCES head(headID)
);
"""


comments = """
CREATE TABLE comments (
    commentID BIGINT NOT NULL,
    type VARCHAR(32) DEFAULT 'kommentar',
    content VARCHAR(4096) DEFAULT 'none',
    PRIMARY KEY (commentID)
);
"""

talks = """
CREATE TABLE talks (
    talkID BIGINT NOT NULL,
    speakerID BIGINT NOT NULL,
    speakerName VARCHAR(128) NOT NULL,
    contentID INT NOT NULL,
    sessionID INT NOT NULL,
    date DATE,
    talk TEXT NOT NULL,
    PRIMARY KEY (talkID),
    FOREIGN KEY (speakerID) REFERENCES parliaments(resID),
    FOREIGN KEY (sessionID) REFERENCES head(headID),
    FOREIGN KEY (contentID) REFERENCES content(contentID)
);
"""

talk_com = """
CREATE TABLE talk_com (
    ID SERIAL,
    talkID BIGINT NOT NULL,
    commentID BIGINT NOT NULL,
    PRIMARY KEY (ID),
    FOREIGN KEY (commentID) REFERENCES comments(commentID),
    FOREIGN KEY (talkID) REFERENCES talks(talkID)
);
"""

createTablesCmd = (head, content, parla, docs, missing, comments, talks, talk_com)
def createTables(conn, commands):
    cur = conn.cursor()
    cur.execute(table_check)
    if len(cur.fetchall()) == 0:
        print('Creating tables...')
        for command in commands:
            print('\t' + command[:26].replace('\n', ''))
            cur.execute(command)

    conn.commit()
    cur.close()

def fillHead(conn, all_sessions):
    print('Filling head data...')
    head_query = """ INSERT INTO public.head
        (headid, "session", "period", publisher, "type", title, place, "date", url)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    cur = conn.cursor()
    for k,v in all_sessions.items():
        sessionid = int(re.findall(r'\d+', k)[0])
        head = v['head']
        head_data = (sessionid, head["plenarprotokollNum"], head['periode'], head['herausgeber'], head['berichtart'], head['sitzungstitel'], head['ort'], head['datum'], head['url'] )
        cur.execute(head_query, head_data)

    conn.commit()
    cur.close()

def fillContentDocs(conn, all_sessions):
    cur = conn.cursor()
    print('Filling content & docs data...')
    contents_query = """INSERT INTO "content"
        (contentid, sessionid, title, topics) VALUES(%s, %s, %s, %s);
    """

    doc_query = """INSERT INTO docs
        (contentid, sessionid, docname, url)
        VALUES(%s, %s, %s, %s);
    """

    cur.execute('SELECT max(contentid) FROM "content"')
    res = cur.fetchall()
    counter = 1 if len(res) == 0 or res[0][0] == None else res[0][0] +1
    p_pattern = re.compile('\d+(\/\d+)')
    periode = '19'
    for k, v in all_sessions.items():
        sessionid = int(re.findall(r'\d+', k)[0])
        for content in v['contents']:
            contents_data = (counter, sessionid, content['title'], content['title']) if len(content['topics']) == 0 else (counter, sessionid, content['title'], ', '.join(content['topics']))
            cur.execute(contents_query, contents_data)
            for topic in content['topics']:
                if 'Drucksache' in topic:
                    for match in p_pattern.findall(topic):
                        url = DOC_BASE_URL.format(periode, match[1:].rjust(5, '0')[:3], periode + match[1:].rjust(5, '0'))
                        doc_data = (counter, sessionid, '19' + match, url)
                        cur.execute(doc_query, doc_data)
            counter +=1

    conn.commit()
    cur.close()

def addParla(conn, all_speaker):
    print('Filling parliaments data...')
    cur = conn.cursor()
    parla_query = """INSERT INTO parliaments
        (resid, f_name, s_name, party, role)
        VALUES(%s, %s, %s, %s, %s);
    """

    for sp in all_speaker.values():
        rep_data = None
        if 'rolle' in sp:
            rep_data = (sp['id'],sp['vorname'],sp['nachname'],None,sp['rolle'])
        else:
            rep_data = (sp['id'],sp['vorname'],sp['nachname'],sp['fraktion'],None)
        cur.execute(parla_query, rep_data)

    if not isPresidentePresent(cur):
        cur.execute(parla_query, (1, 'Sitzungs', 'Präsident', 'Präsident', 'Präsident'))
    conn.commit()
    cur.close()

def isPresidentePresent(cur):
    check_query = """SELECT * FROM parliaments WHERE resid=1;"""
    cur.execute(check_query)
    res = cur.fetchall()
    return not (len(res) == 0 or res[0][0] == None)

def fillComments(conn, all_comments):
    print('Filling comments data...')
    cur = conn.cursor()
    comm_query = """INSERT INTO "comments"
        (commentid, "type", "content")
        VALUES(%s, %s, %s);
    """

    for k, v in all_comments.items():
        comm_data = (int(k), v['type'], v['content'])
        cur.execute(comm_query, comm_data)

    conn.commit()
    cur.close()

def fillMissing(conn, all_sessions, all_speaker):
    print('Filling miss data...')
    cur = conn.cursor()

    missing_query = """INSERT INTO missing
        (resid, sessionid, f_name, s_name)
        VALUES(%s, %s, %s, %s);
    """
    for k,v in all_sessions.items():
        sessionid = int(re.findall(r'\d+', k)[0])
        for person in v['attatchments']['missing']:
            nach, vor = person.split(',')
            for k1, v1 in all_speaker.items():
                if v1['nachname'] == nach.strip() and v1['vorname'] == vor.strip() :
                    missing_data = (int(v1['id']), sessionid, v1['vorname'], v1['nachname'] )
                    cur.execute(missing_query, missing_data)
    conn.commit()
    cur.close()

def addTalks(conn, all_sessions):
    print('Filling talks data...')
    cur = conn.cursor()


    talks_query = """INSERT INTO talks
        (talkid, speakerid, speakername, contentid, sessionid, date, talk)
        VALUES(%s, %s, %s, %s, %s, %s, %s);
    """

    for k,v in all_sessions.items():
        head = v['head']
        sessionid = int(re.findall(r'\d+', k)[0])
        talkID = int(str(sessionid) + '00100')
        print('\tFilling talks from session {}...'.format(sessionid))
        cur.execute('SELECT contentid, title FROM content WHERE sessionid = %s', (sessionid,))
        query_res = cur.fetchall()
        contentID = None
        for i in range(len(v['topics'])):
            talk_IDs = []
            for talk_entry in v['topics'][i]['talks']:
                talk_IDs.append(talkID)
                try:
                    talk_data = None
                    for t in query_res:
                        if v['topics'][i]['topic'] in t[1]:
                            contentID =t[0]
                            break
                    if not contentID:
                        contentID = query_res[0][0]
                    if 'talkID' in talk_entry:
                        talkID = talk_entry['talkID']
                        talk_data = (talkID, talk_entry['speaker']['id'], talk_entry['speaker']['vorname'] + ' ' + talk_entry['speaker']['nachname'], contentID, sessionid, head['datum'], '\n'.join(talk_entry['talk']) )
                        cur.execute(talks_query, talk_data)
                        addTalkComLink(cur, talkID, talk_entry['com'])
                        talkID = talk_IDs[-1]
                    else: # Präsident talk
                        talkID += 1
                        talk_data = (talkID, 1, talk_entry['name'].replace(':',''), contentID, sessionid, head['datum'], '\n'.join(talk_entry['talk'] ))
                        cur.execute(talks_query, talk_data)
                        addTalkComLink(cur, talkID, talk_entry['com'])
                except KeyError:
                    talk_data = (talkID, talk_entry['speaker']['id'], 'Unavaiable', contentID, sessionid, head['datum'],'\n'.join(talk_entry['talk']))
                    cur.execute(talks_query, talk_data)
                    addTalkComLink(cur, talkID, talk_entry['com'])

    conn.commit()
    cur.close()

def addTalkComLink(cur, talkID, comList):
    talk_com_query = """INSERT INTO talk_com
        (talkid, commentid)
        VALUES(%s, %s);
    """
    for com in comList:
        talk_com_data = (talkID, int(com))
        cur.execute(talk_com_query, talk_com_data)

def createConnection():
    conn = None
    heroku_pg_uri = os.getenv('DATABASE_URL')
    try:
        if heroku_pg_uri:
            conn = psycopg2.connect(heroku_pg_uri)
        else:
            if os.environ.get('FLASK_ENV', 'development') == 'development': dotenv.load_dotenv('../../.env')
            conn = psycopg2.connect('dbname={} user={} password={} host={} port={}'.
                format(os.getenv('POSGRES_DB'), os.getenv('POSGRES_USER'), os.getenv('POSGRES_PW'),
                os.getenv('POSGRES_HOST'), os.getenv('POSGRES_PORT')))

    except Exception as e:
        print('Can not connect to DB. Check ConnectionString!')
        raise e
    return conn

def checkLatestDBEntry(conn):
    cur = conn.cursor()
    check_query = """SELECT max(headid) FROM head"""
    cur.execute(check_query)
    return cur.fetchall()

def filterNewEntrys(conn, all_sessions, all_speaker, all_comments):
    lastEntry = checkLatestDBEntry(conn)
    if len(lastEntry) == 0 or lastEntry[0][0] == None:
        return all_sessions, all_speaker, all_comments
    new_sessions = {}
    old_sessions = {}
    for k, v in all_sessions.items():
        sessionid = int(re.findall(r'\d+', k)[0])
        if lastEntry[0][0] and sessionid > lastEntry[0][0]:
            new_sessions[k] = v
        else:
            old_sessions[k] = v

    old_comments = {}
    old_speaker = {}
    for k, v in old_sessions.items():
        for topic in v['topics']:
            old_comments = {**old_comments, **{ck: cv for ck, cv in topic['comments'].items()}}
            old_speaker = {**old_speaker,** {speach['speaker']['id']: speach['speaker'] for speach in topic['talks'] if 'speaker' in speach}}


    new_comments_tmp = {}
    new_speaker_tmp = {}
    for k, v in new_sessions.items():
        for topic in v['topics']:
            new_comments_tmp = {**new_comments_tmp, **{ck: cv for ck, cv in topic['comments'].items()}}
            new_speaker_tmp = {**new_speaker_tmp,** {speach['speaker']['id']: speach['speaker'] for speach in topic['talks'] if 'speaker' in speach}}

    new_comments_out = {k:v for k, v in new_comments_tmp.items() if k not in old_comments}
    new_speaker_out = {k:v for k,v  in new_speaker_tmp.items() if k not in old_speaker}
    if len(new_sessions) > 0:
        print('Found {} new protocoll(s)'.format(len(new_sessions)))
    return new_sessions, new_speaker_out, new_comments_out


def updateDB():
    print('Checking DB...')
    data_dir = '../data/pp19-data/'

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    time.sleep(2)
    conn = createConnection()
    createTables(conn, createTablesCmd)

    filelist = getXMLFileList(data_dir)
    lastEntry = checkLatestDBEntry(conn)
    # Compare last db entry with latest debate session
    if lastEntry and len(lastEntry) >= 0 and lastEntry[0][0] != None and int(re.findall(r'\d+', filelist[-1])[0]) <= lastEntry[0][0]:
        print('Everythin up to date')
        return
    print('Updating DB...')
    all_sessions, all_speaker, all_comments = parse(data_dir)
    all_sessions, all_speaker, all_comments = filterNewEntrys(conn, all_sessions, all_speaker, all_comments)


    if len(all_sessions) == 0:
        print('Everythin up to date')
    else:
        print('Inserting data...')
        fillHead(conn, all_sessions)
        fillContentDocs(conn, all_sessions)
        addParla(conn, all_speaker)
        fillMissing(conn, all_sessions, all_speaker)
        fillComments(conn, all_comments)
        addTalks(conn, all_sessions)

    # Queries
    conn.commit()
    conn.close()

if __name__ == '__main__':
    updateDB()
