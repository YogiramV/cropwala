from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson import ObjectId
from datetime import datetime
from models import db

buyer = Blueprint('buyer', __name__)

@buyer.route('/dashboard')
def buyer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('auth.login'))
    
    products = list(db.products.find({'status': 'available'}))
    for product in products:
        farmer = db.users.find_one({'_id': ObjectId(product['farmer_id'])})
        product['farmer_name'] = farmer['name'] if farmer else 'Unknown Farmer'
    
    auctions = list(db.auctions.find({
        'end_date': {'$gt': datetime.now()},
        'status': 'active'
    }))
    
    unread_count = db.messages.count_documents({
        'recipient_id': session['user_id'],
        'read': False
    })
    
    return render_template('buyer/dashboard.html', products=products, auctions=auctions, unread_count=unread_count)

@buyer.route('/product/<product_id>')
def product_details(product_id):
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('auth.login'))
    
    product = db.products.find_one({'_id': ObjectId(product_id)})
    farmer = db.users.find_one({'_id': ObjectId(product['farmer_id'])})
    
    messages = list(db.messages.find({
        'product_id': product_id,
        '$or': [
            {'sender_id': session['user_id'], 'recipient_id': product['farmer_id']},
            {'sender_id': product['farmer_id'], 'recipient_id': session['user_id']}
        ]
    }).sort('created_at', 1))
    
    return render_template('buyer/product_details.html', product=product, farmer=farmer, messages=messages)

@buyer.route('/profile', methods=['GET', 'POST'])
def buyer_profile():
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('auth.login'))
    
    buyer = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if request.method == 'POST':
        name = request.form.get('name')
        company = request.form.get('company')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {
                'name': name,
                'company': company,
                'phone': phone,
                'location': location
            }}
        )
        session['name'] = name
        flash('Profile updated successfully!')
        return redirect(url_for('buyer.buyer_profile'))
    
    return render_template('buyer/profile.html', buyer=buyer)

@buyer.route('/messages')
def buyer_messages():
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('auth.login'))
    
    db.messages.update_many(
        {'recipient_id': session['user_id'], 'read': False},
        {'$set': {'read': True}}
    )
    
    conversations = db.messages.aggregate([
        {'$match': {'$or': [
            {'sender_id': session['user_id']},
            {'recipient_id': session['user_id']}
        ]}},
        {'$sort': {'created_at': -1}},
        {'$group': {
            '_id': {
                '$cond': [
                    {'$eq': ['$sender_id', session['user_id']]},
                    '$recipient_id',
                    '$sender_id'
                ]
            },
            'last_message': {'$first': '$$ROOT'}
        }}
    ])
    
    conversation_list = []
    for conv in conversations:
        other_user_id = conv['_id']
        other_user = db.users.find_one({'_id': ObjectId(other_user_id)})
        
        if other_user:
            conversation_list.append({
                'user_id': str(other_user['_id']),
                'name': other_user['name'],
                'user_type': other_user['user_type'],
                'last_message': conv['last_message']['content'],
                'timestamp': conv['last_message']['created_at']
            })
    
    return render_template('buyer/messages.html', conversations=conversation_list)