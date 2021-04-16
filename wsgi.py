from app import app, start, checkDB
import dotenv
import os
import threading
from db.src import fillDB19 as db_worker

# worker = threading.Thread(target=checkDB, daemon=True)
# if os.environ.get('FLASK_ENV', 'development') == 'production':
#     worker.start()

# db_worker.updateDB()

def initApp():
    if os.environ.get('FLASK_ENV', 'development') == 'development':
        dotenv.load_dotenv('.env')
    return start()

if __name__ == "__main__":
    app.run()