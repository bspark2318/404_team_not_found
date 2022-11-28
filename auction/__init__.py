import os
from dotenv import load_dotenv
from datetime import datetime 
import time 
from flask import Flask, Response, request, make_response, jsonify, json, abort
import requests
from pymongo import MongoClient
from time import ctime, sleep
from apscheduler.schedulers.background import BackgroundScheduler

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
    
    @app.route('/create_listing', methods=["POST"])
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
        if listing:
            del listing['_id']
        response = create_response(200 if listing else 404, field_name='listing details', field_obj=listing)
        return response

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

    @app.route('/update_listing', methods=["POST"])
    def update_listing():
        payload = request.json
        user = payload['user_id']
        listing_id = payload['listing_id']
        details = payload['details']
        listing = service.handle_get_listing(listing_id)

        update = service.handle_update_listing(user, listing, details)
        
        if update == 'success':
            response = create_response(200, 'details', details)
        elif not update:
            response = create_response(404)
        elif update == 'unauthorized':
            response = create_response(400)

        return response


    @app.route('/view_live', methods=["GET"])
    def view_live():
        live_auctions = service.handle_view_live()
        response = create_response(200 if live_auctions else 400, 
                    field_name='Live Auctions', field_obj=live_auctions)

        return response
        
    @app.route('/start_auction', methods=["POST"])
    def start_auction():
        payload = request.json
        listing_id = payload['listing_id']
        user = payload['user_id']
        start, time = service.handle_start_auction(user, listing_id)
        if start == 'success':
            response = create_response(200, 'auction begun', time)
        elif not start:
            response = create_response(404)
        elif start == 'unauthorized':
            response = create_response(400)
        return response


    @app.route('/take_bid', methods=["POST"])
    def take_bid():
        payload = request.json
        bidder = payload['user_id']
        highest_bid = payload['bid']

        listing = service.handle_get_listing(payload['listing_id'])

        if not listing:
            return create_response(404)
        elif listing['status'] != 'live' or highest_bid < listing['current_price'] + listing['increment']:
            return create_response(400)
        else:
            rv = service.handle_bids(bidder, highest_bid, listing)
            if len(rv) == 8:
                _, prior_leader, prior_bid, listing_id, listing_name, seller, highest_bid, bidder = rv

                service.alert_out_bid(prior_leader, prior_bid, highest_bid, listing_id, listing_name)
                service.bid_placed_alert(listing_id, listing_name, prior_bid, highest_bid, bidder, seller)
                return create_response(200, field_name="Bid Placed", field_obj=(listing_name, highest_bid))    
    
            elif len(rv) == 7:
                _, prior_bid, listing_id, listing_name, seller, highest_bid, bidder = rv
                service.bid_placed_alert(listing_id, listing_name, prior_bid, highest_bid, bidder, seller)
                return create_response(200, field_name="Bid Placed", field_obj=(listing_name, highest_bid))

    @app.route('/view_metrics', methods=["GET"])
    def view_metrics():
        payload = request.json
        window_start = payload['window_start']
        window_end = payload['window_end']

        req_auctions = service.handle_view_metrics(window_start, window_end)
        
        return create_response(200 if req_auctions else 404, 
                              field_name=f'{window_start} - {window_end}', 
                              field_obj=req_auctions)


    def pass_winner(listing_id):
        #Triggered when ctime == end_time
        payload = request.json
        listing_id = payload['listing_id']
        listing = service.handle_get_listing(listing_id)
        winner, amount = listing['bid_list'][0]
        payout_details = {
            'winner': winner,
            'cost': amount,
            'seller': listing['seller'],
            'seller_email': listing['seller_email'],
            'item': listing_id
        }

        # Send these to payout details. BumSu, let me know if payments needs more info
        # What is needed for payment
        # {
        # "user_id": "13",
        # "cart_id": "12312312",
        # "total": 46.12,
        # "payment_method": {
        #     "currency": "usd",
        #     "method": "card",
        #     "method_detail": {
        #         "card_number": "4123123212322222",
        #         "security_code": "931",
        #         "holder_name": "BumSu Park",
        #         "billing_address": {
        #             "street_address": "1407 S. State St",
        #             "city": "Chicago",
        #             "state": "IL",
        #             "zipcode": "60605",
        #             "country": "USA"
        #             }
        #         }
        #     }
        # }   

        return payout_details

    
    


    return app

    
        


class AuctionService:
    def __init__(self, conn):
        self.db = conn.listings

    def countdown(self, start, end):
        start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        time = end - start
        time = time.total_seconds()
        while time:
            mins, secs = divmod(time, 60)
            # timer = '{:02d}:{:02d}'.format(mins, secs)
            sleep(1)
            time -= 1
            print(time)
        
        return True


    
    def handle_create_listing(self, item_details):
        
        try:
            res = self.db.find({"listing_id": item_details["item_id"]})
            ## Handle this later. Check if already exists
                        
            listing_obj = {} 
            dest_source = [("listing_id", 'item_id'), ("listing_name", 'item_name'), ("start_time", 'start_time'), ("starting_price", 'price'),
            ("current_price", 'price'), ("increment", 'increment'), ("description", 'description'), 
            ("seller", 'user_id'), ("seller_email", 'owner_email'), ("watchers", 'watchers'), ("end_time", 'end_time'), ("endgame", 'endgame')]
            
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

    
    def handle_update_listing(self, user, listing, details):
        if not listing:
            return None
        elif listing['seller'] != user:
            return 'unauthorized'
        else:
            self.db.update(listing['listing_id'], details)
            return 'success'


    def handle_view_live(self):
        live_auctions = self.db.find({'live': True})
        return live_auctions


    def handle_start_auction(self, user_id, listing_id, details={'status':'live', 'start_time': ctime()}):
        start = self.handle_update_listing(user_id, listing_id, details)
        return (start, ctime())
        # insert method for starting the timer

    def handle_bids(self, bidder, highest_bid, listing):
        prior_leader = None
        prior_bid = None
        listing_name = listing['listing_name']
        listing_id = listing['listing_id']
        seller = listing['seller_email']
        bid = (bidder, highest_bid, ctime())
        if listing['bid_list']:
            prior_leader, prior_bid, _ = listing['bid_list'][0]

        accepted = self.handle_update_listing(listing['seller'], listing, 
                                            {'current_price' : highest_bid, 
                                            'bid_list': listing['bid_list'].insert(0, bid)})
        
        #rv = (accepted, get_email_func(prior_leader), prior_bid, listing_id, listing_name, seller, highest_bid, get_email_func(bidder))

        if prior_leader and bidder != prior_leader:
            rv = (accepted, prior_leader, prior_bid, listing_id, listing_name, seller, highest_bid, bidder)
        else:
            rv = (accepted, prior_bid, listing_id, listing_name, seller, highest_bid, bidder)

        return rv
            
    def handle_view_metrics(self, window_start, window_end):
        req_auctions = self.db.find({'end_time' : {'$gte': window_start, '$lte': window_end}})
        return req_auctions


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
    
    
                
    def alert_out_bid(self, prior_leader, prior_bid, highest_bid, listing_id, listing_name):
        
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
    

    def bid_placed_alert(self, listing_id, listing_name, prior_bid, amount, bidder, seller):
        
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


    def end_game_alert(self, listing_id, listing_name, prior_bid, amount, e_time, bidders, watchers, seller):
        
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
    
