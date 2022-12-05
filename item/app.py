import flask
from flask_mongoengine import MongoEngine
import requests
import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import sys
# from flask_sqlalchemy import SQLAlchemy

db = MongoEngine()
connString = os.environ['MONGODB_CONNSTRING']   ### for docker uncomment
app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = [
    {
        "db": "item",
        # "host": "localhost",               ### comment if docker
        "host": connString,              ### comment if localhost
        "port": 27017,
        "alias": "core_item",
    },
    {
        "db": "category",
        # "host": "localhost",
        "host": connString,
        "port": 27017,
        "alias": "core_category",
    }
]
db.init_app(app)


@app.route('/')
def hello_world():
    return 'Item Microservice'


def isint(num):
    '''
    To check if the arg passed in an integer
    '''
    try:
        int(num)
        return True
    except ValueError:
        return False


def isfloat(num):
    '''
    To check if the arg passed in a float
    '''
    try:
        float(num)
        return True
    except ValueError:
        return False


def admin_status(user_id):
    params = { 'user_id': user_id }
    response = requests.get("http://service.user:5000/getAdminStatus",params=params)

    if response.json()['status_code'] == "200":
        op = response.json()["detail"]["user_data"]
    else:
        op = response.json()["detail"]
    return op


@app.route('/categorize', methods=['POST'])
def Categorize():
    '''
    Fucntion to add a category to an item
    '''
    item_inp = int(request.args.get('item_id'))
    categorize_inp = int(request.args.get('category_id'))

    if not isint(item_inp):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    if not isint(categorize_inp):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Category Id has to be an integer"
                }
            })

    presence_check = len(Item_class.objects(item_id=item_inp))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Such an item ID does not exist'
                }
            })
    presence_check = len(Category_class.objects(category_id=categorize_inp))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Such a category ID does not exist'
                }
            })
    if_admin = admin_status(int(request.args.get('session_owner')))
    if not if_admin:
        if not (Item_class.objects(item_id=item_inp)[0].item_owner == int(request.args.get('session_owner'))):
            return jsonify({
                    "status_code": "403",
                    "detail": {
                        "error" : "You are not the owner and cannot make this update"
                    }
                })

    item_out = Item_class.objects(item_id=item_inp)[0]
    cat_out = Category_class.objects(category_id=categorize_inp)[0]
    if item_inp not in cat_out.category_items:
        cat_out.category_items.append(item_inp)
        cat_out.save()
    if categorize_inp not in item_out.item_categories:
        item_out.item_categories.append(categorize_inp)
        item_out.save()

    return jsonify({
        "status_code": "201",
        "detail": "Item Categorized!"
    })


@app.route('/flag', methods=['POST'])
def Flag():
    '''
    Fucntion to let a user flag an item
    '''
    item_inp = int(request.args.get('item_id'))
    flagger = int(request.args.get('session_owner'))

    if not isint(item_inp):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })

    presence_check = len(Item_class.objects(item_id=item_inp))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Such an item ID does not exist'
                }
            })

    item_out = Item_class.objects(item_id=item_inp)[0]

    if flagger not in item_out.item_flag_list:
        item_out.item_flag_list.append(flagger)
        item_out.save()

    return jsonify({
        "status_code": "201",
        "detail": "Item Flagged!"
    })


@app.route('/viewflag', methods=['GET'])
def viewflag():
    '''
    Fucntion to let a user flag an item
    '''

    flagger = int(request.args.get('session_owner'))

    if_admin = admin_status(flagger)
    if not if_admin:
        return jsonify({
                "status_code": "403",
                "detail": {
                    "error" : "You are not an admin"
                }
            })


    search_out = Item_class.objects().all()
    if not search_out:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Data not found'
                }
            })
    else:
        final_op = []
        for i in search_out:
            print(i, flush=True)
            if len(i.item_flag_list) > 0:
                print(i.item_flag_list, flush=True)
                final_op.append(i.to_json())

        return jsonify({
                "status_code": "200",
                "detail": {
                    "item_data" : final_op
                }
            })


