from flask import Flask, Blueprint, request, Response, jsonify, json
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_socketio import SocketIO
import redis
import os
import sys

#app configuration
class MyApp(Flask):
    def __init__(self, import_name):
        super(MyApp, self).__init__(import_name)
        self.secret_key = os.urandom(24)
        # self.config['MYSQL_HOST'] = 'localhost'
        # self.config['MYSQL_USER'] = 'root'
        # self.config['MYSQL_PASSWORD'] = 'Djj@19950420'
        self.config['MYSQL_HOST'] = 'hr-portal.cnqqzdrj2hp3.us-west-1.rds.amazonaws.com'
        self.config['MYSQL_USER'] = 'admin'
        self.config['MYSQL_PASSWORD'] = '6VzyMVtDyA'
        self.config['MYSQL_DB'] = 'employees'
        # Configure Redis for storing the session data on the server-side
        # self.redis_client = FlaskRedis(self)
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.mysql = MySQL(self)
        CORS(self)


app = MyApp(__name__)