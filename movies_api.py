# To run program:  python3 movies_api.py

# README:  if conn error make sure password is set properly in RDS PASSWORD section
# README:  Debug Mode may need to be set to False when deploying live (although it seems to be working through Zappa)
# README:  if there are errors, make sure you have all requirements are loaded

print("In Movies 2")

import os
import boto3
# import json
# import sys
# import json
import pytz
import pymysql
import requests
# import stripe
# from fuzzywuzzy import fuzz
import numpy as np
import pandas as pd


from dotenv import load_dotenv
from datetime import date, datetime
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
# from flask_mail import Mail, Message
from werkzeug.exceptions import BadRequest, InternalServerError
from decimal import Decimal
# from hashlib import sha512
from gensim.models import Word2Vec
from io import StringIO

#  NEED TO SOLVE THIS
# from NotificationHub import Notification
# from NotificationHub import NotificationHub

# BING API KEY
# Import Bing API key into bing_api_key.py

#  NEED TO SOLVE THIS
# from env_keys import BING_API_KEY, RDS_PW


# app = Flask(__name__)
app = Flask(__name__, template_folder="assets")
api = Api(app)
# load_dotenv()
os.environ['FLASK_ENV'] = 'development'

# CORS(app)
CORS(app, resources={r'/api/*': {'origins': '*'}})

# Set this to false when deploying to live application
app.config['DEBUG'] = True


# --------------- Google Scopes and Credentials------------------




# --------------- Stripe Variables ------------------




# --------------- Mail Variables ------------------




# --------------- Time Variables ------------------
# convert to UTC time zone when testing in local time zone
utc = pytz.utc

# # These statment return Day and Time in GMT
# def getToday(): return datetime.strftime(datetime.now(utc), "%Y-%m-%d")
# def getNow(): return datetime.strftime(datetime.now(utc), "%Y-%m-%d %H:%M:%S")

# # These statment return Day and Time in Local Time - Not sure about PST vs PDT
def getToday():
    return datetime.strftime(datetime.now(), "%Y-%m-%d")

def getNow():
    return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")


# Not sure what these statments do
# getToday = lambda: datetime.strftime(date.today(), "%Y-%m-%d")
# print(getToday)
# getNow = lambda: datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
# print(getNow)



# --------------- S3 BUCKET CONFIGUATION ------------------



# --------------- DATABASE CONFIGUATION ------------------
# Connect to MySQL database (API v2)
def connect():
    global RDS_PW
    global RDS_HOST
    global RDS_PORT
    global RDS_USER
    global RDS_DB

    print("Trying to connect to RDS (API v2)...")
    # print("RDS_HOST: ", os.getenv('RDS_HOST'))
    # print("RDS_USER: ", os.getenv('RDS_USER'))
    # print("RDS_PORT: ", os.getenv('RDS_PORT'), type(os.getenv('RDS_PORT')))
    # print("RDS_PW: ", os.getenv('RDS_PW'))
    # print("RDS_DB: ", os.getenv('RDS_DB'))

   
    try:
        conn = pymysql.connect(
            host=os.getenv('RDS_HOST'),
            user=os.getenv('RDS_USER'),
            port=int(os.getenv('RDS_PORT')),
            passwd=os.getenv('RDS_PW'),
            db=os.getenv('RDS_DB'),
            cursorclass=pymysql.cursors.DictCursor,
        )
        print("Successfully connected to RDS. (API v2)")
        return conn
    except:
        print("Could not connect to RDS. (API v2)")
        raise Exception("RDS Connection failed. (API v2)")


# Disconnect from MySQL database (API v2)
def disconnect(conn):
    try:
        conn.close()
        print("Successfully disconnected from MySQL database. (API v2)")
    except:
        print("Could not properly disconnect from MySQL database. (API v2)")
        raise Exception("Failure disconnecting from MySQL database. (API v2)")



# Serialize JSON
def serializeResponse(response):
    try:
        # print("In Serialize JSON")
        for row in response:
            for key in row:
                if type(row[key]) is Decimal:
                    row[key] = float(row[key])
                elif type(row[key]) is date or type(row[key]) is datetime:
                    row[key] = row[key].strftime("%Y-%m-%d")
        # print("In Serialize JSON response", response)
        return response
    except:
        raise Exception("Bad query JSON")


