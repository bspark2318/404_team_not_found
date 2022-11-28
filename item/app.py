import flask
from flask_mongoengine import MongoEngine
import requests
import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
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
    try:
        int(num)
        return True
    except ValueError:
        return False


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


@app.route('/searchItemId', methods=['GET'])
def Search_ItemID():
    '''
    Function to Search an item by the Item ID 
    '''
    search_inp = request.args.get('item_id')
    if not isint(search_inp):
        return jsonify({'error': 'Item Id has to be an integer'})
    presence_check = len(Item_class.objects(item_id=search_inp))
    if presence_check == 0:
        return jsonify({'error': 'Such an item ID does not exist'})
    search_out = Item_class.objects(item_id=search_inp)[0]
    if not search_out:
        return jsonify({'error': 'Data not found'})
    else:
        return jsonify(search_out.to_json())


@app.route('/searchItemName', methods=['GET'])       
def Search_ItemName():
    '''
    Function to Search an item by the Item name
    '''
    search_inp = request.args.get('item_name')
    presence_check = len(Item_class.objects(item_name=search_inp))
    if presence_check == 0:
        return jsonify({'error': 'Such an item name does not exist'})
    search_out = Item_class.objects(item_name=search_inp)
    if not search_out:
        return jsonify({'error': 'Data not found'})
    else:
        return jsonify(search_out.to_json())


@app.route('/searchCategoryId', methods=['GET'])   ###########check op format
def Search_CategoryID():
    # mongo_setup.global_init_category()
    search_inp = request.args.get('category_id')
    if not isint(search_inp):
        return jsonify({'error': 'Category Id has to be an integer'})
    presence_check = len(Category_class.objects(category_id=search_inp))
    if presence_check == 0:
        return jsonify({'error': 'Such a category ID does not exist'})
    search_out = Category_class.objects(category_id=search_inp)[0].category_items
    # print(search_out)
    if not search_out:
        return jsonify({'error': 'Data not found'})
    else:
        final_op = []
        for i in search_out:

            final_op.append(Item_class.objects(item_id=i).to_json())
        # print(final_op)
        # return jsonify(final_op.to_json())
        return json.dumps(final_op)


@app.route('/createItem', methods=["POST"])
def CreateItem():
    # print("Please press enter to skip optional fields")
    
    if len(Item_class.objects().all()) == 0:
        item_id = 1
    else:   
        item_id = (Item_class.objects.order_by('-id').first().item_id) + 1

    item_name = request.args.get('item_name')
    if item_name == "":
        return jsonify({
            "status_code": "400",
            "detail": {
                "error" : "Name cannot be left blank"
            }
        })

    item_price = request.args.get('item_price')
    try:
        item_price = float(request.args.get('item_price'))
    except ValueError:
        return jsonify({
            "status_code": "400",
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
            item_weight = float(request.args.get('item_price'))
        except ValueError:
            return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Item weight must be a valid number"
                }
            })

    try:
        item_categories = list(map(int, request.args.get('item_categories').split()))
    except ValueError:
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Item categories must be a valid integers"
                }
            })
        
    i = Item_class()
    i.item_id = item_id
    i.item_name = item_name
    i.item_description = item_description 
    i.item_price = item_price
    i.item_weight = item_weight
    i.item_categories = item_categories
    i.item_status = "BuyNow"

    i.save()

    return jsonify({
        "status_code": "200",
        "detail": {
            "item_id" : item_id
        }
    })


@app.route('/deleteItem', methods=["DELETE"])
def DeleteItem():
    item_id_to_delete = request.args.get('item_id')
    if not isint(item_id_to_delete):
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Item_class.objects(item_id=item_id_to_delete))
    if presence_check == 0:
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Such an item ID does not exist"
                }
            })
    Item_class.objects().filter(item_id=item_id_to_delete).delete()
    return jsonify({
        "status_code": "200",
        "detail": {
            "item_id" : "item deleted"
        }
    })


@app.route('/updateItem', methods=["POST"])
def UpdateItem():
    
    update_name = False
    update_price = False
    update_description = False
    update_weight = False

    item_id_to_update = request.args.get('item_id')
    if not isint(item_id_to_update):
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Item_class.objects(item_id=item_id_to_update))
    if presence_check == 0:
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Such an item ID does not exist"
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
                "status_code": "400",
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
                "status_code": "400",
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
        "status_code": "200",
        "detail": {
            "item_id" : "Item Updated"
        }
    })


@app.route('/createCategory', methods=["POST"])
def CreateCategory():

    if len(Category_class.objects().all()) == 0:
        category_id = 1
    else:   
        category_id = (Category_class.objects.order_by('-id').first().category_id) + 1

    category_name = request.args.get('category_name')
    if category_name == "":
        return jsonify({
            "status_code": "400",
            "detail": {
                "error" : "Category name cannot be left blank"
            }
        })

    category_description = request.args.get('category_description')

    category_items = []
    
    c = Category_class()
    c.category_id = category_id
    c.category_name = category_name
    c.category_description = category_description 
    c.category_items = category_items

    c.save()

    return jsonify({
        "status_code": "200",
        "detail": {
            "category_id" : category_id
        }
    })


@app.route('/deleteCategory', methods=["DELETE"])
def DeleteCategory():
    category_id_to_delete = request.args.get('category_id')
    if not isint(category_id_to_delete):
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Category_class.objects(category_id=category_id_to_delete))
    if presence_check == 0:
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Such a category ID does not exist"
                }
            })
    Category_class.objects().filter(category_id=category_id_to_delete).delete()
    return jsonify({
        "status_code": "200",
        "detail": {
            "category_id" : "Category deleted"
        }
    })


@app.route('/updateCategory', methods=["POST"])
def UpdateCategory():

    update_name = False
    update_description = False

    category_id_to_update = request.args.get('category_id')
    if not isint(category_id_to_update):
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Item Id has to be an integer"
                }
            })
    presence_check = len(Category_class.objects(category_id=category_id_to_update))
    if presence_check == 0:
        return jsonify({
                "status_code": "400",
                "detail": {
                    "error" : "Such a category ID does not exist"
                }
            })

    change_to_name = request.args.get('category_name')
    old_value_name = Category_class.objects(item_id=category_id_to_update)[0].category_name
    
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
        "status_code": "200",
        "detail": {
            "category_id" : "Category Updated"
        }
    })
    

class Item_class(db.Document):
    item_id = db.IntField(required = True)
    item_name = db.StringField(required=True)
    item_description = db.StringField(required=False)
    item_price = db.FloatField(required=True)
    item_weight = db.FloatField(required=False)
    item_categories = db.ListField(required=False)
    item_status = db.StringField(required=True)

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
            "item_categories": self.item_categories
        }


class Category_class(db.Document):
    category_id = db.IntField(required = True)
    category_name = db.StringField(required=True)
    category_description = db.StringField(required=False)
    category_items = db.ListField(required=False)

    meta = {
        'db_alias': 'core_category',
        'collection': 'categories'
    }


if __name__ == "__main__":
    # app.run()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)