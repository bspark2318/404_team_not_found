import flask
from flask_mongoengine import MongoEngine
import sys
import requests
import os
import json
from flask import Flask, request, jsonify, make_response, Response
from dotenv import load_dotenv
import datetime
import random
import math


db = MongoEngine()
connstring = os.environ['MONGODB_CONNSTRING']
app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = [
    {
        "db": "user",
        # "host": "localhost",
        "host": connstring,
        "port": 27017,
        "alias": "core",
    }
]
db.init_app(app)

@app.route('/')
def hello_world():
    return 'User Microservice'

@app.route('/lookupUser', methods=['GET'])
def lookupUser():
    user_id_input = request.args.get('user_id')
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })
    user = User_class.objects(user_id=user_id_input)[0]
    if not user:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User does not exist!"
            }
        })
    else:
        return jsonify({
            "status_code": "200",
            "detail": {
                "user_data" : user.to_json()
            }
        })



@app.route('/getEmailId', methods=['GET'])
def getEmailId():
    user_id_input = request.args.get('user_id')
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })
    user = User_class.objects(user_id=user_id_input)[0]
    if not user:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User does not exist!"
            }
        })
    else:
        return jsonify({
            "status_code": "200",
            "detail": {
                "user_data" : user.email
            }
        })


@app.route('/getAdminStatus', methods=['GET'])
def getAdminStatus():
    user_id_input = request.args.get('user_id')
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })
    user = User_class.objects(user_id=user_id_input)[0]
    if not user:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User does not exist!"
            }
        })
    else:
        return jsonify({
            "status_code": "200",
            "detail": {
                "user_data" : user.adminStatus
            }
        })


@app.route('/signUp', methods=['POST'])
def signUp():
    user_id = len(User_class.objects().all())+1
    user_name = request.args.get('user_name')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    password = request.args.get('password')
    print(request.args.get('date_of_birth'))
    print(type(request.args.get('date_of_birth')))
    date_of_birth = list(map(int, request.args.get('date_of_birth').split("-")))
    date_obj = datetime.datetime(int(date_of_birth[0]), int(date_of_birth[1]), int(date_of_birth[2]))

    phone_number = request.args.get('phone_number')
    if not User_class().isint(phone_number) or len(phone_number) != 10:
        # print('Phone number is not a valid number!')
        return jsonify({
            "status_code": "403",
            "detail": {
                "error" : "Phone number is not a valid number!"
            }
        })
    phone_number = int(phone_number)

    address = request.args.get('address')
    email = request.args.get('email')
    admin_status = request.args.get('admin_status')

    u = User_class()
    u.user_id = user_id
    u.user_name = user_name
    u.first_name = first_name
    u.last_name = last_name
    u.password = password
    u.date_of_birth = date_obj
    u.phone_number = phone_number
    u.address = address
    u.email = email
    u.suspendStatus = False
    if admin_status == "True":
        u.adminStatus = True
    else:
        u.adminStatus = False
    u.cart = []
    u.watchlist = []
    u.save()
    return jsonify({
        "status_code": "201",
        "detail": {
            "user_id" : u.user_id
        }
    })


@app.route('/suspendUser', methods=['POST'])
def suspendUser():  # check if the user has to be suspended only for a time period
    user_id_input = request.args.get('user_id')
    user_id_admin = request.args.get('user_id_admin')
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_input) + " does not exist to suspend the user!"
            }
        })
    if not User_class.objects(user_id=user_id_admin):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_admin) + " does not exist!"
            }
        })
    user_admin = User_class.objects(user_id=user_id_admin)[0]
    if not user_admin:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_admin) + " does not exist!"
            }
        })
    else:
        if user_admin.adminStatus:
            if not User_class.objects(user_id=user_id_input)[0].suspendStatus:
                User_class.objects(user_id=user_id_input).update_one(set__suspendStatus=True)
                print("User suspended!")
                return jsonify({
                    "status_code": "201",
                    "detail": "User ID " + str(user_id_input) + " suspended!"
                })
            else:
                print("User has been suspended already!")
                return jsonify({
                    "status_code": "404",
                    "detail": "User ID " + str(user_id_input) + " has been suspended already!"
                })
        else:
            return jsonify({
                "status_code": "403",
                "detail": "User ID " + str(user_id_admin) + " is not authorized to suspend another user!"
            })


