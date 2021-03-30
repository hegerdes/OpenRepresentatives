import os
import dotenv
import psycopg2

dotenv.load_dotenv('../.env')
conn = psycopg2.connect('dbname={} user={} password={} host={} port={}'.
        format(os.getenv('POSGRES_DB'), os.getenv('POSGRES_USER'), os.getenv('POSGRES_PW'),
        os.getenv('POSGRES_HOST'), os.getenv('POSGRES_PORT')))
