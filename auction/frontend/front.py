import flask
from flask_mongoengine import MongoEngine
import requests
import os
import json
from flask import Flask, request, jsonify, session, flash, redirect, url_for, render_template
from dotenv import load_dotenv

db = MongoEngine()
app = Flask(__name__)

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


@app.route('/create_listing')
def create_listing():
    return render_template('create_listing.html')

@app.route('/make_listing')
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
    if resp.json()['status_code'] == "200":
        return resp.json()
    else:
        return resp.json()["detail"]

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

@app.route('/view_bids', methods=['GET'])
def view_bids():
    params = {
        'user_id' : session['user']
    }
    resp = requests.get("http://service.auction:5000/view_bids",params=params)
    return resp.json()


