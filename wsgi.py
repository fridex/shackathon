import os
import connexion
from flask import Flask, request, send_from_directory

app = connexion.App(__name__)
application = app.app
app.add_api('swagger.yaml')


@app.route('/')
def index():
    print('index')
    return send_from_directory('hackathon-frontend', 'index.html')


@app.route('/<path:path>')
def assets(path):
    print(path)
    return send_from_directory(os.path.join('hackathon-frontend', 'assets'), path)
