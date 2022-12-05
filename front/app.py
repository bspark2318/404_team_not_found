import flask
from flask_mongoengine import MongoEngine
import requests
import os
import json
from flask import Flask, request, jsonify, session, flash, redirect, url_for, render_template
from dotenv import load_dotenv

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

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/createitem')
def createitem():
    return render_template('createitem.html')

@app.route('/modifyitem')
def modifyitem():
    return render_template('modifyitem.html')

@app.route('/createcategory')
def createcategory():
    return render_template('createcategory.html')

@app.route('/modifycategory')
def modifycategory():
    return render_template('modifycategory.html')

@app.route('/updateUser')
def updateUser():
    return render_template('updateUser.html')

@app.route('/receiveSupport')
def receiveSupport():
    return render_template('receiveSupport.html')

@app.route('/loginUser', methods=['POST'])
def loginUser():
    form = request.form
    params = {
        'user_name': form['uname'],
        'password': form['psw']
    }
    resp = requests.post("http://service.user:5000/login",params=params)
    if resp.json()['status_code'] == "200":
        session['user'] = resp.json()["detail"]["user_id"]
        return redirect(url_for('home'))
    else:
        # flash('Incorrect credentials')
        return redirect(url_for('login'))


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
        'phone_number': form['phone_number']
    }
    resp = requests.post("http://service.user:5000/signUp",params=params)
    if resp.json()['status_code'] == "200":
        # return resp.json()["detail"]
        return redirect(url_for('login'))
    else:
        return resp.json()["detail"]



@app.route('/logoutUser', methods=['POST','GET'])
def logoutUser():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/auction')
def auction():
    return render_template('auction.html')

@app.route('/create_listing', methods=['GET', 'POST'])
def create_listing():
    return render_template('create_listing.html')

@app.route('/make_listing', methods=['GET', 'POST'])
def make_listing():
    form = request.form
    params = {
        "item_id": form["item_id"],
        "start_time":form["start_time"],
        "end_time":form["end_time"],
        "endgame":form["endgame"],
        "user_id": session['user'],
        "increment": form["increment"]
    }
    resp = requests.post("http://service.auction:5000/create_listing",params=params)
    if not resp:
        return 'No Item Found'
    if resp.json()['status_code'] == "201":
        return resp.json()
    else:
        return resp.json()["detail"]

@app.route('/get_listing', methods=['GET', 'POST'])
def get_listing():
    return render_template('get_listing.html')

@app.route('/find_listing', methods=['GET', 'POST'])
def find_listing():
    form = request.form
    # params = {
    #     "listing_id": form['listing_id']
    # }
    resp = requests.get("http://service.auction:5000/get_listing",params=form)
    if resp.json()['status_code'] == "200":
        return resp.json()
    else:
        return resp.json()["detail"]

@app.route('/delete_listing', methods=['GET', 'DELETE'])
def delete_listing():
    return render_template('delete_listing.html')

@app.route('/destroy_listing', methods=['GET', 'DELETE'])
def destroy_listing():
    form = request.form
    params = {
        "listing_id": form['listing_id'],
        'user_id': session['user']
    }
    resp = requests.get("http://service.auction:5000/delete_listing",params=params)
    if resp.json()['status_code'] == "200":
        return resp.json()
    else:
        return resp.json()["detail"]


@app.route('/update_listing', methods=['GET', 'POST'])
def update_listing():
    return render_template('update_listing.html')

@app.route('/modify_listing', methods=['GET', 'POST'])
def modify_listing():
    form = request.form
    inputs = ['listing_name', 'description', 'starting_price', 'increment', 'start_time', 'end_time', 'endgame']
    params = {
        'listing_id': form['listing_id'],
        'user_id': session['user'],
    }
    for input in inputs:
        if form[input]:
            params[input] = form[input]
    # params = {
    #     'listing_id': form['listing_id'],
    #     'user_id': session['user'],
    #     'listing_name': form['listing_name'],
    #     'description': form['description'],
    #     'starting_price': form['starting_price'],
    #     'increment': form['increment'],
    #     'start_time': form['start_time'],
    #     'end_time': form['end_time'],
    #     'endgame': form['endgame']
    # }
    resp = requests.post("http://service.auction:5000/update_listing",params=params)
    if resp.json()['status_code'] == "200":
        return resp.json()
    else:
        return resp.json()["detail"]

@app.route('/view_live', methods=['GET', 'POST'])
def view_live():
    return render_template('view_live.html')

@app.route('/see_live', methods=['GET', 'POST'])
def see_live():
    form = request.form
    resp = requests.get("http://service.auction:5000/view_live",params=form)
    if resp.json()['status_code'] == "200":
        return resp.json()
    else:
        return resp.json()["detail"]

@app.route('/stop_auction', methods=['GET', 'POST'])
def stop_auction():
    return render_template('stop_auction.html')

@app.route('/halt_auction', methods=['GET', 'POST'])
def halt_auction():
    form = request.form
    params = {
        'listing_id': form['listing_id'],
        'admin_id': session['user']
    }
    resp = requests.post("http://service.auction:5000/stop_auction",params=params)
    if resp.json()['status_code'] == "200":
        return resp.json()
    else:
        return resp.json()["detail"]

@app.route('/bid', methods=['GET', 'POST'])
def bid():
    return render_template('bid.html')

@app.route('/take_bid', methods=['GET', 'POST'])
def take_bid():
    form = request.form
    params = {
        'listing_id': form['listing_id'],
        'user_id': session['user'],
        'bid': form['bid']
    }
    resp = requests.post("http://service.auction:5000/take_bid",params=params)
    if resp.json()['status_code'] == "200":
        return resp.json()
    else:
        return resp.json()["detail"]

@app.route('/view_metrics', methods=['GET', 'POST'])
def view_metrics():
    return render_template('view_metrics.html')

@app.route('/see_metrics', methods=['GET', 'POST'])
def see_metrics():
    form = request.form
    params = {
        'window_start': form['window_start'],
        'window_end': form['window_end']
    }
    resp = requests.get("http://service.auction:5000/view_metrics",params=params)
    if resp.json()['status_code'] == "200":
        return resp.json()
    else:
        return resp.json()["detail"]

@app.route('/view_bids', methods=['GET', 'POST'])
def view_bids():
    return render_template('view_bids.html')

@app.route('/see_bids', methods=['GET', 'POST'])
def see_bids():
    params = {
        'user_id' : session['user']
    }
    resp = requests.get("http://service.auction:5000/view_bids",params=params)
    return resp.json()


if __name__ == "__main__":
    # app.run()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)