import dotenv
import os
import time
from src import fillDB19 as db_worker


#Backgrund db updater
def checkDB():
    while True:
        print('Starting DB update check...')
        db_worker.updateDB()
        time.sleep(172800)


if __name__ == '__main__':
    checkDB()