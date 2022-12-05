import sys
import os
from dotenv import load_dotenv
import time 
import json
from flask import Flask, request, make_response, jsonify
import requests
from pymongo import MongoClient

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
    connString = os.environ['MONGODB_CONNSTRING']
    
    
    client = MongoClient(connString, 27017)
    
    db_conn = client.ebay

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
    
    def create_response(status, recipient, noti_type):
        response_payload = {}
        response_payload["notification_status"] = status
        response_payload["recipient"] = recipient
        response_payload["notification_type"] = "{}".format(noti_type)
        response_json = {}
        response_json["message"] = "\"{}\" successful".format(noti_type) if status else "\"{}\" failed".format(noti_type)
        response_json["payload"] = response_payload
        response = make_response(jsonify(response_payload))
        response.status_code = 201 if status else 400   
        return response

    # a simple page that says hello
    @app.route('/')
    def hello_world():
        return 'Notification Microservice'
    
    @app.route('/alert_watchlist', methods=["POST"])
    def watchlist_alert():
        payload = request.json
        
        item_id = payload['item_id']
        auction_id = payload['auction_id']
        timestamp = payload['timestamp']
        recipient = payload['recipient']
        
        success = service.handle_alert_watchlist(item_id, auction_id, timestamp, recipient)
        
        response = create_response(success, recipient, "watchlist_alert")
        return response
    
    @app.route('/alert_seller_bid', methods=["POST"])
    def seller_bid_alert():
        payload = request.json
        
        auction_title = payload['auction_title']
        auction_id = payload['auction_id']
        timestamp = payload['timestamp']
        recipient = payload['recipient']
        new_bid = payload['new_bid']
        old_bid = payload['old_bid']
                
        success = service.handle_seller_bid_alert(auction_title, auction_id, new_bid, old_bid, recipient)
        response = create_response(success, recipient, "seller_bid_alert")    
        print("Making a request items ")
        params = {
            "item_name": "hello",
            "item_description": "desc",
            "item_price": 123,
            "item_weight": 122,
            "item_categories": [1, 3, 5]   
        }
        
        return response
    
    @app.route('/alert_buyer_outbid', methods=["POST"])
    def buyer_outbid_alert():
        payload = request.json
        
        auction_title = payload['auction_title']
        auction_id = payload['auction_id']
        timestamp = payload['timestamp']
        recipient = payload['recipient']
        new_bid = payload['new_bid']
        old_bid = payload['old_bid']
                
        success = service.handle_buyer_outbid_alert(auction_title, auction_id, new_bid, old_bid, recipient)
        response = create_response(success, recipient, "buyer_outbid_alert")    
        return response
    
    @app.route('/alert_countdown', methods=["POST"])
    def countdown_alert():
        payload = request.json
        
        auction_title = payload['auction_title']
        auction_id = payload['auction_id']
        timestamp = payload['timestamp']
        recipient = payload['recipient']
        current_bid = payload['current_bid']
        end_time = payload['end_time']
                
        success = service.handle_countdown_alert(auction_title, auction_id, current_bid, end_time, recipient)
        
        response = create_response(success, recipient, "countdown_alert")    
        return response
    
    @app.route('/customer_support_response', methods=["POST"])
    def customer_support_response():
        payload = request.json
        payload = json.loads(payload)
        user_id = int(payload['user_id'])
        request_body = payload['request']
        response_body = payload['response']
        timestamp = payload['timestamp']
        recipient = payload['recipient']
                
        success = service.handle_customer_support_response(user_id, request_body, response_body, recipient)
        response = create_response(success, recipient, "customer_support_response")    
        return response
    
    return app

