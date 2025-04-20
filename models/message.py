# models/message.py
from datetime import datetime
from bson import ObjectId
from models import db

class Message:
    @staticmethod
    def create(sender_id, recipient_id, content, product_id=None):
        """Create a new message"""
        message = {
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'content': content,
            'product_id': product_id,
            'read': False,
            'created_at': datetime.now()
        }
        
        return db.messages.insert_one(message)
    
    @staticmethod
    def find_conversation(user1_id, user2_id):
        """Find conversation between two users"""
        return list(db.messages.find({
            '$or': [
                {'sender_id': user1_id, 'recipient_id': user2_id},
                {'sender_id': user2_id, 'recipient_id': user1_id}
            ]
        }).sort('created_at', 1))
    
    @staticmethod
    def find_product_conversation(user1_id, user2_id, product_id):
        """Find conversation about a specific product"""
        return list(db.messages.find({
            'product_id': product_id,
            '$or': [
                {'sender_id': user1_id, 'recipient_id': user2_id},
                {'sender_id': user2_id, 'recipient_id': user1_id}
            ]
        }).sort('created_at', 1))
    
    @staticmethod
    def mark_as_read(recipient_id, sender_id=None):
        """Mark messages as read"""
        query = {'recipient_id': recipient_id, 'read': False}
        if sender_id:
            query['sender_id'] = sender_id
            
        return db.messages.update_many(
            query,
            {'$set': {'read': True}}
        )
    
    @staticmethod
    def count_unread(user_id):
        """Count unread messages for a user"""
        return db.messages.count_documents({
            'recipient_id': user_id,
            'read': False
        })
    
    @staticmethod
    def get_conversations(user_id):
        """Get all conversations for a user"""
        return db.messages.aggregate([
            {'$match': {'$or': [
                {'sender_id': user_id},
                {'recipient_id': user_id}
            ]}},
            {'$sort': {'created_at': -1}},
            {'$group': {
                '_id': {
                    '$cond': [
                        {'$eq': ['$sender_id', user_id]},
                        '$recipient_id',
                        '$sender_id'
                    ]
                },
                'last_message': {'$first': '$$ROOT'}
            }}
        ])