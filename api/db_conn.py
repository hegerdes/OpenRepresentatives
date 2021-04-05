import os
import dotenv
import psycopg2

conn = None

def createConnection():
    heroku_pg_uri = os.getenv('DATABASE_URL')
    docker_env = os.getenv('DOCKER_ENV')
    try:
        if heroku_pg_uri:
            return psycopg2.connect(heroku_pg_uri)
        elif docker_env:
            print('Using docker')
            return psycopg2.connect('dbname={} user={} password={} host={} port={}'.
                format(os.getenv('POSGRES_DB'), os.getenv('POSGRES_USER'), os.getenv('POSGRES_PW'),
                os.getenv('POSGRES_HOST'), os.getenv('POSGRES_PORT')))
        else:
            dotenv.load_dotenv('../.env')
            return psycopg2.connect('dbname={} user={} password={} host={} port={}'.
                format(os.getenv('POSGRES_DB'), os.getenv('POSGRES_USER'), os.getenv('POSGRES_PW'),
                os.getenv('POSGRES_HOST'), os.getenv('POSGRES_PORT')))

    except Exception as e:
        print('Can not connect to DB. Check ConnectionString!')
        raise e



conn = createConnection()