@app.route('/searchItemId', methods=['GET']) #### status code
def Search_ItemID():
    '''
    Function to Search an item by the Item ID 
    '''
    search_inp = request.args.get('item_id')
    if not isint(search_inp):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Item_class.objects(item_id=search_inp))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Such an item ID does not exist'
                }
            })
        
    search_out = Item_class.objects(item_id=search_inp)[0]
    if not search_out:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Data not found'
                }
            })
    else:
        item_owner = search_out.item_owner
        resp = requests.get("http://service.user:5000/getEmailId",params={'user_id': item_owner})
        if resp.json()["status_code"] == "200":
            item_owner_email = resp.json()["detail"]["user_data"]
            return jsonify({
                    "status_code": "200",
                    "detail": {
                        "item_data":
                            {
                                "item_id": search_out.item_id,
                                "item_name": search_out.item_name,
                                "item_price": search_out.item_price,
                                "item_description": search_out.item_description,
                                "item_weight": search_out.item_weight,
                                "item_categories": search_out.item_categories,
                                "item_owner": search_out.item_owner,
                                "item_owner_email": item_owner_email,
                                "item_status": search_out.item_status
                            }
                        }
                     })
        else:
            return resp.json()


@app.route('/searchItemName', methods=['GET'])       
def Search_ItemName():
    '''
    Function to Search an item by the Item name
    '''
    search_inp = request.args.get('item_name')
    presence_check = len(Item_class.objects(item_name=search_inp))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Such an item name does not exist'
                }
            })
    search_out = Item_class.objects(item_name=search_inp)[0]
    if not search_out:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Data not found'
                }
            })
    else:
        return jsonify({
                "status_code": "200",
                "detail": {
                    "item_data" : search_out.to_json()
                }
            })


@app.route('/searchCategory', methods=['GET'])       
def Search_Category():
    '''
    Function to Search Category by category ID 
    '''
    search_inp = request.args.get('category_id')
    if not isint(search_inp):
        return jsonify({'error': 'Category Id has to be an integer'})
    presence_check = len(Category_class.objects(category_id=search_inp))
    if presence_check == 0:
        return jsonify({'error': 'Such a category ID does not exist'})
    search_out = Category_class.objects(category_id=search_inp)[0]
    if not search_out:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Data not found'
                }
            })
    else:
        return jsonify({
                "status_code": "200",
                "detail": {
                    "item_data" : search_out.to_json_cat()
                }
            })


@app.route('/searchCategoryId', methods=['GET'])
def Search_CategoryID():
    '''
    Search all items for a particular category
    '''
    search_inp = request.args.get('category_id')
    if not isint(search_inp):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Category Id has to be an integer"
                }
            })
    presence_check = len(Category_class.objects(category_id=search_inp))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Such a category ID does not exist'
                }
            })
    search_out = Category_class.objects(category_id=search_inp)[0].category_items
    if not search_out:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Data not found'
                }
            })
    else:
        final_op = []
        for i in search_out:
            final_op.append(Item_class.objects(item_id=i)[0].to_json())
        return jsonify({
                "status_code": "200",
                "detail": {
                    "item_data" : final_op
                }
            })


@app.route('/allCategories', methods=['GET'])
def Search_all_Categories():
    '''
    Search all existing categories
    '''
    search_out = Category_class.objects().all()
    if not search_out:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Data not found'
                }
            })
    else:
        final_op = []
        for i in search_out:
            final_op.append(i.to_json_cat())
        return jsonify({
                "status_code": "200",
                "detail": {
                    "item_data" : final_op
                }
            })


@app.route('/allItems', methods=['GET'])
def Search_all_Items():
    '''
    Search all existing items
    '''
    search_out = Item_class.objects().all()
    if not search_out:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : 'Data not found'
                }
            })
    else:
        final_op = []
        for i in search_out:
            final_op.append(i.to_json())
        return jsonify({
                "status_code": "200",
                "detail": {
                    "item_data" : final_op
                }
            })