@app.route('/unsuspendUser', methods=['POST'])
def unsuspendUser():  # check if the user has to be suspended only for a time period
    user_id_input = request.args.get('user_id')
    user_id_admin = request.args.get('user_id_admin')
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_input) + " does not exist to unsuspend the user!"
            }
        })
    if not User_class.objects(user_id=user_id_admin):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_admin) + " does not exist!"
            }
        })
    user_admin = User_class.objects(user_id=user_id_admin)[0]
    if not user_admin:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_admin) + " does not exist!"
            }
        })
    else:
        if user_admin.adminStatus:
            if User_class.objects(user_id=user_id_input)[0].suspendStatus:
                User_class.objects(user_id=user_id_input).update_one(set__suspendStatus=False)
                print("User unsuspended!")
                return jsonify({
                    "status_code": "201",
                    "detail": "User ID " + str(user_id_input) + " unsuspended!"
                })
            else:
                print("User has been unsuspended already!")
                return jsonify({
                    "status_code": "404",
                    "detail": "User ID " + str(user_id_input) + " has been unsuspended already!"
                })
        else:
            return jsonify({
                "status_code": "403",
                "detail": "User ID " + str(user_id_admin) + " is not authorized to unsuspend another user!"
            })

@app.route('/changeAdminStatus', methods = ['POST'])
def changeAdminStatus():
    user_id_input = request.args.get('user_id')
    user_id_admin = request.args.get('user_id_admin')
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_input) + " does not exist to change his status to an Admin!"
            }
        })
    if not User_class.objects(user_id=user_id_admin):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_admin) + " does not exist!"
            }
        })
    user_admin = User_class.objects(user_id=user_id_admin)[0]
    if not user_admin:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "User ID " + str(user_id_admin) + " does not exist!"
            }
        })
    else:
        if user_admin.adminStatus:
            if not User_class.objects(user_id=user_id_input)[0].adminStatus:
                User_class.objects(user_id=user_id_input).update_one(set__adminStatus=True)
                print("Changed user status to Admin!")
                return jsonify({
                    "status_code": "201",
                    "detail": "Status of User ID " + str(user_id_input) + " is changed to Admin!"
                })
            else:
                print("User is already an admin!")
                return jsonify({
                    "status_code": "404",
                    "detail": "User ID " + str(user_id_input) + " is already an admin!"
                })
        else:
            return jsonify({
                "status_code": "403",
                "detail": "User ID " + str(user_id_admin) + " is not authorized to make another user an admin!"
            })


@app.route('/deleteUser', methods=['DELETE'])
def deleteUser():
    user_id_input = request.args.get('user_id')
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })
    User_class.objects().filter(user_id=user_id_input).delete()
    print("User deleted!")
    return jsonify({
        "status_code": "204",
        "detail": "User deleted!"
    })


@app.route('/receiveSupport', methods=['POST'])
def receiveSupport():
    user_id_input = request.args.get('user_id')  # check if the entered user id is int
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    email = User_class.objects(user_id=user_id_input)[0].email
    title = request.args.get('title')
    content = request.args.get('content')

    json_obj = {
        "user_id": user_id_input,
        "received_mail": email,
        "request": {
            "title": title,
            "content": content
        },
        "timestamp": datetime.datetime.now()
    }


    # send request to notification
    # get response and print it
    pass


@app.route('/login',methods=['POST'])
def login():
    user_name_input = request.args.get('user_name')
    password_input = request.args.get('password')
    user = User_class.objects(user_name=user_name_input)
    if not user:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error": "User does not exist"
            }
        })
        # return 'error'
    elif user[0].password != password_input:
        return jsonify({
            "status_code": "401",
            "detail": {
                "error": "Incorrect credentials"
            }
        })
        # return 'error'
    else:
        return jsonify({
            "status_code": "201",
            "detail": {
                "user_id": user[0].user_id,
                "suspendStatus": user[0].suspendStatus
            }
        })
        # return 'success'


def logout():
    pass


