#!/usr/bin/env python3
import threading
import flask
import ariadne
import time
import os
import dotenv
import logging
from flask import Flask, redirect
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter


logging.basicConfig(filename='openMP.log', level=logging.INFO)
from lib.const import DB_UPDATE_FREQUENCY
from lib.db_conn import initDB
from lib.resolvers import query_resolver, talk_resolver, date_scalar, session_resolver, mp_resolver
from db.src import fillDB19 as db_worker

# Flask setup
worker = None
logging.info('Init Flask')
app = Flask(__name__)
logging.info('Adding limiter')
limiter = Limiter(app,
    key_func=get_remote_address,
    default_limits=["60 per hour"]
)

# GraphQL setup
schema_file = ariadne.load_schema_from_path("public/schema.graphql")
logging.info('Loaded graphql schema')
schema = ariadne.make_executable_schema(
    schema_file, query_resolver, talk_resolver, session_resolver, mp_resolver, date_scalar, ariadne.snake_case_fallback_resolvers)

@app.route('/')
def hello():
    return redirect('/graphql')

@app.route('/schema')
def docs():
    return open('public/schema.graphql', 'r', encoding='utf8').read()

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return ariadne.constants.PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = flask.request.get_json()

    success, result = ariadne.graphql_sync(
        schema,
        data,
        context_value=flask.request,
        debug=app.debug,
        mimetype="text/event-stream"
    )

    status_code = 200 if success else 400
    return flask.jsonify(result), status_code


def start():
    logging.info('Starting App')
    if os.environ.get('FLASK_ENV', 'development') == 'development':
        dotenv.load_dotenv('.env')
        logging.debug('Using .env file')
    initDB()
    return app


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        appenv = os.environ.get('FLASK_ENV', 'development')
        if appenv == 'development':
            dotenv.load_dotenv('.env')
        app = start()
        if appenv == 'development':
            app.testing = True
            app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

    except KeyboardInterrupt:
        print('Interrupt received! Closing...')
        if worker: worker.join()