@app.route('/createItem', methods=["POST"])
def CreateItem():
    '''
    Function to creat an item
    '''
    if len(Item_class.objects().all()) == 0:
        item_id = 1
    else:   
        item_id = (Item_class.objects.order_by('-id').first().item_id) + 1

    item_name = request.args.get('item_name')
    if item_name == "":
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Name cannot be left blank"
            }
        })

    item_price = request.args.get('item_price')
    try:
        item_price = float(request.args.get('item_price'))
    except ValueError:
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Item price must be a valid number"
            }
        })
    
    item_description = request.args.get('item_description')

    item_weight = request.args.get('item_weight')
    if item_weight == '':
        item_weight = -1
    else:
        try:
            item_weight = float(request.args.get('item_weight'))
        except ValueError:
            return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item weight must be a valid number"
                }
            })

    try:
        item_categories = list(map(int, request.args.get('item_categories').split()))
    except ValueError:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item categories must be a valid integers"
                }
            })
    for i in item_categories:
        presence_check = len(Category_class.objects(category_id=i))
        if presence_check == 0:
            return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : f"Category {str(i)} does not exist"
                }
            })

    item_owner = request.args.get('item_owner')
        
    i = Item_class()
    i.item_id = item_id
    i.item_name = item_name
    i.item_description = item_description 
    i.item_price = item_price
    i.item_weight = item_weight
    i.item_categories = item_categories
    i.item_status = "BuyNow"
    i.item_flag = False
    i.item_flag_list = []
    i.item_owner = item_owner

    i.save()

    for i in item_categories:
        cat_out = Category_class.objects(category_id=i)[0]
        cat_out.category_items.append(item_id)
        cat_out.save()

    return jsonify({
        "status_code": "201",
        "detail": {
            "item_id" : item_id
        }
    })


@app.route('/deleteItem', methods=["DELETE"])
def DeleteItem():
    '''
    Fucntion to delete an item
    '''
    item_id_to_delete = request.args.get('item_id')
    if not isint(item_id_to_delete):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Item_class.objects(item_id=item_id_to_delete))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Such an item ID does not exist"
                }
            })

    if_admin = admin_status(int(request.args.get('session_owner')))
    if not if_admin:
        if not (Item_class.objects(item_id=item_id_to_delete)[0].item_owner == int(request.args.get('session_owner'))):
            return jsonify({
                    "status_code": "403",
                    "detail": {
                        "error" : "You are not the owner and cannot make this delete"
                    }
                })

    Item_class.objects().filter(item_id=item_id_to_delete).delete()
    return jsonify({
        "status_code": "204",
        "detail": {
            "item_id" : "item deleted"
        }
    })


@app.route('/deleteCartItem', methods=["DELETE"])
def DeleteCartItem():
    '''
    Fucntion to delete an item after payment
    '''
    item_id_to_delete = request.args.get('item_id')
    if not isint(item_id_to_delete):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Item_class.objects(item_id=item_id_to_delete))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Such an item ID does not exist"
                }
            })

    Item_class.objects().filter(item_id=item_id_to_delete).delete()
    return jsonify({
        "status_code": "204",
        "detail": {
            "item_id" : "item deleted"
        }
    })


