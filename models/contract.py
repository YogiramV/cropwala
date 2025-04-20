# models/contract.py
from datetime import datetime
from bson import ObjectId
from models import db

class Contract:
    @staticmethod
    def create(product_id, farmer_id, buyer_id, quantity, total_price, delivery_date, payment_method, terms):
        """Create a new contract"""
        contract = {
            'product_id': product_id,
            'farmer_id': farmer_id,
            'buyer_id': buyer_id,
            'quantity': float(quantity),
            'total_price': float(total_price),
            'delivery_date': delivery_date,
            'payment_method': payment_method,
            'terms': terms,
            'status': 'pending',  # pending, approved, completed, cancelled
            'created_at': datetime.now()
        }
        
        return db.contracts.insert_one(contract)
    
    @staticmethod
    def find_by_id(contract_id):
        """Find a contract by ID"""
        return db.contracts.find_one({'_id': ObjectId(contract_id)})
    
    @staticmethod
    def find_by_farmer(farmer_id):
        """Find contracts by farmer ID"""
        return list(db.contracts.find({'farmer_id': farmer_id}).sort('created_at', -1))
    
    @staticmethod
    def find_by_buyer(buyer_id):
        """Find contracts by buyer ID"""
        return list(db.contracts.find({'buyer_id': buyer_id}).sort('created_at', -1))
    
    @staticmethod
    def update_status(contract_id, status):
        """Update contract status"""
        return db.contracts.update_one(
            {'_id': ObjectId(contract_id)},
            {'$set': {'status': status}}
        )