import os
from dotenv import load_dotenv
import time 
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
    connString = os.environ['POSTGRESQL_CONNSTRING']
    # db_user = os.environ['POSTGRES_USER']
    # db_password = os.environ['POSTGRES_PASSWORD']
    ## PSQL
    db_conn = psycopg2.connect(
        host=connString,
        
        database="ebay",
        # user=db_user, 
        # password=db_password
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

    service = PaymentService(db_conn)
    
    def create_response(status, message, user_id=None, total=None, cart_id=None, transaction_id=None, timestamp=None):
        response_payload = {}
        response_payload["user_id"] = user_id if user_id else ""
        response_payload["cart_id"] = cart_id if cart_id else ""
        response_payload["total"] = total if total else 0
        response_payload["transaction_id"] = transaction_id if transaction_id else ""
        response_payload["timestamp"] = timestamp if timestamp else ""
        response_json = {}
        response_json["message"] = message
        response_json["payload"] = response_payload
        response = make_response(jsonify(response_payload))
        response.status_code = 200 if status else 400   
        return response

    # a simple page that says hello
    @app.route('/')
    def hello_world():
        return 'Payment Microservice'
    
    @app.route('/pay_for_cart', methods=["POST"])
    def pay_for_cart():
        payload = request.json
        
        user_id = payload['user_id']
        cart_id = payload['cart_id']
        total = payload['total']
        payment_method = payload['payment_method']
        
        if not service.verify_payment_info(user_id, cart_id, total, payment_method):
            return create_response(False, "Insufficient payment information")
        
        transaction_id = service.handle_pay_for_cart(user_id, cart_id, total, payment_method)
        success = True if transaction_id else False
        message = "Successful payment for total of ${}.".format(total) if success else "Error encountered while processing payment for cart ID {}.".format(cart_id)
        
        response = create_response(success, message, user_id=user_id, cart_id=cart_id, transaction_id=transaction_id, timestamp=None)
        return response
    
    @app.route('/view_transaction', methods=["POST"])
    def view_transaction():
        payload = request.json
        
        user_id = payload['user_id']
        transaction_id = payload['transaction_id']
        
        transaction_detail = service.handle_view_transaction(user_id, transaction_id)
        success = True if transaction_detail else False
        message = "Transaction with ID {} successfully retrieved.".format(transaction_id) if success else "Error encountered while retrieving transaction detail."
        
        response = create_response(success, message, user_id=user_id, cart_id=transaction_detail['cart_id'], transaction_id=transaction_id, timestamp=transaction_detail['timestamp'])
        return response
    
    return app

class PaymentService:
    def __init__(self, conn):
        self.db = conn
        
    def verify_payment_info(self, user_id, cart_id, total, payment_method):
        if not user_id or not cart_id or not total:
            return False 
        
        if not payment_method:
            return False 
        
        first_check_list = ["method", "method_detail"]
        second_check_list = ["security_code", "holder_name", "billing_address"]
        for check in first_check_list:
            if check not in payment_method or not payment_method[check]:
                return False 
        for check in second_check_list:
            if check not in payment_method["method_detail"] or not payment_method["method_detail"][check]:
                return False
        if "zipcode" not in payment_method["method_detail"]["billing_address"]:
            return False 
        
        return True
    
    def enable_third_party_payment(self):
        return True
    
    def handle_pay_for_cart(self, user_id, cart_id, total, payment_method):
        try:
            ## Possibly third-party processing of payment
            assert(self.enable_third_party_payment(), "Error encountered while connecting with the payment processing third party.")
            ## Handle database transaction
            method_type = payment_method["method"]
            insert_query = """
            INSERT INTO transactions (user_id, cart_id, total, method)
            VALUES ({}, {}, {}, \'{}\');
            """.format(user_id, cart_id, total, method_type)
            cursor = self.db.cursor() 
            cursor.execute(insert_query)
            self.db.commit()
            select_query = """
            SELECT transaction_id 
            FROM transactions 
            ORDER BY transaction_time DESC
            LIMIT 1;
            """
            cursor.execute(select_query)
            transaction_id = cursor.fetchone()[0]
            cursor.close()
            return transaction_id
            

        except Exception as e:
            print("Error: Failure to execute \"handle_pay_for_cart\" due to {}".format(e))
            return None 

    def handle_view_transaction(self, user_id, transaction_id):
        try:
            ## Possibly third-party processing of payment
            cursor = self.db.cursor() 
            select_query = """
            SELECT * 
            FROM transactions 
            WHERE user_id = \'{}\' AND transaction_id = {}
            """.format(user_id, transaction_id)
            cursor.execute(select_query)
            result = cursor.fetchone()
            cursor.close()
            transaction_detail = {
                "transaction_id": result[0],
                "user_id": result[1],
                "cart_id": result[2],
                "total": result[3],
                "method": result[4],
                "timestamp": result[5]
            }
            return transaction_detail

        except Exception as e:
            print("Error: Failure to execute \"handle_view_transaction\" due to {}".format(e))
            return None 