# Execute an SQL command (API v2)
# Set cmd parameter to 'get' or 'post'
# Set conn parameter to connection object
# OPTIONAL: Set skipSerialization to True to skip default JSON response serialization
def execute(sql, cmd, conn, skipSerialization=False):
    response = {}
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cmd == "get":
                result = cur.fetchall()
                response["message"] = "Successfully executed SQL query."
                # Return status code of 280 for successful GET request
                response["code"] = 280
                if not skipSerialization:
                    result = serializeResponse(result)
                response["result"] = result
            elif cmd == "post":
                conn.commit()
                response["message"] = "Successfully committed SQL command."
                # Return status code of 281 for successful POST request
                response["code"] = 281
            else:
                response[
                    "message"
                ] = "Request failed. Unknown or ambiguous instruction given for MySQL command."
                # Return status code of 480 for unknown HTTP method
                response["code"] = 480
    except:
        response["message"] = "Request failed, could not execute MySQL command."
        # Return status code of 490 for unsuccessful HTTP request
        response["code"] = 490
    finally:
        response["sql"] = sql
        return response


# Close RDS connection
def closeRdsConn(cur, conn):
    try:
        cur.close()
        conn.close()
        print("Successfully closed RDS connection.")
    except:
        print("Could not close RDS connection.")


# Runs a select query with the SQL query string and pymysql cursor as arguments
# Returns a list of Python tuples
def runSelectQuery(query, cur):
    try:
        cur.execute(query)
        queriedData = cur.fetchall()
        return queriedData
    except:
        raise Exception("Could not run select query and/or return data")







# -- Stored Procedures start here -------------------------------------------------------------------------------






# -- Queries start here -------------------------------------------------------------------------------

def get_model_from_s3():
    s3_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    s3_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    s3_bucket_name = os.getenv('BUCKET_NAME')
    s3_file_key_word2vec_model = os.getenv('S3_PATH_KEY_WORD2VEC_MODEL')

    # print("s3_access_key: ", os.getenv('AWS_ACCESS_KEY_ID'))
    # print("s3_secret_key: ", os.getenv('AWS_SECRET_ACCESS_KEY'))
    # print("s3_bucket_name: ", os.getenv('BUCKET_NAME'))
    # print("s3_file_key_word2vec_model: ", os.getenv('S3_PATH_KEY_WORD2VEC_MODEL'))

    s3_client = boto3.client('s3', aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key)
    # after s3 connect

    local_model_path = '/tmp/word2vec_movie_ratings_embeddings.model'
    s3_client.download_file(s3_bucket_name, s3_file_key_word2vec_model, local_model_path)
    # model downloaded from s3

    model = Word2Vec.load(local_model_path)
    return model


def get_genres_from_s3():
    s3_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    s3_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    s3_bucket_name = os.getenv('BUCKET_NAME')
    s3_file_key_genres = os.getenv('S3_PATH_KEY_GENRES')

    # print("s3_access_key: ", os.getenv('AWS_ACCESS_KEY_ID'))
    # print("s3_secret_key: ", os.getenv('AWS_SECRET_ACCESS_KEY'))
    # print("s3_bucket_name: ", os.getenv('BUCKET_NAME'))
    # print("s3_file_key_word2vec_model: ", os.getenv('S3_PATH_KEY_GENRES'))

    s3_client = boto3.client('s3', aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key)

    genres_response = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_file_key_genres)

    genres_csv_content = genres_response['Body'].read().decode('utf-8')
    genres_cleaned = pd.read_csv(StringIO(genres_csv_content))
    return genres_cleaned


def generate_user_profile(ratings, model, genres_cleaned):
    user_vector = np.zeros(model.vector_size)
    total_weight = 0.0

    for title, rating in ratings.items():
        movie_id = genres_cleaned[genres_cleaned['title'] == title]['movieId'].values[0]
        if int(movie_id) in model.wv:
            user_vector += model.wv[int(movie_id)] * rating
            total_weight += rating

    if total_weight > 0:
        user_vector /= total_weight

    return user_vector

