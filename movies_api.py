# To run program:  python3 movies_api.py

# README:  if conn error make sure password is set properly in RDS PASSWORD section
# README:  Debug Mode may need to be set to False when deploying live (although it seems to be working through Zappa)
# README:  if there are errors, make sure you have all requirements are loaded

print("In Movies")

import os
# import boto3
# import json
# import sys
# import json
import pytz
# import pymysql
# import requests
# import stripe
# from fuzzywuzzy import fuzz

# from dotenv import load_dotenv
from datetime import date, datetime
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
# from flask_mail import Mail, Message
# from werkzeug.exceptions import BadRequest, InternalServerError
# from decimal import Decimal
# from hashlib import sha512

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




# -- Stored Procedures start here -------------------------------------------------------------------------------






# -- Queries start here -------------------------------------------------------------------------------



class test_api(Resource):
    def get(self):
        print("In Test API GET")
        return {"message": "Hello, World! This is a GET request."}, 200
    
    def post(self):
        print("In Test API POST")
        data = request.get_json()
        print("Data Received: ", data)
        return {"message": "Hello, World! This is a POST request."}, 200




# -- DEFINE APIS -------------------------------------------------------------------------------


# Define API routes


api.add_resource(test_api, '/api/v2/testAPI')

# api.add_resource(NewEndpoint, "/api/v2/newEndpoint")
# Run on below IP address and port
# Make sure port number is unused (i.e. don't use numbers 0-1023)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4000)