@app.route('/updateInfo', methods=['POST'])
def updateInfo():
    user_id_input = request.args.get('user_id')
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    update_user_name = False
    update_first_name = False
    update_last_name = False
    update_address = False
    update_email = False
    update_date_of_birth = False
    update_phone_number = False
    update_password = False

    new_user_name = request.args.get('user_name')
    old_user_name = User_class.objects(user_id=user_id_input)[0].user_name
    if new_user_name == "":
        User_class.objects(user_id=user_id_input).update_one(set__user_name=old_user_name)
    elif old_user_name != new_user_name:
        update_user_name = True
        # User_class.objects(user_id=user_id_input).update_one(set__user_name=new_user_name)
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "New user name is not valid!"
            }
        })

    new_first_name = request.args.get('first_name')
    old_first_name = User_class.objects(user_id=user_id_input)[0].first_name
    if new_first_name == "":
        User_class.objects(user_id=user_id_input).update_one(set__first_name=old_first_name)
    elif old_first_name != new_first_name:
        update_first_name = True
        # User_class.objects(user_id=user_id_input).update_one(set__first_name=new_first_name)
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "New first name is not valid!"
            }
        })

    new_last_name = request.args.get('last_name')
    old_last_name = User_class.objects(user_id=user_id_input)[0].last_name
    if new_last_name == "":
        User_class.objects(user_id=user_id_input).update_one(set__last_name=old_last_name)
    elif old_last_name != new_last_name:
        update_last_name = True
        # User_class.objects(user_id=user_id_input).update_one(set__last_name=new_last_name)
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "New last name is not valid!"
            }
        })

    new_password = request.args.get('password')
    old_password = User_class.objects(user_id=user_id_input)[0].password
    if new_password == "":
        User_class.objects(user_id=user_id_input).update_one(set__password=old_password)
    elif old_password != new_password:
        update_password = True
        # User_class.objects(user_id=user_id_input).update_one(set__address=new_address)
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "New password is not valid!"
            }
        })

    new_address = request.args.get('address')
    old_address = User_class.objects(user_id=user_id_input)[0].address
    if new_address == "":
        User_class.objects(user_id=user_id_input).update_one(set__address=old_address)
    elif old_address != new_address:
        update_address = True
        # User_class.objects(user_id=user_id_input).update_one(set__address=new_address)
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "New address is not valid!"
            }
        })

    new_email = request.args.get('email')
    old_email = User_class.objects(user_id=user_id_input)[0].email
    if new_email == "":
        User_class.objects(user_id=user_id_input).update_one(set__email=old_email)
    elif old_email != new_email:
        update_email = True
        # User_class.objects(user_id=user_id_input).update_one(set__email=new_email)
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "New email is not valid!"
            }
        })

    try:
        if request.args.get('date_of_birth') == "":
            old_date_obj = User_class.objects(user_id=user_id_input)[0].date_of_birth
        else:
            date_of_birth = list(map(int, request.args.get('date_of_birth').split("-")))
    except ValueError:
        # print("Date of birth should have only integer values. ")
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Date of birth should have only integer values"
            }
        })
    except IndexError:
        # print("Date of birth should have integer values separated by '-'")
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Date of birth should have integer values separated by '-'"
            }
        })

    if request.args.get('date_of_birth') == "":
        old_date_obj = User_class.objects(user_id=user_id_input)[0].date_of_birth
    else:
        date_of_birth = list(map(int, request.args.get('date_of_birth').split("-")))
        date_obj = datetime.datetime(int(date_of_birth[0]), int(date_of_birth[1]), int(date_of_birth[2]))

    if request.args.get('date_of_birth') == "":
        User_class.objects(user_id=user_id_input).update_one(set__date_of_birth=old_date_obj)
    else:
        update_date_of_birth = True
        # User_class.objects(user_id=user_id_input).update_one(set__date_of_birth=date_obj)

    new_phone_number = request.args.get('phone_number')
    old_phone_number = User_class.objects(user_id=user_id_input)[0].phone_number
    if new_phone_number == "":
        User_class.objects(user_id=user_id_input).update_one(set__phone_number=old_phone_number)
    elif not User_class().isint(new_phone_number) or len(new_phone_number) != 10 and len(new_phone_number) != 0:
        # print('Phone number is not a valid number!')
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Phone number is not a valid number!"
            }
        })
    else:
        new_phone_number = int(new_phone_number)
        if new_phone_number != old_phone_number:
            update_phone_number = True
            # User_class.objects(user_id=user_id_input).update_one(set__phone_number=new_phone_number)
        else:
            return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "New phone number is not valid!"
                }
            })

    if update_user_name:
        User_class.objects(user_id=user_id_input).update_one(set__user_name=new_user_name)
    if update_first_name:
        User_class.objects(user_id=user_id_input).update_one(set__first_name=new_first_name)
    if update_last_name:
        User_class.objects(user_id=user_id_input).update_one(set__last_name=new_last_name)
    if update_address:
        User_class.objects(user_id=user_id_input).update_one(set__address=new_address)
    if update_email:
        User_class.objects(user_id=user_id_input).update_one(set__email=new_email)
    if update_date_of_birth:
        User_class.objects(user_id=user_id_input).update_one(set__date_of_birth=date_obj)
    if update_phone_number:
        User_class.objects(user_id=user_id_input).update_one(set__phone_number=new_phone_number)
    if update_password:
        User_class.objects(user_id=user_id_input).update_one(set__password=new_password)

    if not update_user_name and not update_last_name and not update_first_name and not update_address and not update_email and not update_date_of_birth and not update_phone_number and not update_password:
        return jsonify({
            "status_code": "404",
            "detail": "No updates were made"
        })

    user = User_class.objects(user_id=user_id_input)[0]
    return jsonify({
        "status_code": "201",
        "detail": {
            "user_data" : user.to_json()
        }
    })




