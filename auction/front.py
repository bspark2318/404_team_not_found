import os
import sys
import time
import requests
import json
from dotenv  import load_dotenv
from flask import Flask, Response, request, make_response, jsonify, json, abort
from pymongo import MongoClient
from flask import render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    
    load_dotenv()
    connString = os.environ['MONGODB_CONNSTRING']
    
    ## Change this to the docker host//IP ADDRESSS
    client = MongoClient(connString, 27017)
    db_conn = client.core

    scheduler = BackgroundScheduler(jobstores={'mongo': MongoDBJobStore(client=client)}, executors={'default': ThreadPoolExecutor(20)}, job_defaults={'coalesce': False, 'max_instances': 3},timezone='America/Chicago')
    scheduler.start()


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    
    except OSError:
        pass



    @app.route('/create_listing')
    def create_listing():
        return render_template('create_listing.html')

    @app.route('/get_listing')
    def get_listing():
        return render_template('get_listing.html')

    @app.route('/delete_listing')
    def delete_listing():
        return render_template('delete_listing.html')

    @app.route('/update_listing')
    def update_listing():
        return render_template('update_listing.html')

    @app.route('/view_live')
    def view_live():
        return render_template('view_live.html')

    @app.route('/stop_auction')
    def stop_auction():
        return render_template('stop_auction.html')

    @app.route('/bid', methods=['POST'])
    def bid():
        return render_template('bid.html')

    @app.route('/view_metrics', methods=['POST'])
    def view_metrics():
        return render_template('view_metrics.html')