def recommend_movies(user_vector, model, metadata, top_n=10):
    similarity_scores = []

    for movie_id in model.wv.index_to_key:
        movie_vector = model.wv[movie_id]
        user_norm = np.linalg.norm(user_vector)
        movie_norm = np.linalg.norm(movie_vector)

        if user_norm == 0 or movie_norm == 0:
            similarity = 0
        else:
            similarity = np.dot(user_vector, movie_vector) / (user_norm * movie_norm)

        similarity_scores.append((movie_id, similarity))

    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    top_recommendations = similarity_scores[:top_n]

    recommended_movies = []
    for movie_id, score in top_recommendations:
        movie_data = metadata[metadata['movieId'] == int(movie_id)].iloc[0]
        recommended_movies.append({
            'movieId': movie_id,
            'title': movie_data['title'],
            'genres': movie_data['genres']
        })

    return recommended_movies


def fetch_tmdb_data(movie_title):
    # print("In Fetch TMDB: ", movie_title)
    api_key = os.getenv('TMDB_API_KEY')
    # print("TMDB Key: ", api_key)
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(search_url)
    search_data = response.json()

    if search_data['results']:
        movie_id = search_data['results'][0]['id']
        movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US"

        movie_response = requests.get(movie_url)
        credits_response = requests.get(credits_url)

        movie_data = movie_response.json()
        credits_data = credits_response.json()

        return {
            "tmdb_id": movie_id,
            "poster": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}",
            "overview": movie_data.get('overview', 'Overview not available'),
            "rating": f"{movie_data.get('vote_average', 'Not rated')}/10 ({movie_data.get('vote_count', 0)} votes)",
            "cast": ", ".join([actor['name'] for actor in credits_data.get('cast', [])[:5]])
        }
    return None

class test_api(Resource):
    def get(self):
        print("In Test API GET")
        return {"message": "Hello, World! This is a GET request."}, 200
    
    def post(self):
        print("In Test API POST")
        data = request.get_json()
        print("Data Received: ", data)
        return {"message": "Hello, World! This is a POST request."}, 200

class test_db(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            # Connect to the DataBase
            conn = connect()
            # QUERY 2
            query = """
                SELECT * FROM movies.user_ratings;
                """
            # The query is executed here
            items = execute(query, "get", conn)
            # The return message and result from query execution
            response["message"] = "successful"
            response["result"] = items["result"]
            # Returns code and response
            return response, 200
        except:
            raise BadRequest(
                "Movies Request failed, please try again later.")
        finally:
            disconnect(conn)

class profile_recs(Resource):
    def post(self):
        print("In Profile Recommendations")
        user_input = request.json
        # print("User data received: ", user_input)
        ratings = user_input.get('ratings', {})
        # print("Data stored: ", ratings)

        if not ratings:
            return {"error": "No ratings provided"}, 400

        
        word2vec_model = get_model_from_s3()
        genres_cleaned = get_genres_from_s3()

        # Generate user profile using titles
        user_vector = generate_user_profile(ratings, word2vec_model, genres_cleaned)
        recommendations = recommend_movies(user_vector, word2vec_model, genres_cleaned, top_n=10)

        # Add TMDb data to recommendations
        detailed_recommendations = []
        for recommendation in recommendations:
            # print("Inside for loop", recommendation)
            movie_title = recommendation['title']
            tmdb_info = fetch_tmdb_data(movie_title)

            if tmdb_info:
                recommendation.update(tmdb_info)
            detailed_recommendations.append(recommendation)

        return jsonify({"recommended_movies": detailed_recommendations})


# -- DEFINE APIS -------------------------------------------------------------------------------


# Define API routes


api.add_resource(test_api, '/api/v2/testAPI')
api.add_resource(test_db, '/api/v2/testDB')
api.add_resource(profile_recs, '/api/v2/profile')

# api.add_resource(NewEndpoint, "/api/v2/newEndpoint")
# Run on below IP address and port
# Make sure port number is unused (i.e. don't use numbers 0-1023)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4000)