def viewBids():
    # send user id to auction
    # get bids from auction
    pass


@app.route('/addItemToWatchList', methods=['POST'])
def addItemToWatchList():
    user_id_input = request.args.get('user_id')  # check if user id is int
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    item_id_input = request.args.get('item_id')
    if not User_class().isint(item_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Item ID is not a valid integer!"
            }
        })

    item_id_input = int(item_id_input)
    response = requests.get("http://service.item:5000/searchItemId",params={'item_id': item_id_input})
    # CHECK FOR ITEM STATUS CODES
    try:
        if response.json()["status_code"] != "200": # This line should check for status_code == 200, then add price to total
            return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item "+ str(item_id_input) +" does not exist!"
                }
            })
    except KeyError:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Item "+ str(item_id_input) +" does not exist!"
            }
        })

    u = User_class.objects(user_id=user_id_input)[0]
    if item_id_input not in u.watchlist:
        u.watchlist.append(item_id_input)
        u.save()
        return jsonify({
            "status_code": "201",
            "detail": "Item "+ str(item_id_input) +" added to the user's watchlist!"
        })
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error": "Item "+ str(item_id_input) +" already in user's watchlist!"
            }
        })


@app.route('/addItemToCart', methods=['POST'])
def addItemToCart():
    user_id_input = request.args.get('user_id')  # check if user id is int
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "400",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    item_id_input = request.args.get('item_id')
    if not User_class().isint(item_id_input):
        return jsonify({
            "status_code": "400",
            "detail": {
                "error" : "Item ID is not a valid integer!"
            }
        })

    item_id_input = int(item_id_input)
    response = requests.get("http://service.item:5000/searchItemId",params={'item_id': item_id_input})
    # CHECK FOR ITEM STATUS CODES
    try:
        if response.json()["status_code"] != "200":
            return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item "+ str(item_id_input) +" does not exist!"
                }
            })
    except KeyError:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Item "+ str(item_id_input) +" does not exist!"
            }
        })

    u = User_class.objects(user_id=user_id_input)[0]
    if item_id_input not in u.cart:
        u.cart.append(item_id_input)
        u.save()
        return jsonify({
            "status_code": "201",
            "detail": "Item "+ str(item_id_input) +" added to the user's cart!"
        })
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error": "Item "+ str(item_id_input) +" already in user's cart!"
            }
        })


@app.route('/deleteItemFromCart', methods=['DELETE'])
def deleteItemFromCart():
    user_id_input = request.args.get('user_id')  # check if user id is int
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    item_id_input = request.args.get('item_id')
    if not User_class().isint(item_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Item ID is not a valid integer!"
            }
        })

    item_id_input = int(item_id_input)

    u = User_class.objects(user_id=user_id_input)[0]
    if item_id_input in u.cart:
        u.update(pull__cart=item_id_input)
        u.save()
        return jsonify({
            "status_code": "204",
            "detail": "Item "+ str(item_id_input) +" deleted from the user's cart!"
        })
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error": "Item "+ str(item_id_input) +" does not exist in the user's cart!"
            }
        })



