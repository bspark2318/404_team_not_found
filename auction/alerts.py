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