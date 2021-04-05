
import flask
import ariadne
import resolvers
from flask_setup import app
import os

schema_file = ariadne.load_schema_from_path("schema.graphql")
query = ariadne.ObjectType("Query")
query.set_field("sessions", resolvers.resolv_sessions)
query.set_field("session", resolvers.resolv_session)

schema = ariadne.make_executable_schema(
    schema_file, query, ariadne.snake_case_fallback_resolvers
)

@app.route('/')
def hello():
    return 'HiThere!'

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
        debug=app.debug
    )

    status_code = 200 if success else 400
    return flask.jsonify(result), status_code


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(host='0.0.0.0')

