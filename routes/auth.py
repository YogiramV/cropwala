from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import bcrypt
from bson import ObjectId
from models import db
from datetime import datetime
auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return render_template('base.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        user = db.users.find_one({'email': email})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            if user['user_type'] == user_type:
                session['user_id'] = str(user['_id'])
                session['user_type'] = user['user_type']
                session['name'] = user['name']
                
                if user_type == 'farmer':
                    return redirect(url_for('farmer.farmer_dashboard'))
                else:
                    return redirect(url_for('buyer.buyer_dashboard'))
            else:
                flash('Invalid user type')
        else:
            flash('Invalid email or password')
    
    return render_template('auth/login.html')

@auth.route('/register/farmer', methods=['GET', 'POST'])
def register_farmer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        farmer_id = request.form.get('farmer_id')
        location = request.form.get('location')
        phone = request.form.get('phone')
        
        if db.users.find_one({'farmer_id': farmer_id}) or db.users.find_one({'email': email}):
            flash('Farmer ID or Email already exists')
            return redirect(url_for('auth.register_farmer'))
        
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
        
        db.users.insert_one(user)
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_farmer.html')

@auth.route('/register/buyer', methods=['GET', 'POST'])
def register_buyer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        company = request.form.get('company')
        location = request.form.get('location')
        phone = request.form.get('phone')
        
        if db.users.find_one({'email': email}):
            flash('Email already exists')
            return redirect(url_for('auth.register_buyer'))
        
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
        
        db.users.insert_one(user)
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_buyer.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))