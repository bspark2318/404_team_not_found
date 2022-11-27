import os
from dotenv import load_dotenv
from datetime import datetime 
import time 
from flask import Flask, Response, request, make_response, jsonify, json, abort
import requests
from pymongo import MongoClient

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    #
    ## Make the database right here
    
    load_dotenv()
    
    ## Change this to the docker host//IP ADDRESSS
    client = MongoClient("localhost", 27017)
    db_conn = client.core

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

    service = AuctionService(db_conn)
    
    def create_response(response_code, field_name=None, field_obj=None):
        response_json = {}
        response = make_response()
        if field_name and field_obj:
            response_json[field_name] = field_obj
            ## Fix this for 
            response = make_response(jsonify(response_json))
        response.status_code = response_code
        return response

    # a simple page that says hello
    @app.route('/')
    def hello_world():
        return 'Auction Microservice'
    
    @app.route('/create_listing', methods=["PUT"])
    def create_listing():
        payload = request.json
        item_details = payload['item_details']
        
        listing = service.handle_create_listing(item_details)
        if listing:
            del listing['_id']
        
        response = create_response( 201 if listing else 400 , field_name="listing_details", field_obj=listing)
        return response
    

    @app.route('/get_listing', methods=["GET"])
    def get_listing():
        payload = request.json
        listing_id = payload['listing_id']
        listing = service.handle_get_listing(listing_id)
        response = create_response(200 if listing else 404, field_name='listing details', field_obj=listing)

    @app.route('/delete_listing', methods=["DELETE"])
    def delete_listing():
        payload = request.json
        listing_id = payload['listing_id']
        user = payload['user_id']
        deletion = service.handle_delete_listing(listing_id, user)
        if deletion == 'success':
            response = create_response(200)
        elif not deletion:
            response = create_response(404)
        elif deletion == 'unauthorized':
            response = create_response(400)
        
        return response

    @app.route('/update_listing', methods=["DELETE"])
    def update_listing():
        payload = request.json


    
    def alert_out_bid(prior_leader, prior_bid, highest_bid, listing_id, listing_name):
        
        post_body = {}
        post_body["auction_title"] = listing_name
        post_body["new_bid"] = highest_bid
        post_body["old_bid"] = prior_bid
        post_body["auction_id"] = listing_id
        dt = datetime.now()
        post_body["timestamp"] = datetime.timestamp(dt)
        post_body["recipient"] = [prior_leader]
        
        ## Do we need to implement this through async pub sub?
        ## Will need to change the URL later on
        resp = requests.post(
            "http://localhost:5000/alert_buyer_outbid",
            json=post_body
        )
        
        print("alert out bid result: ", resp)
        
        return True 
    
    def bid_placed_alert(listing_id, listing_name, prior_bid, amount, bidder, seller):
        
        post_body = {}
        post_body["auction_title"] = listing_name
        post_body["auction_id"] = listing_id
        post_body["new_bid"] = amount
        post_body["old_bid"] = prior_bid
        dt = datetime.now()
        post_body["timestamp"] = datetime.timestamp(dt)
        post_body["recipient"] = [seller]
        
        ## Do we need to implement this through async pub sub?
        ## Will need to change the URL later on
        resp = requests.post(
            "http://localhost:5000/alert_seller_bid",
            json=post_body
        )
        
        print("alert seller bid result: ", resp)
        
        return True 

    def end_game_alert(listing_id, listing_name, prior_bid, amount, e_time, bidders, watchers, seller):
        
        post_body = {}
        post_body["auction_title"] = listing_name
        post_body["auction_id"] = listing_id
        post_body["current_bid"] = amount
        post_body["old_bid"] = prior_bid
        dt = datetime.now()
        post_body["timestamp"] = datetime.timestamp(dt)
        post_body["end_time"] = e_time
        post_body["recipient"] = watchers
        
        ## Do we need to implement this through async pub sub?
        ## Will need to change the URL later on
        resp = requests.post(
            "http://localhost:5000/alert_countdown",
            json=post_body
        )
        print("alert End Game: ", resp)
        
        return True 
    


    return app

    
        


class AuctionService:
    def __init__(self, conn):
        self.db = conn.listings
    
    def handle_create_listing(self, item_details):
        
        try:
            res = self.db.find({"listing_id": item_details["item_id"]})
            ## Handle this later. Check if already exists
                        
            listing_obj = {} 
            dest_source = [("listing_id", 'item_id'), ("listing_name", 'item_name'), ("start_time", 'start_time'), ("starting_price", 'price'),
            ("current_price", 'price'), ("increment", 'increment'), ("description", 'description'), 
            ("seller", 'user_id'), ("watchers", 'watchers'), ("end_time", 'end_time'), ("endgame", 'endgame')]
            
            for dest, source in dest_source:
                listing_obj[dest] = item_details[source]
            
            self.db.insert_one(listing_obj)
            print("Successful execution")
            return listing_obj
            
        except Exception as e:
            print("Error: Failure to execute \"handle_create_listing\" due to {}".format(e))
            return None


    def handle_get_listing(self, listing_id):
        '''
        '''
        return self.db.find_one({'listing_id': listing_id})
        

    def handle_delete_listing(self, listing_id, user):
        listing = self.handle_get_listing(listing_id)
        if not listing:
            return None
        elif listing['seller'] != user:
            return 'unauthorized'
        else:
            self.db.delete_one({'listing_id': listing_id})
            return 'success'

    
    def handle_update_listing():
        pass


    def handle_buyer_outbid_alert(self, auction_title, auction_id, new_bid, old_bid, recipient):
        try:
            ## Handle sending the email
            noti_title = "Buyer Outbid Alert for Auction \"{}\"".format(auction_title)
            noti_message = "You have been outbid for the auction with ID {}:\nNew Bid: {}\nOld Bid:{}".format(auction_id, new_bid, old_bid)
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
            noti_message = "Your auction with ID {} has received a new bid.\nNew Bid: {}\nOld Bid:{}".format(auction_id, new_bid, old_bid)
            noti_timestamp = time.time()
            response = self.send_email(recipient, noti_title, noti_message)
            print("Seller Bid Alert Notification Status: ", response)
            
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
        except:
            print("Error: Failure to execute \"handle_seller_bid_alert\"")
            return False
        
        return True
    
    def handle_countdown_alert(self, auction_title, auction_id, current_bid, end_time, recipient):
        try:
            ## Handle sending the email
            noti_title = "Countdown Alert for Auction \"{}\"".format(auction_title)
            noti_message = "Auction with ID {} is expiring in 10 minutes!\nEnd Time: {}\nCurrent Highest Bid:{}".format(auction_id, end_time, current_bid)
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
            noti_message = "Here is the response to your question:\n{}\n\nResponse:\n{}".format(request_content, response_content)
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
        
    
