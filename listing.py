#from auction import Auction
from time import ctime
'''
Listing Entity.
'''

class Listing:
    '''
    '''

    def __init__(self, item_details, increment, live=False):
        '''
        Listing Entity

        Inputs: item_id
                price
                increment
                description
                user_id
                watchers
                live
        '''
        self.listing_id = item_details['item_id']
        self.price = item_details['price']
        self.increment = increment
        self.description = item_details['description']
        self.seller = item_details['user_id']
        self.watchers = item_details['watchers']
        self.live = live
        self.listing_details = self.store_details()
        self.auction = None


    def store_details(self):
        '''
        '''
        listing_details = {
            'listing_id': self.listing_id,
            'starting_price': self.price,
            'increment': self.increment,
            'description': self.description,
            'seller': self.seller,
            'watchers': self.watchers,
            'live': self.live
        }
        return listing_details


    def create_auction(self, start_time, end_time, endgame=10):
        '''
        Creates an auction entity off the root of the listing

        Inputs: s_time
                e_time
                endgame
        '''
        self.auction = Auction(start_time=start_time, end_time=end_time,
                                endgame=endgame, current_price=self.price,
                                bid_list=[], auction_id=self.listing_id,
                                seller = self.seller)

        return 201, self.auction.auction_details


    def take_bid(self, bidder, amount):
        '''
        '''

        assert self.auction, 'This listing is not available for bids'
        assert amount >= self.auction.current_price + self.increment, f'Bid total less than increment, minimum acceptable bid is: {self.auction.current_price + self.increment}'
        
        current_leader = None
        bid = (bidder, amount, ctime())

        if self.auction.bid_list:
            current_leader, _, __ = self.auction.bid_list[0]

        self.auction.current_price = amount
        self.auction.auction_details['current_price'] = amount
        self.auction.bid_list.insert(0, bid)

        #self.bid_placed_alert() ACTUAL IMPLEMENTATION

        if current_leader and bidder != current_leader:
            #self.outbid_alert(current_leader, amount) ACTUAL IMPLEMENTATION
            return 201, self.bid_placed_alert(amount), self.outbid_alert(current_leader, amount) # Replace with ACTUAL IMPLEMENTATION
        
        return 201, self.bid_placed_alert(amount) # Replace with ACTUAL IMPLEMENTATION
        

    def delete_listing(self, user_id, listing_id):
        '''
        '''
        if user_id == self.seller and listing_id == self.listing_id:
            'send a delete query to the database'
            return 200, f'Permanently Deleted {listing_id}'


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
        return f'{self.listing_details}'


class Auction:
    '''
    '''

    def __init__(self, start_time, end_time, endgame, current_price, bid_list, auction_id, seller):
        '''
        '''
        self.start_time = start_time
        self.end_time = end_time
        self.endgame = endgame
        self.current_price = current_price
        self.bid_list = bid_list
        self.auction_id = auction_id
        self.seller = seller
        self.auction_details = self.store_details()
        


    def store_details(self):
        '''
        '''
        return {
            'start time': self.start_time,
            'end time': self.end_time,
            'endgame': self.endgame,
            'current price': self.current_price,
            'bids': self.bid_list,
            'id': self.auction_id,
            'seller': self.seller
        }

    def mod_duration(self, start_time=None, end_time=None):
        '''
        '''

        if start_time and end_time:
            self.start_time = start_time
            self.end_time = end_time
            return 200, f'Now Starts: {self.start_time}. Now Ends: {self.end_time}' # Replace with ACTUAL IMPLEMENTATION
        
        elif end_time:
            self.end_time = end_time
            return 200, f'Now Ends: {self.end_time}' # Replace with ACTUAL IMPLEMENTATION

        elif start_time:
            self.start_time = start_time
            return 200, f'Now Starts: {self.start_time}.' # Replace with ACTUAL IMPLEMENTATION
        
        else:
            return 400, 'No modifications supplied, no changes made.'


    def pass_winner(self):
        '''
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
        '''
        '''
        # Need a separate repr for when the auction is live
        return f'The auction begins {self.start_time}, with a price of {self.current_price}, and ends {self.end_time}'


class MetaFunctions:
    '''
    '''

    def view_live_auctions(self):
        '''
        '''

        'write a query for all listings where live==False'
        '''
        {
        status_code: 200
        auctions (single object): {
            item_name: string
            description: string
            price: float
            e_time: dateTime
            }
        }
        '''


    def view_metrics(self, window_start, window_end):
        '''
        '''

        'write a query for all listings with a start_time >= window_start and an end_time <= window_end'
        '''return
        {
        status_code
        metrics (single object): {
            listing_id: int
            sale_price: float
            seller: int
            buyer: int
            }
        }
    '''
