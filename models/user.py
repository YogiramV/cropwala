# models/user.py
from datetime import datetime
from bson import ObjectId
import bcrypt
from models import db

class User:
    @staticmethod
    def create_farmer(name, email, password, farmer_id, location, phone):
        """Create a new farmer user"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'user_type': 'farmer',
            'farmer_id': farmer_id,
            'location': location,
            'phone': phone,
            'created_at': datetime.now()
        }
        
        return db.users.insert_one(user)
    
    @staticmethod
    def create_buyer(name, email, password, company, location, phone):
        """Create a new buyer user"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'user_type': 'buyer',
            'company': company,
            'location': location,
            'phone': phone,
            'created_at': datetime.now()
        }
        
        return db.users.insert_one(user)
    
    @staticmethod
    def find_by_email(email):
        """Find a user by email"""
        return db.users.find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        """Find a user by ID"""
        return db.users.find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def find_by_farmer_id(farmer_id):
        """Find a farmer by farmer ID"""
        return db.users.find_one({'farmer_id': farmer_id})
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user data"""
        return db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify if provided password matches stored hash"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)