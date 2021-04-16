from app import app, start, checkDB
import dotenv
import os
import threading


worker = threading.Thread(target=checkDB, daemon=True)
print('test')
if os.environ.get('FLASK_ENV', 'development') == 'production':
    worker.start()


def initApp():
    if os.environ.get('FLASK_ENV', 'development') == 'development':
        dotenv.load_dotenv('.env')
    return start()

if __name__ == "__main__":
    app.run()