
from ariadne import constants
from flask import request, jsonify
from ariadne import make_executable_schema, graphql_sync, snake_case_fallback_resolvers, ObjectType, gql, constants
import resolvers
from flask_setup import app

type_defs = gql("""
    schema {
        query: Query
    }
    type Query {
        sessions: [Session]
        session(sessionID: ID!): Session
    }

    type Session {
        id: ID!
        title: String!
        type: String!
        place: String!
    }
""")

query = ObjectType("Query")
query.set_field("sessions", resolvers.resolv_sessions)
query.set_field("session", resolvers.resolv_session)

schema = make_executable_schema(
    type_defs, query, snake_case_fallback_resolvers
)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return constants.PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == '__main__':
    app.run()
