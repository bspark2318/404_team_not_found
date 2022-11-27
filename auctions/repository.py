import mongoengine
from listing import Listing
#from auction import Auction
import datetime


def create_listing(item_details):
    '''
    '''

    if get_listing(item_details['item_id']):
        return 400, 'duplicate listing'

    listing = Listing()

    listing.listing_id = item_details['item_id']
    listing.start_time = item_details['start_time']
    listing.starting_price = item_details['price']
    listing.current_price = item_details['price']
    listing.increment = item_details['increment']
    listing.description = item_details['description']
    listing.seller = item_details['user_id']

    listing.watchers = item_details['watchers']
    listing.end_time = item_details['end_time']
    listing.endgame = item_details['endgame']

    listing.save()

    return listing


def get_listing(listing_id):
    '''
    '''

    listing = Listing.objects(listing_id=listing_id).first()

    if not listing:
        return False
        #return 404, 'Listing does not exist'

    return listing


def update_listing(user_id, listing_id, details):
    '''
    '''
    
    structure = [
        'starting_price',
        'current_price',
        'start_time',
        'end_time',
        'endgame',
        'increment',
        'description',
        'watchers',
        'status',
        'bid_list'
        ]

    for detail in details:
        if detail not in structure:
            return 400, f'There is no listing detail named {detail}. Please select any of {structure}.'

    listing = get_listing(listing_id)

    if user_id == listing.seller:
        for k, v in details.items():
            setattr(listing, k, v)
        listing.save()
        return 200, f'Listing number {listing_id} has been updated.'
    
    return 400, 'Unauthorized update attempt.'



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


def view_live():
    '''
    '''
    live_listings = Listing.objects(status='live')
    return live_listings


def view_metrics(window_start, window_end):
    '''
    '''
    #metrics = Listing.objects.find({end_time: {$gt: window_start, $lt: window_end}, status: 'Complete' })

