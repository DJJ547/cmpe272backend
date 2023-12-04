from flask import Flask, Blueprint, request, Response, jsonify, json
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_socketio import SocketIO
import redis
import os
import sys
from dotenv import load_dotenv

load_dotenv()

#app configuration
class MyApp(Flask):
    def __init__(self, import_name):
        super(MyApp, self).__init__(import_name)
        self.secret_key = os.urandom(24)
        # self.config['MYSQL_HOST'] = 'localhost'
        # self.config['MYSQL_USER'] = 'root'
        # self.config['MYSQL_PASSWORD'] = 'Djj@19950420'
        self.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
        self.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
        self.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
        self.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
        # Configure Redis for storing the session data on the server-side
        # self.redis_client = FlaskRedis(self)
        self.redis = redis.Redis(host=os.environ.get('REDIS_HOST'), port=6379, decode_responses=True)
        self.mysql = MySQL(self)
        CORS(self, origins=os.environ.get('FRONTEND_URL'))


app = MyApp(__name__)