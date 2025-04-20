from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson import ObjectId
from datetime import datetime
from models import db

messaging = Blueprint('messaging', __name__)

@messaging.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content')
    product_id = request.form.get('product_id', None)
    
    message = {
        'sender_id': session['user_id'],
        'recipient_id': recipient_id,
        'content': content,
        'product_id': product_id,
        'read': False,
        'created_at': datetime.now()
    }
    
    db.messages.insert_one(message)
    
    if product_id:
        return redirect(url_for('buyer.product_details', product_id=product_id))
    else:
        if session['user_type'] == 'farmer':
            return redirect(url_for('farmer.farmer_messages'))
        else:
            return redirect(url_for('buyer.buyer_messages'))

@messaging.route('/conversation/<user_id>')
def conversation(user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    other_user = db.users.find_one({'_id': ObjectId(user_id)})
    
    db.messages.update_many(
        {'sender_id': user_id, 'recipient_id': session['user_id'], 'read': False},
        {'$set': {'read': True}}
    )
    
    messages = list(db.messages.find({
        '$or': [
            {'sender_id': session['user_id'], 'recipient_id': user_id},
            {'sender_id': user_id, 'recipient_id': session['user_id']}
        ]
    }).sort('created_at', 1))
    
    return render_template('messaging/conversation.html', messages=messages, other_user=other_user, current_date=datetime.now())