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

@spotify_routes.route("/dummy_data")
def dummy_data(): #just some dummy data to get working with.
  dummy_list = [
            {'title': 'The Ocean - 1990 Remaster',
            'album_name': 'Houses of the Holy (1994 Remaster)',
            'artist': 'Led Zeppelin',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273441fd03f69579d36801631d9'
            },
            
            {'title': 'I Disappear',
            'album_name': 'I Disappear',
            'artist': 'Metallica',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273bfe41664b2ca1038b5e3bc6c'
            },

            {'title': 'Creeping Death (Remastered)',
            'album_name': 'Ride The Lightning (Deluxe Remaster)',
            'artist': 'Metallica',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273533fd0b248052d04e6b732c0'
            },

            {'title': "I Guess That's Why They Call It The Blues",
            'album_name': 'Too Low For Zero',
            'artist': 'Elton John',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273eb11e2abccdca41f39ad3b89'
            },

            {'title': 'Sweet Leaf - 2014 Remaster',
            'album_name': 'Master of Reality (2014 Remaster)',
            'artist': 'Black Sabbath',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273c199494ba9ea2b73e9208f91'
            }
  ]
  return jsonify(dummy_list)