@app.route('/updateItem', methods=["POST"])
def UpdateItem():
    '''
    Function to update an item
    '''
    update_name = False
    update_price = False
    update_description = False
    update_weight = False

    item_id_to_update = request.args.get('item_id')
    if not isint(item_id_to_update):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Item_class.objects(item_id=item_id_to_update))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Such an item ID does not exist"
                }
            })
    if_admin = admin_status(int(request.args.get('session_owner')))
    if not if_admin:
        if not (Item_class.objects(item_id=item_id_to_update)[0].item_owner == int(request.args.get('session_owner'))):
            return jsonify({
                    "status_code": "403",
                    "detail": {
                        "error" : "You are not the owner and cannot make this update"
                    }
                })

    change_to_name = request.args.get('item_name')
    old_value_name = Item_class.objects(item_id=item_id_to_update)[0].item_name
    
    if change_to_name == "":
        Item_class.objects(item_id=item_id_to_update).update_one(set__item_name=old_value_name)
    elif old_value_name != change_to_name:
        # Item_class.objects(item_id=item_id_to_update).update_one(set__item_name=change_to_name)
        update_name = True

    change_to_price = request.args.get('item_price')
    old_value_price = Item_class.objects(item_id=item_id_to_update)[0].item_price
    
    if change_to_price == "":
        Item_class.objects(item_id=item_id_to_update).update_one(set__item_price=old_value_price)
    elif not isfloat(change_to_price):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Price has to be a number"
                }
            })
    elif old_value_price != change_to_price:
        # Item_class.objects(item_id=item_id_to_update).update_one(set__item_price=change_to_price) 
        update_price = True

    change_to_description = request.args.get('item_description')
    old_value_description = Item_class.objects(item_id=item_id_to_update)[0].item_description
    
    if change_to_description == "":
        Item_class.objects(item_id=item_id_to_update).update_one(set__item_description=old_value_description)
    elif old_value_description != change_to_description:
        # Item_class.objects(item_id=item_id_to_update).update_one(set__item_description=change_to_description)
        update_description = True

    change_to_weight = request.args.get('item_weight')
    old_value_weight = Item_class.objects(item_id=item_id_to_update)[0].item_weight

    if change_to_weight == "":
        Item_class.objects(item_id=item_id_to_update).update_one(set__item_weight=old_value_weight) 
    elif not isfloat(change_to_weight):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Weight has to be a number"
                }
            })
    elif old_value_weight != change_to_weight:
        # Item_class.objects(item_id=item_id_to_update).update_one(set__item_weight=change_to_weight) 
        update_weight = True

    if update_name:
        Item_class.objects(item_id=item_id_to_update).update_one(set__item_name=change_to_name)
    if update_price:
        Item_class.objects(item_id=item_id_to_update).update_one(set__item_price=change_to_price) 
    if update_description:
        Item_class.objects(item_id=item_id_to_update).update_one(set__item_description=change_to_description)
    if update_weight:
        Item_class.objects(item_id=item_id_to_update).update_one(set__item_weight=change_to_weight)
    
    return jsonify({
        "status_code": "201",
        "detail": {
            "item_id" : "Item Updated"
        }
    })


@app.route('/createCategory', methods=["POST"])
def CreateCategory():
    '''
    Function to create a category
    '''
    if len(Category_class.objects().all()) == 0:
        category_id = 1
    else:   
        category_id = (Category_class.objects.order_by('-id').first().category_id) + 1

    category_name = request.args.get('category_name')
    if category_name == "":
        return jsonify({
            "status_code": "404",
            "detail": {
                "error" : "Category name cannot be left blank"
            }
        })

    category_description = request.args.get('category_description')

    category_owner = request.args.get('category_owner')

    category_items = []
    
    c = Category_class()
    c.category_id = category_id
    c.category_name = category_name
    c.category_description = category_description 
    c.category_items = category_items
    c.category_owner = category_owner

    c.save()

    return jsonify({
        "status_code": "201",
        "detail": {
            "category_id" : category_id
        }
    })


@app.route('/deleteCategory', methods=["DELETE"])
def DeleteCategory():
    '''
    Function to delete category by category id
    '''
    category_id_to_delete = request.args.get('category_id')
    if not isint(category_id_to_delete):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Category_class.objects(category_id=category_id_to_delete))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Such a category ID does not exist"
                }
            })

    if_admin = admin_status(int(request.args.get('session_owner')))
    if not if_admin:
        if not (Category_class.objects(category_id=category_id_to_delete)[0].category_owner == int(request.args.get('session_owner'))):
            return jsonify({
                    "status_code": "403",
                    "detail": {
                        "error" : "You are not the owner and cannot make this delete"
                    }
                })

    Category_class.objects().filter(category_id=category_id_to_delete).delete()
    return jsonify({
        "status_code": "204",
        "detail": {
            "category_id" : "Category deleted"
        }
    })


