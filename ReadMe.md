# More transparency in German politics

**This is a small project to make German politics more transparent.**

## Current state:

Right now it does:
 * Download all open discussion reports from the Deutschen Bundestag
 * Parses all talks/comments and metadata
 * Puts (*almost*) everything into a DB
 * Starts a flask backend-server

## ToDo:
Things to do:
 * Make parsing more robust ✔
 * Save it to a database ✔
 * Create a WebAPI 🏃‍♂️
 * GraphQL API 🏃‍♂️
 * Cache 🏃‍♂️
 * Simple Info page calling the API
 * Add more open data
    * Scrape Bundestag
    * Twitter from politicians