@app.route('/deleteItemFromWatchList', methods=['DELETE'])
def deleteItemFromWatchList():
    user_id_input = request.args.get('user_id')  # check if user id is int
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    item_id_input = request.args.get('item_id')
    if not User_class().isint(item_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Item ID is not a valid integer!"
            }
        })

    item_id_input = int(item_id_input)

    u = User_class.objects(user_id=user_id_input)[0]
    if item_id_input in u.watchlist:
        u.update(pull__watchlist=item_id_input)
        u.save()
        return jsonify({
            "status_code": "204",
            "detail": "Item "+ str(item_id_input) +" deleted from the user's watchlist!"
        })
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error": "Item "+ str(item_id_input) +" does not exist in the user's watchlist!"
            }
        })



@app.route('/viewWatchList', methods=['GET'])
def viewWatchList():
    user_id_input = request.args.get('user_id')  # check if user id is int
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    u = User_class.objects(user_id=user_id_input)[0]
    if u.watchlist:
        return jsonify({
            "status_code": "200",
            "detail": {
                "watchlist": u.watchlist
            }
        })
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error": "User's watchlist is empty!"
            }
        })



@app.route('/viewCart', methods=['GET'])
def viewCart():
    user_id_input = request.args.get('user_id')  # check if user id is int
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    u = User_class.objects(user_id=user_id_input)[0]
    if u.cart:
        return jsonify({
            "status_code": "200",
            "detail": {
                "cart": u.cart
            }
        })
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error": "User's cart is empty!"
            }
        })


@app.route('/checkout', methods=['POST'])
def checkout():
    # send details to payment processing
    # send user id, cart to payment processing
    # delete cart items in the user
    user_id_input = request.args.get('user_id')  # check if user id is int
    if not User_class.objects(user_id=user_id_input):
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "The user id that you entered as input does not exist!"
            }
        })

    u = User_class.objects(user_id=user_id_input)[0]
    if u.cart:
        cart_id = random.randint(1, 10000)
        items_not_in_cart = []
        total = 0
        for i in u.cart:
            response = requests.get("http://service.item:5000/searchItemId",params={'item_id': i})
            # CHECK FOR ITEM STATUS CODES
            try:
                if response.json()["detail"]["item_data"]["item_price"]: # This line should check for status_code == 200, then add price to total
                    price = response.json()["detail"]["item_data"]["item_price"]
                    total += price
            except KeyError:
                items_not_in_cart.append(i)

        if total > 0:
            method = "card"
            num = []
            for i in range(16):
                num.append(random.randint(1, 9))
            method_info = int(''.join(map(str, num)))
            billing_address = User_class.objects(user_id=user_id_input)[0].address
            shipping_address = User_class.objects(user_id=user_id_input)[0].address
            params = {
                'user_id': user_id_input,
                'cart_id': cart_id,
                'total': total,
                'payment_method': {
                    'method': method,
                    'method_info': method_info,
                    'billing_address': billing_address,
                    'shipping_address': shipping_address
                }
            }
            
            json_params = json.dumps(params)            
            

            resp = requests.post("http://service.payment:5000/pay_for_cart", json=json_params)
            
            if resp.status_code == 201:
                for i in u.cart:
                    response = requests.delete("http://service.item:5000/deleteCartItem",params={'item_id': i})
                    if response.json()['status_code'] != "204":
                        print(response.json()['detail'])
                u.cart = []
                u.save()
                return resp.text
            else:
                return resp.text
        else:
            return jsonify({
                "status_code": "404",
                "detail": {
                    "error": "Total is zero! Checkout cannot be processed!"
                }
            })
    else:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error": "User's cart is empty!"
            }
        })


class User_class(db.Document):
    user_id = db.IntField(required=True)
    user_name = db.StringField(required=True)
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    password = db.StringField(required=True)
    date_of_birth = db.DateTimeField(required=True)
    phone_number = db.IntField(required=True)
    address = db.StringField(required=True)
    email = db.StringField(required=True)
    suspendStatus = db.BooleanField(required=False)
    adminStatus = db.BooleanField(required=False)
    cart = db.ListField(required=False, default=[])
    watchlist = db.ListField(required=False, default=[])

    meta = {
        'db_alias': 'core',
        'collection': 'users'
    }

    def to_json(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "password": self.password,
            "date_of_birth": self.date_of_birth,
            "phone_number": self.phone_number,
            "address": self.address,
            "email": self.email,
            "suspendStatus": self.suspendStatus,
            "adminStatus": self.adminStatus,
            "cart": self.cart,
            "watchlist": self.watchlist
        }

    def isint(self, num):
        try:
            int(num)
            return True
        except ValueError:
            return False

if __name__ == "__main__":
    # app.run()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)