@app.route('/updateCategory', methods=["POST"])
def UpdateCategory():
    '''
    Function to update category
    '''
    update_name = False
    update_description = False

    category_id_to_update = request.args.get('category_id')
    if not isint(category_id_to_update):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Category_class.objects(category_id=category_id_to_update))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Such a category ID does not exist"
                }
            })

    if_admin = admin_status(int(request.args.get('session_owner')))
    if not if_admin:
        print(Category_class.objects(category_id=category_id_to_update)[0].category_owner, flush=True)
        print(request.args.get('session_owner'), flush=True)
        if not (Category_class.objects(category_id=category_id_to_update)[0].category_owner == int(request.args.get('session_owner'))):
            return jsonify({
                    "status_code": "403",
                    "detail": {
                        "error" : "You are not the owner and cannot make this update"
                    }
                })

    change_to_name = request.args.get('category_name')
    old_value_name = Category_class.objects(category_id=category_id_to_update)[0].category_name
    
    if change_to_name == "":
        Category_class.objects(category_id=category_id_to_update).update_one(set__category_name=old_value_name)
    elif old_value_name != change_to_name:
        # Category_class.objects(category_id=category_id_to_update).update_one(set__category_name=change_to_name)
        update_name = True

    change_to_description = request.args.get('category_description')
    old_value_description = Category_class.objects(category_id=category_id_to_update)[0].category_description
    
    if change_to_description == "":
        Category_class.objects(category_id=category_id_to_update).update_one(set__category_description=old_value_description)
    elif old_value_description != change_to_description:
        # Category_class.objects(category_id=category_id_to_update).update_one(set__category_description=change_to_description)
        update_description = True

    if update_name:
        Category_class.objects(category_id=category_id_to_update).update_one(set__category_name=change_to_name)
    if update_description:
        Category_class.objects(category_id=category_id_to_update).update_one(set__category_description=change_to_description)

    return jsonify({
        "status_code": "201",
        "detail": {
            "category_id" : "Category Updated"
        }
    })


@app.route('/pushToAuction', methods=["POST"])
def pushToAuction():
    '''
    Fucntion to change status of item to Auction and pust to Auction microservice
    '''
    item_id_to_push = request.args.get('item_id')
    if not isint(item_id_to_push):
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Item_class.objects(item_id=item_id_to_push))
    if presence_check == 0:
        return jsonify({
                "status_code": "404",
                "detail": {
                    "error" : "Such an item ID does not exist"
                }
            })

    if_admin = admin_status(int(request.args.get('session_owner')))
    if not if_admin:
        if not (Item_class.objects(item_id=item_id_to_push)[0].item_owner == int(request.args.get('session_owner'))):
            return jsonify({
                    "status_code": "403",
                    "detail": {
                        "error" : "You are not the owner and cannot complete this action"
                    }
                })

    Item_class.objects(item_id=item_id_to_push).update_one(set__item_status="Auction")

    return jsonify({
        "status_code": "201",
        "detail": "Update made"
        })

    # params ={
    #     'item_id': item_id_to_push
    # }

    # # push to auction microservice
    # response = requests.post("http://service.auction:5000/create_listing", params)

    # if response.json()['status_code'] == "201" or response.json()['status_code'] == "200":
    #     return response.json()["detail"]
    # else:
    #     return response.json()["detail"]

    # return jsonify({
    #     "status_code": response.status_code,
    #     "detail": response.text
    # })


class Item_class(db.Document):
    '''
    Item class
    '''
    item_id = db.IntField(required = True)
    item_name = db.StringField(required=True)
    item_description = db.StringField(required=False)
    item_price = db.FloatField(required=True)
    item_weight = db.FloatField(required=False)
    item_categories = db.ListField(required=False)
    item_status = db.StringField(required=True)
    item_flag = db.BooleanField(requred=True)
    item_flag_list = db.ListField(required=False)
    item_owner = db.IntField(required = True)

    meta = {
        'db_alias': 'core_item',
        'collection': 'items'
    }

    def to_json(self):
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "item_price": self.item_price,
            "item_description": self.item_description,
            "item_weight": self.item_weight,
            "item_categories": self.item_categories,
            "item_owner": self.item_owner,
            "item_status": self.item_status
        }


class Category_class(db.Document):
    '''
    Category_class
    '''
    category_id = db.IntField(required = True)
    category_name = db.StringField(required=True)
    category_description = db.StringField(required=False)
    category_items = db.ListField(required=False)
    category_owner = db.IntField(required = True)

    meta = {
        'db_alias': 'core_category',
        'collection': 'categories'
    }

    def to_json_cat(self):
        return {
            "category_id": self.category_id,
            "category_name": self.category_name,
            "category_description": self.category_description,
            "category_items": self.category_items
        }


if __name__ == "__main__":
    # app.run()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)