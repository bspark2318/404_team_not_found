import mongoengine
from time import ctime

class Auction(mongoengine.EmbeddedDocument):
    start_time = mongoengine.DateTimeField(required=True)
    end_time = mongoengine.DateTimeField()
    endgame = mongoengine.DateTimeField(required=True)
    current_price = mongoengine.FloatField(required=True)
    increment = mongoengine.IntField(required=True)
    bid_list = mongoengine.ListField(required=True)
    auction_id = mongoengine.IntField(required=True)
    seller = mongoengine.IntField(required=True)
    status = mongoengine.StringField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'auctions',
        'strict': False
    }


    def start_auction(self):
        '''
        '''

        self.status = 'Live'
        #whatever function starts the clock

    def take_bid(self, bidder, amount):
        '''
        '''

        assert amount >= self.current_price + self.increment, f'Bid total less than increment, minimum acceptable bid is: {self.current_price + self.increment}'
        
        current_leader = None
        bid = (bidder, amount, ctime())

        if self.bid_list:
            current_leader, _, __ = self.bid_list[0]

        self.current_price = amount
        self.bid_list.insert(0, bid)
    
        #self.bid_placed_alert() ACTUAL IMPLEMENTATION

        if current_leader and bidder != current_leader:
            #self.outbid_alert(current_leader, amount) ACTUAL IMPLEMENTATION
            return 201, f'hi bidder,bid placed at {amount}. hi seller, your auction {self.auction_id} received a bid of {amount}' # Replace with ACTUAL IMPLEMENTATION
        
        return 201, f'hi seller, your auction {self.auction_id} received a bid of {amount}'


    def pass_winner(self):
        '''
        Gets triggered when ctime == end_time
        '''
        winner, amount, _ = self.bid_list[0]
        payout_details = {
            'winner': winner,
            'cost': amount,
            'seller': self.seller,
            'item': self.auction_id
        }

        'send payour_details to PAYMENT PROCESSING for execution'

        return 200, payout_details  # Replace with ACTUAL IMPLEMENTATION

    def __repr__(self):
        return f'{dict(self.to_mongo())}'