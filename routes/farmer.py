from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from bson import ObjectId
from datetime import datetime
from werkzeug.utils import secure_filename
from models import db
from utils import allowed_file
import os

farmer = Blueprint('farmer', __name__)

@farmer.route('/dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('auth.login'))
    
    products = list(db.products.find({'farmer_id': session['user_id']}))
    
    unread_count = db.messages.count_documents({
        'recipient_id': session['user_id'],
        'read': False
    })
    
    return render_template('farmer/dashboard.html', products=products, unread_count=unread_count)

@farmer.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        quantity = float(request.form.get('quantity'))
        unit = request.form.get('unit')
        price = float(request.form.get('price'))
        harvest_date = request.form.get('harvest_date')
        
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
        
        product = {
            'name': name,
            'description': description,
            'category': category,
            'quantity': quantity,
            'unit': unit,
            'price': price,
            'image': image_filename,
            'harvest_date': harvest_date,
            'farmer_id': session['user_id'],
            'created_at': datetime.now(),
            'status': 'available'
        }
        
        db.products.insert_one(product)
        flash('Product added successfully!')
        return redirect(url_for('farmer.farmer_dashboard'))
    
    return render_template('farmer/add_product.html')

@farmer.route('/profile', methods=['GET', 'POST'])
def farmer_profile():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('auth.login'))
    
    farmer = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {
                'name': name,
                'phone': phone,
                'location': location
            }}
        )
        session['name'] = name
        flash('Profile updated successfully!')
        return redirect(url_for('farmer.farmer_profile'))
    
    return render_template('farmer/profile.html', farmer=farmer)

@farmer.route('/messages')
def farmer_messages():
    if 'user_id' not in session or session['user_type'] != 'farmer':
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
    
    return render_template('farmer/messages.html', conversations=conversation_list)