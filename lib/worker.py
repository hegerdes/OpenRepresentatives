from app import checkDB
import dotenv
import os
import time
import threading
from db.src import fillDB19 as db_worker
from lib.const import DB_UPDATE_FREQUENCY

while True:
    print('Starting DB update check...')
    db_worker.updateDB()
    time.sleep(DB_UPDATE_FREQUENCY)