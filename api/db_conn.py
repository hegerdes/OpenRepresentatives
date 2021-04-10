import os
import dotenv
import psycopg2
import const
import time
from const import DB_RETRY

class DB_Connection:
    def __init__(self):
        self.conn = self.createConnection()


    def createConnection(self):
        heroku_pg_uri = os.getenv('DATABASE_URL')
        docker_env = os.getenv('DOCKER_ENV')
        try:
            conn = None
            if heroku_pg_uri:
                conn = psycopg2.connect(heroku_pg_uri)
            elif docker_env:
                conn = psycopg2.connect('dbname={} user={} password={} host={} port={}'.
                    format(os.getenv('POSGRES_DB'), os.getenv('POSGRES_USER'), os.getenv('POSGRES_PW'),
                    os.getenv('POSGRES_HOST'), os.getenv('POSGRES_PORT')))
            else:
                dotenv.load_dotenv('../.env')
                conn = psycopg2.connect('dbname={} user={} password={} host={} port={}'.
                    format(os.getenv('POSGRES_DB'), os.getenv('POSGRES_USER'), os.getenv('POSGRES_PW'),
                    os.getenv('POSGRES_HOST'), os.getenv('POSGRES_PORT')))
            conn.set_session(readonly=True)
            self.conn = conn
            return self.conn
        except Exception as e:
            print('Can not connect to DB. Check ConnectionString!')
            raise e

    def fetchDB(self, query, arguments=(None, )):
        for i in range(DB_RETRY):
            if i == 2:
                print('DB connection broken. Aborting')
                raise psycopg2.Error('Can not connect to DB')
            try:
                cur = self.conn.cursor()
                cur.execute(query, arguments)
                db_res = cur.fetchall()
                cur.close()
                return db_res
            except psycopg2.Error:
                print('DB connection broken. Retry...')
                self.conn = self.createConnection()
                time.sleep(0.5)
        return




db_conn = DB_Connection()
for i in range(const.DB_RETRY):
    if db_conn.conn.closed != 0:
        time.sleep(0.5)
        db_conn.createConnection()
    else:
        print('Connected to DB')
        break
