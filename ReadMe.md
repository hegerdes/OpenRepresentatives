# More transparency in German politics

**This is a small project to make German politics more transparent.**

## Heroku demo:
See [LiveDemo](https://open-representatives.herokuapp.com/graphql) here
___
## Current state:

Right now it does:
 * Download all open discussion reports from the Deutschen Bundestag
 * Parses all talks/comments and metadata
 * Puts (*almost*) everything into a DB
 * Starts a flask backend-server with gunicorn



## How to setup dev:
 * Rename the ``.env_example`` to ``.env``
 * Rename the ``api/db/cache/redis.conf.example`` to ``api/db/cache/redis.conf``
 * Change the pw in redis.conf to the one in your .env file [HowTo](https://stackink.com/how-to-set-password-for-redis-server/)
 * Run docker-compose up or use the [.dev-container](/.devcontainer)

___
## ToDo:
Things to do:
 * ✅ Make parsing more robust
 * ✅ Save it to a database
 * ✅ GraphQL API
 * ✅ Create a WebAPI
 * 🏃‍♂️ Logging
 * 🏃‍♂️ Cache
 * 🏃‍♂️ Deployment
   * Heroku free dynamo sleeps after 30 min
   * PosgresDB is limited to 10.000 rows (current 250k)
 * 🏃‍♂️ Demo Frontend
   * Under Development at [hegerdes/OpenRepresentatives-frontend](https://github.com/hegerdes/OpenRepresentatives-frontend)
 * ⏲ Add more open data
    * Scrape Bundestag
    * Twitter from politicians

