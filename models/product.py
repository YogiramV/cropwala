# models/product.py
from datetime import datetime
from bson import ObjectId
from models import db

class Product:
    @staticmethod
    def create(name, description, category, quantity, unit, price, image, harvest_date, farmer_id):
        """Create a new product"""
        product = {
            'name': name,
            'description': description,
            'category': category,
            'quantity': float(quantity),
            'unit': unit,
            'price': float(price),
            'image': image,
            'harvest_date': harvest_date,
            'farmer_id': farmer_id,
            'created_at': datetime.now(),
            'status': 'available'  # available, contracted, sold, in_auction, pending_contract
        }
        
        return db.products.insert_one(product)
    
    @staticmethod
    def find_by_id(product_id):
        """Find a product by ID"""
        return db.products.find_one({'_id': ObjectId(product_id)})
    
    @staticmethod
    def find_by_farmer(farmer_id):
        """Find products by farmer ID"""
        return list(db.products.find({'farmer_id': farmer_id}))
    
    @staticmethod
    def find_available():
        """Find all available products"""
        return list(db.products.find({'status': 'available'}))
    
    @staticmethod
    def update(product_id, update_data):
        """Update product data"""
        return db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def update_status(product_id, status):
        """Update product status"""
        return db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'status': status}}
        )