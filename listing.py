import mongoengine
import repository as rep
import datetime
from time import ctime


class Listing(mongoengine.Document):
    listing_id = mongoengine.IntField(required=True)
    start_time = mongoengine.DateTimeField(required=True)
    end_time = mongoengine.DateTimeField()
    endgame = mongoengine.IntField(default=10)
    starting_price = mongoengine.FloatField(required=True)
    current_price = mongoengine.FloatField()
    increment = mongoengine.IntField(required=True)
    description = mongoengine.StringField()
    bid_list = mongoengine.ListField(default=[])
    seller = mongoengine.IntField(required=True)
    watchers = mongoengine.ListField(default=[])
    status = mongoengine.StringField(default='prep')


    meta = {
        'db_alias': 'core',
        'collection': 'listings',
        'strict': False
    }


    def start_auction(self):
        '''
        '''

        assert self.end_time, 'please schedule an end time for your auction'
        assert self.status != 'live', 'this is an active auction'

        self.status = 'live'

        rep.update_listing(self.seller, self.listing_id, {'status':'live'})

        #whatever function starts the clock


    def take_bid(self, bidder, amount):
        '''
        '''
        assert self.status == 'live', f'This auction has not started'
        assert amount >= self.current_price + self.increment, f'Bid total less than increment, minimum acceptable bid is: {self.current_price + self.increment}'
        
        current_leader = None
        bid = (bidder, amount, ctime())

        if self.bid_list:
            current_leader, _, __ = self.bid_list[0]

        self.current_price = amount
        self.bid_list.insert(0, bid)

        rep.update_listing(self.seller, self.listing_id, {'current_price':self.current_price, 'bid_list': self.bid_list})
    

        if current_leader and bidder != current_leader: # New highest bidder
            self.outbid_alert(current_leader, amount)
        self.bid_placed_alert(amount)
            #return 201, f'hi bidder,bid placed at {amount}. hi seller, your auction {self.listing_id} received a bid of {amount}' # Replace with ACTUAL IMPLEMENTATION
        
        return 201, f'hi seller, your auction {self.listing_id} received a bid of {amount}'


    def pass_winner(self):
        '''
        Gets triggered when ctime == end_time
        '''
        winner, amount, _ = self.bid_list[0]
        payout_details = {
            'winner': winner,
            'cost': amount,
            'seller': self.seller,
            'item': self.listing_id
        }

        'send payour_details to PAYMENT PROCESSING for execution'

        return 200, payout_details  # Replace with ACTUAL IMPLEMENTATION
    

    def outbid_alert(self, recipient, new_highest):
        '''
        '''
        message = f'''
            You have been outbid on {self.listing_id}. The new highest bid is {new_highest}.
        '''
        'send (recipient, message) to NOTIFICATION SERVICE for delivery'
        return 200, (recipient, message) # Replace with ACTUAL IMPLEMENTATION


    def bid_placed_alert(self, new_highest):
        '''
        '''

        message = f'''
            A new bid of {new_highest} was placed on {self.listing_id}.
        '''

        'send (self.seller, message) to NOTIFICATION SERVICE for delivery'

        return 200, self.seller, message  # Replace with ACTUAL IMPLEMENTATION


    def endgame_alert(self):
        '''
        '''
        recipients = set(self.watchers)

        for bid in self.auction.bid_list:
            recipients.add(bid[0])

        message = f'''
            The auction for {self.listing_id} will end at {self.auction.endgame}. The price is currently {self.auction.current_price}.
        '''
        'send (recipients, message) to NOTIFICATION SERVICE for delivery'

        return 200, recipients, message  # Replace with ACTUAL IMPLEMENTATION


        def __repr__(self):
            '''
            '''
            return f'{dict(self.to_mongo())}'
            #return f'Listing Number: {self.listing_id} contains {self.description}.'