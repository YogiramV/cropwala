# models/auction.py
from datetime import datetime
from bson import ObjectId
from models import db

class Auction:
    @staticmethod
    def create(product_id, farmer_id, end_date, starting_price, min_increment, description):
        """Create a new auction"""
        auction = {
            'product_id': product_id,
            'farmer_id': farmer_id,
            'start_date': datetime.now(),
            'end_date': end_date,
            'starting_price': float(starting_price),
            'current_price': float(starting_price),
            'min_increment': float(min_increment),
            'description': description,
            'status': 'active',  # active, completed, cancelled
            'bids': [],
            'created_at': datetime.now()
        }
        
        return db.auctions.insert_one(auction)
    
    @staticmethod
    def find_by_id(auction_id):
        """Find an auction by ID"""
        return db.auctions.find_one({'_id': ObjectId(auction_id)})
    
    @staticmethod
    def find_by_farmer(farmer_id):
        """Find auctions by farmer ID"""
        return list(db.auctions.find({'farmer_id': farmer_id}).sort('created_at', -1))
    
    @staticmethod
    def find_active():
        """Find all active auctions"""
        return list(db.auctions.find({
            'end_date': {'$gt': datetime.now()},
            'status': 'active'
        }).sort('end_date', 1))
    
    @staticmethod
    def add_bid(auction_id, buyer_id, buyer_name, amount):
        """Add a bid to an auction"""
        bid = {
            'buyer_id': buyer_id,
            'buyer_name': buyer_name,
            'amount': float(amount),
            'timestamp': datetime.now()
        }
        
        return db.auctions.update_one(
            {'_id': ObjectId(auction_id)},
            {
                '$push': {'bids': bid},
                '$set': {'current_price': float(amount)}
            }
        )
    
    @staticmethod
    def update_status(auction_id, status, contract_id=None):
        """Update auction status"""
        update_data = {'status': status}
        if contract_id:
            update_data['contract_id'] = contract_id
            
        return db.auctions.update_one(
            {'_id': ObjectId(auction_id)},
            {'$set': update_data}
        )