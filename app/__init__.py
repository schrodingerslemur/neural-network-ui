# import os

# from flask import Flask, jsonify, request
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# def create_app():
#     app = Flask(__name__)
#     app.config['SECRET_KEY'] = 'dfh3rb3nb 2i3br93c dei930bfwe0f'

#     db_password = os.getenv("DB_PASSWORD")
#     uri = f"mongodb+srv://bhendrat:{db_password}@schrodingercluster.m7vra.mongodb.net/?retryWrites=true&w=majority&appName=SchrodingerCluster"
#     # Create a new client and connect to the server
#     client = MongoClient(uri, server_api=ServerApi('1'))
#     # Send a ping to confirm a successful connection
#     try:
#         client.admin.command('ping')
#         print("Pinged your deployment. You successfully connected to MongoDB!")
#     except Exception as e:
#         print("Failed to connect to MongoDB: ", e)

#     from .routes import routes # JSON routes back and forth
#     app.register_blueprint(routes, url_prefix='/')

#     from .models import models # JSON to database and vice-versa
