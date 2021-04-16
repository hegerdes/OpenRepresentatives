from app import checkDB
import dotenv
import os
import threading
from db.src import fillDB19 as db_worker

worker = threading.Thread(target=checkDB, daemon=True)
worker.start()