import os
from dotenv import load_dotenv
from flask import Flask, Response, request, make_response, jsonify, json, abort
import requests
import psycopg2


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    #
    ## Make the database right here
    
    load_dotenv()


    db_conn = psycopg2.connect(
        host="localhost",
        database="flask_db",
        # user=os.environ[''],
        # password=os.environ['']
    )

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

    service = NotificationService(db_conn)

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Notification Microservice'
    
    
    


    @app.route('/alert_watchlist', methods=["POST"])
    def watchlist_alert():
        payload = request.json
        
        item_id = payload['item_id']
        auction_id = payload['auction_id']
        timestamp = payload['timestamp']
        recipient = payload['recipient']
        
        
        resp1 = service.send_email(["ebspark1994@uchicago.edu", "bspark2318@gmail.com"], "hell", "yoyo")
        resp2 =  service.send_email(["bspark2318@gmail.com"], "hell", "yoyo")
        
        print("a", resp1)
        print("b", resp2)
        
        
        return_payload = {}
        return return_payload
    
    return app
        

class NotificationService:
    
    def __init__(self, conn):
        self.db = conn 
        self.mailgun_key = os.environ.get("MAILGUN_API_KEY")
        print(self.mailgun_key)
        
        
    def send_email(self, recipient, title, content):
        
        resp = requests.post(
            "https://api.mailgun.net/v3/sandbox275e03f26ba84051bc89593d48ad8b9e.mailgun.org/messages",
		    auth=("api", self.mailgun_key),
		    data={"from": "EBay-Like Market <mailgun@sandbox275e03f26ba84051bc89593d48ad8b9e.mailgun.org>",
			"to": recipient,
			"subject": title,
			"text": content})
        
        return resp
    

    
        
    

