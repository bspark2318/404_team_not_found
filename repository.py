import mongoengine
from listing import Listing
from auction import Auction


def create_listing(listing_id, starting_price, increment, description, seller, watchers, live):
    '''
    '''

    listing = Listing()

    listing.listing_id = listing_id
    listing.starting_price = starting_price
    listing.increment = increment
    listing.description = description
    listing.seller = seller
    listing.watchers = watchers
    listing.live = live

    listing.save()

    return listing


def get_listing(listing_id):
    '''
    '''

    listing = Listing.objects(listing_id=listing_id).first()

    if not listing:
        return 404, 'Listing does not exist'

    return listing



def delete_listing(user_id, listing_id):
    '''
    '''

    listing = get_listing(listing_id)

    if type(listing) == tuple:
        return listing

    if user_id == listing.seller:
        listing.delete()
        return 200, f'Permanently Deleted {listing_id}'
    
    return 400, 'Unauthorized deletion attempt.'


def update_listing(user_id, listing_id, details):
    '''
    '''
    
    structure = [
        'starting_price',
        'increment',
        'description',
        'seller',
        'watchers',
        'live']

    if detail not in structure:
        return 400, f'There is no listing detail named {detail}. Please select any of {structure}.'

    listing = get_listing(listing_id)

    if user_id == listing.seller:
        for k, v in details.items():
            setattr(listing, k, v)
        listing.save()
        return 200, f'Listing number {listing_id} has been updated.'
    
    return 400, 'Unauthorized update attempt.'


def view_live():
    '''
    '''
    live_listings = Listing.objects(live=True)
    return live_listings


def get_auction(auction_id):
    '''
    '''

    auction = Auction.objects(auction_id=auction_id).first()

    if not listing:
        return 404, 'Listing does not exist'

    return listing


def create_auction(listing_id, start_time, end_time, endgame=10):
    '''
    '''
    listing = get_listing(listing_id)
    auction = Auction(
                    start_time=start_time, end_time=end_time,
                    endgame=endgame, current_price=listing.starting_price,
                    increment = listing.increment, bid_list=[],
                    auction_id=listing_id, seller = listing.seller,
                    status = 'Prep'
                    )

    return auction


def modify_auction(user_id, auction_id, details):
    '''
    '''

    structure = [
        'start_time',
        'end_time',
        'endgame',
        ]

    if detail not in structure:
        return 400, f'There is no listing detail named {detail}. Please select any of {structure}.'

    auction = get_auction(auction_id)

    if user_id == auction.seller:
        for k, v in details.items():
            setattr(listing, k, v)
        auction.save()
        return 200, f'Listing number {auction_id} has been updated.'
    
    return 400, 'Unauthorized update attempt.'


def view_metrics(window_start, window_end):
    '''
    '''
    #metrics = Auction.objects.find({end_time: {$gt: window_start, $lt: window_end}, status: 'Complete' })

