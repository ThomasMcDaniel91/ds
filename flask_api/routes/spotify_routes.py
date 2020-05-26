from flask import Blueprint, jsonify
from flask_api.services.spotify_service import spotify_api
from dotenv import load_dotenv
import os
import psycopg2

spotify_routes = Blueprint("spotify_routes", __name__)

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")
DB_HOST = os.getenv("DB_HOST")

@spotify_routes.route("/")
def index(): #test our DB connection and verify we can pull data out in json format.
    pg_conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        password=DB_PW, host=DB_HOST
    )
    pg_curs = pg_conn.cursor()

    query = '''SELECT * FROM tracks LIMIT 5'''

    pg_curs.execute(query)
    result = pg_curs.fetchall()

    pg_curs.close()
    pg_conn.close()
    return jsonify(result)