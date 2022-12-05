import datetime

import flask
from flask_mongoengine import MongoEngine
import requests
import os
import json
from flask import Flask, request, jsonify, session, flash, redirect, url_for, render_template
from dotenv import load_dotenv
import sys
import datetime

db = MongoEngine()
# connString = os.environ['MONGODB_CONNSTRING']   ### for docker uncomment
app = Flask(__name__)
# app.config["MONGODB_SETTINGS"] = [
#     {
#         "db": "item",
#         # "host": "localhost",               ### comment if docker
#         "host": connString,              ### comment if localhost
#         "port": 27017,
#         "alias": "core_item",
#     },
# ]
app.config['SECRET_KEY'] = 'GDtfDCFYjD'
db.init_app(app)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/home')
def home():
    # user_id = None
    # if session['user']:
    #     user_id = session['user']
    return render_template('home.html')


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/search_itemID', methods=['POST'])
def search_item_id():
    form = request.form
    params = {
        'item_id': form['item_id']
    }
    resp = requests.get("http://service.item:5000/searchItemId", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/search_itemName', methods=['POST'])
def search_item_name():
    form = request.form
    params = {
        'item_name': form['item_name']
    }
    resp = requests.get("http://service.item:5000/searchItemName", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/search_categoryId', methods=['POST'])
def search_item_category():
    form = request.form
    params = {
        'category_id': form['category_id']
    }
    resp = requests.get("http://service.item:5000/searchCategoryId", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]



@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/signUp_User', methods=['POST'])
def signUp_User():
    form = request.form
    params = {
        # 'user_id': session['user'],
        'user_name': form['user_name'],
        'first_name': form['first_name'],
        'last_name': form['last_name'],
        'password': form['password'],
        'date_of_birth': form['date_of_birth'],
        'address': form['address'],
        'email': form['email'],
        'phone_number': form['phone_number'],
        'admin_status': False
    }
    resp = requests.post("http://service.user:5000/signUp",params=params)
    if resp.json()['status_code'] == "201":
        # return resp.json()["detail"]
        flash("Info: Your user_id is "+str(resp.json()["detail"]["user_id"]))
        return redirect(url_for('login'))
    else:
        return resp.json()["detail"]["error"]

@app.route('/createitem')
def createitem():
    return render_template('createitem.html')


@app.route('/create_item', methods=['POST'])
def create_item():
    form = request.form
    params = {
        'item_owner': session['user'],
        'item_name': form['item_name'],
        'item_price': form['item_price'],
        'item_description': form['item_desc'],
        'item_weight': form['item_weight'],
        'item_categories': form['item_categories']
    }
    resp = requests.post("http://service.item:5000/createItem", params=params)
    # print(resp.text)
    # return resp.text
    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/modifyitem')
def modifyitem():
    return render_template('modifyitem.html')


@app.route('/modify_item', methods=['POST'])
def modify_item():
    form = request.form
    params = {
        'session_owner': session['user'],
        'item_id': form['item_id'], 
        'item_name': form['item_name'], 
        'item_price': form['item_price'], 
        'item_description': form['item_desc'],
        'item_weight': form['item_weight']
    }
    # print("IN APP FRONT", file=sys.stderr)
    # print(params, file=sys.stderr)

    resp = requests.post("http://service.item:5000/updateItem", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/delete_item', methods=['POST','GET'])
def delete_item():
    form = request.form
    params = {
        'session_owner': session['user'],
        'item_id': form['itemId']
    }
    resp = requests.delete("http://service.item:5000/deleteItem", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/createcategory')
def createcategory():
    return render_template('createcategory.html')


@app.route('/create_category', methods=['POST'])
def create_category():
    form = request.form
    params = {
        'category_owner': session['user'],
        'category_name': form['category_name'],
        'category_description': form['category_desc']
    }
    resp = requests.post("http://service.item:5000/createCategory", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/modify_category', methods=['POST'])
def modify_category():
    form = request.form
    params = {
        'session_owner': session['user'],
        'category_id': form['category_id'],
        'category_name': form['category_name'],
        'category_description': form['category_desc']
    }
    resp = requests.post("http://service.item:5000/updateCategory", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/modifycategory')
def modifycategory():
    return render_template('modifycategory.html')


@app.route('/delete_category', methods=['POST','GET'])
def delete_category():
    form = request.form
    params = {
        'session_owner': session['user'],
        'category_id': form['catId']
    }
    resp = requests.delete("http://service.item:5000/deleteItem", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/Categorize', methods=['POST'])
def categorize():
    form = request.form
    params = {
        'session_owner': session['user'],
        'item_id': form['itemId'],
        'category_id': form['catId']
    }
    resp = requests.post("http://service.item:5000/categorize", params=params)

    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
        # return redirect(url_for('home'))
    else:
        return resp.json()["detail"]


@app.route('/updateUser')
def updateUser():
    return render_template('updateUser.html')


@app.route('/update_User', methods=['POST'])
def update_User():
    form = request.form
    params = {
        'user_id': session['user'],
        'user_name': form['user_name'],
        'first_name': form['first_name'],
        'last_name': form['last_name'],
        'password': form['password'],
        'date_of_birth': form['date_of_birth'],
        'address': form['address'],
        'email': form['email'],
        'phone_number': form['phone_number']
    }
    resp = requests.post("http://service.user:5000/updateInfo",params=params)
    if resp.json()['status_code'] == "201":
        # return resp.json()["detail"]
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]

@app.route('/delete_User', methods=['POST','GET'])
def delete_User():
    params = {
        'user_id': session['user'],
    }
    resp = requests.delete("http://service.user:5000/deleteUser",params=params)
    if resp.json()['status_code'] == "204":
        # return resp.json()["detail"]
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]

@app.route('/lookup_User', methods=['GET'])
def lookup_User():
    params = {
        'user_id': session['user'],
    }
    resp = requests.get("http://service.user:5000/lookupUser",params=params)
    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/suspend_user', methods=['POST'])
def suspend_user():
    form = request.form
    params = {
        'user_id_admin': session['user'],
        'user_id': form['userId']
    }
    resp = requests.post("http://service.user:5000/suspendUser",params=params)
    if resp.json()['status_code'] == "201":
        # return resp.json()["detail"]
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/unsuspend_user', methods=['POST'])
def unsuspend_user():
    form = request.form
    params = {
        'user_id_admin': session['user'],
        'user_id': form['userId']
    }
    resp = requests.post("http://service.user:5000/unsuspendUser",params=params)
    if resp.json()['status_code'] == "201":
        # return resp.json()["detail"]
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/change_status_admin', methods=['POST'])
def change_status_admin():
    form = request.form
    params = {
        'user_id_admin': session['user'],
        'user_id': form['userId']
    }
    resp = requests.post("http://service.user:5000/changeAdminStatus",params=params)
    if resp.json()['status_code'] == "201":
        # return resp.json()["detail"]
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/receiveSupport')
def receiveSupport():
    return render_template('receiveSupport.html')

@app.route('/receiveCustomerSupport_page', methods=['POST'])
def receiveCustomerSupport_page():
    form = request.form
    resp = requests.get("http://service.user:5000/getEmailId",params={'user_id': session['user']})
    email_id = resp.json()["detail"]["user_data"]
    params = {
        'user_id': session['user'],
        'recipient': email_id,
        'request': {
            'title': form['title'],
            'content': form['content']
        },
        'response': {
            'title': 're: '+form['title'],
            'content': 'You will receive your response in a couple of days. Thank you for your patience.'
        },
        'timestamp': datetime.datetime.now()
    }
    # CHECK THIS POST REQUEST ONCE
    resp = requests.post("http://service.notification:5000/customer_support_response", data=params)
    if resp.json()['status_code'] == "201":
        # return resp.json()["detail"]
        return resp.json()
    else:
        return resp.json()


@app.route('/checkout', methods=['GET','POST'])
def checkout():
    params = {
        'user_id': session['user'],
    }
    resp = requests.post("http://service.user:5000/checkout",params=params)
    return resp.text
    # if resp.json()['status_code'] == "200":
    #     # return resp.json()["detail"]
    #     return resp.json()["detail"]
    # else:
    #     return resp.json()["detail"]


@app.route('/viewCart', methods=['GET'])
def viewCart():
    params = {
        'user_id': session['user'],
    }
    resp = requests.get("http://service.user:5000/viewCart",params=params)
    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/viewWatchlist', methods=['GET'])
def viewWatchlist():
    params = {
        'user_id': session['user'],
    }
    resp = requests.get("http://service.user:5000/viewWatchList",params=params)
    if resp.json()['status_code'] == "200":
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/add_to_Cart', methods=['POST'])
def add_to_Cart():
    form = request.form
    params = {
        'user_id': session['user'],
        'item_id': form['itemId']
    }
    resp = requests.post("http://service.user:5000/addItemToCart",params=params)
    if resp.json()['status_code'] == "201":
        # return resp.json()["detail"]
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/add_to_Watchlist', methods=['POST'])
def add_to_Watchlist():
    form = request.form
    params = {
        'user_id': session['user'],
        'item_id': form['itemId']
    }
    resp = requests.post("http://service.user:5000/addItemToWatchList",params=params)
    if resp.json()['status_code'] == "201":
        # return resp.json()["detail"]
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]



@app.route('/delete_from_Cart', methods=['POST','GET'])
def delete_from_Cart():
    form = request.form
    params = {
        'user_id': session['user'],
        'item_id': form['itemId']
    }
    resp = requests.delete("http://service.user:5000/deleteItemFromCart",params=params)
    # return resp.json()
    if resp.json()['status_code'] == "204":
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/delete_from_Watchlist', methods=['POST','GET'])
def delete_from_Watchlist():
    form = request.form
    params = {
        'user_id': session['user'],
        'item_id': form['itemId']
    }
    resp = requests.delete("http://service.user:5000/deleteItemFromWatchList",params=params)
    # return resp.json()
    if resp.json()['status_code'] == "204":
        return resp.json()["detail"]
    else:
        return resp.json()["detail"]["error"]


@app.route('/loginUser', methods=['POST'])
def loginUser():
    form = request.form
    params = {
        'user_name': form['uname'],
        'password': form['psw']
    }
    resp = requests.post("http://service.user:5000/login",params=params)
    if resp.json()['status_code'] == "201":
        session['user'] = resp.json()["detail"]["user_id"]
        return redirect(url_for('home'))
    else:
        flash('Error: Incorrect credentials')
        return redirect(url_for('login'))

@app.route('/logoutUser', methods=['POST','GET'])
def logoutUser():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    # app.run()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)