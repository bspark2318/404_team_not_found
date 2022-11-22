import mongoengine

class Listing(mongoengine.Document):
    listing_id = mongoengine.IntField(required=True)
    starting_price = mongoengine.FloatField(required=True)
    description = mongoengine.StringField()
    increment = mongoengine.IntField(required=True)
    seller = mongoengine.IntField(required=True)
    watchers = mongoengine.ListField()
    live = mongoengine.BooleanField(required=True)


    meta = {
        'db_alias': 'core',
        'collection': 'listings',
        'strict': False
    }


    def __repr__(self):
        '''
        '''
        return f'{dict(self.to_mongo())}'
        #return f'Listing Number: {self.listing_id} contains {self.description}.'