class NotificationService:
    def __init__(self, conn):
        self.db = conn.notification
        self.mailgun_key = os.environ['MAILGUN_API_KEY']
        self.mailgun_domain = os.environ['MAILGUN_DOMAIN']
        print(self.mailgun_domain, flush=True)
        print(self.mailgun_key, flush=True)
        
        
    def send_email(self, recipient, title, content):
        
        resp = requests.post(
            "https://api.mailgun.net/v3/{}/messages".format(self.mailgun_domain),
		    auth=("api", self.mailgun_key),
		    data={"from": "404 Team Not Found Market <mailgun@{}>".format(self.mailgun_domain),
			"to": recipient,
			"subject": title,
			"text": content})
        return resp
    
    def handle_alert_watchlist(self, item_id, auction_id, timestamp, recipient):
        try:
            ## Handle sending the email
            noti_title = "Watchlist Alert for Auction ID {}".format(auction_id)
            noti_message = "Item on your watchlist with ID {} has is now available through an auction! Search for auction ID {}! \n\nSincerely,\n404 Team Not Found".format(item_id, auction_id)
            noti_timestamp = time.time()
            response = self.send_email(recipient, noti_title, noti_message)
            print("Watchlist Alert Notification Status: ", response, file=sys.stderr)
            
            ## Handle database transaction
            records = []
            for user_email in recipient:
                storage_obj = {}
                storage_obj["alert_type"] = "watchlist_alert"
                storage_obj["user_email"] = user_email
                storage_obj["item_id"] = item_id
                storage_obj["auction_id"] = auction_id
                storage_obj["timestamp"] = noti_timestamp
                records.append(storage_obj)
            
            self.db.insert_many(records)
        except:
            print("Error: Failure to execute \"handle_alert_watchlist\"")
            return False
        
        return True
    
    def handle_buyer_outbid_alert(self, auction_title, auction_id, new_bid, old_bid, recipient):
        try:
            ## Handle sending the email
            noti_title = "Buyer Outbid Alert for Auction \"{}\"".format(auction_title)
            noti_message = "You have been outbid for the auction with ID {}:\nNew Bid: {}\nOld Bid:{}\n\nSincerely,\n404 Team Not Found".format(auction_id, new_bid, old_bid)
            noti_timestamp = time.time()
            response = self.send_email(recipient, noti_title, noti_message)
            print("Buyer Outbid Alert Notification Status: ", response)
            
            ## Handle database transaction
            records = []
            for user_email in recipient:
                storage_obj = {}
                storage_obj["alert_type"] = "buyer_outbid_alert"
                storage_obj["user_email"] = user_email
                storage_obj["auction_id"] = auction_id
                storage_obj["new_bid"] = new_bid
                storage_obj["timestamp"] = noti_timestamp
                records.append(storage_obj)
            
            self.db.insert_many(records)
        except:
            print("Error: Failure to execute \"handle_buyer_outbid_alert\"")
            return False
        
        return True
    
    def handle_seller_bid_alert(self, auction_title, auction_id, new_bid, old_bid, recipient):
        try:
            ## Handle sending the email
            noti_title = "Seller Bid Alert for Auction \"{}\"".format(auction_title)
            noti_message = "Your auction with ID {} has received a new bid.\n\nNew Bid: {}\nOld Bid:{}\n\nSincerely,\n404 Team Not Found".format(auction_id, new_bid, old_bid)
            noti_timestamp = time.time()
            response = self.send_email(recipient, noti_title, noti_message)
            print("Seller Bid Alert Notification Status: ", response, file=sys.stderr)
            
            ## Handle database transaction
            records = []
            for user_email in recipient:
                storage_obj = {}
                storage_obj["alert_type"] = "seller_bid_alert"
                storage_obj["user_email"] = user_email
                storage_obj["auction_id"] = auction_id
                storage_obj["new_bid"] = new_bid
                storage_obj["timestamp"] = noti_timestamp
                records.append(storage_obj)
            
            self.db.insert_many(records)
            
            
        except Exception as e:
            print("Error: Failure to execute \"handle_seller_bid_alert\"", file=sys.stderr)
            print(e, file=sys.stderr)
            
            return False
        
        return True
    
    def handle_countdown_alert(self, auction_title, auction_id, current_bid, end_time, recipient):
        try:
            ## Handle sending the email
            noti_title = "Countdown Alert for Auction \"{}\"".format(auction_title)
            noti_message = "Auction with ID {} is expiring in 10 minutes!\n\nEnd Time: {}\nCurrent Highest Bid:{}\n\nSincerely,\n404 Team Not Found".format(auction_id, end_time, current_bid)
            noti_timestamp = time.time()
            response = self.send_email(recipient, noti_title, noti_message)
            print("Countdown Alert Notification Status: ", response)
            
            ## Handle database transaction
            records = []
            for user_email in recipient:
                storage_obj = {}
                storage_obj["alert_type"] = "countdown_alert"
                storage_obj["user_email"] = user_email
                storage_obj["auction_id"] = auction_id
                storage_obj["timestamp"] = noti_timestamp
                records.append(storage_obj)
            
            self.db.insert_many(records)
        except:
            print("Error: Failure to execute \"handle_countdown_alert\"")
            return False
        
        return True
    
    def handle_customer_support_response(self, user_id, request_body, response_body, recipient):    
        try:
            ## Handle sending the email
            
            request_title = request_body["title"]
            request_content = request_body["content"]
            response_content = response_body["content"]
            noti_title = "Responding to the request \"{}\"".format(request_title)
            noti_message = "Here is the response to your question:\n{}\n\nResponse:\n{}\n\nSincerely,\n404 Team Not Found".format(request_content, response_content)
            noti_timestamp = time.time()
            response = self.send_email(recipient, noti_title, noti_message)
            print("Customer Support Response Notification Status: ", response)
            
            ## Handle database transaction
            records = []
            for user_email in recipient:
                storage_obj = {}
                storage_obj["alert_type"] = "customer_support_response"
                storage_obj["user_email"] = user_email
                storage_obj["request"] = request_body
                storage_obj["response"] = response_body
                storage_obj["timestamp"] = noti_timestamp
                records.append(storage_obj)
            self.db.insert_many(records)
        except:
            print("Error: Failure to execute \"handle_customer_support_response\"")
            return False
        
        return True
        
    

