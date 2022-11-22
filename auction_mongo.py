from pymongo import MongoClient

def get_db(address=None):
    '''
    '''
    if not address:
        conn_str = 'mongodb+srv://localhost/'
    else:
        conn_str = address
        
    client = MongoClient(conn_str)

    return client['auctions']
    '''
    After line 9, you have the overall db ready to be instantiated as you add collections
    collection_name = auc_db['collection name'] should be run as many times as you need collections within the auctions database
    collection_name.insert_one(dictionary) will insert a record each time you need to
    .update_one()//.update_many() will run updates as needed on documents in the collection
    .find_one()//.find() will query for documents as needed.
    '''