from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta 
from bson import ObjectId
from pymongo import MongoClient
from routes.auth import auth
from routes.farmer import farmer
from routes.buyer import buyer
from routes.messaging import messaging
from routes.auction import auction
from utils import allowed_file
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.assured_contract_farming

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(farmer, url_prefix='/farmer')
app.register_blueprint(buyer, url_prefix='/buyer')
app.register_blueprint(messaging)
app.register_blueprint(auction)

# Contract routes
@app.route('/create_contract/<product_id>', methods=['GET', 'POST'])
def create_contract(product_id):
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('auth.login'))
    
    product = db.products.find_one({'_id': ObjectId(product_id)})
    farmer = db.users.find_one({'_id': ObjectId(product['farmer_id'])})
    buyer = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if request.method == 'POST':
        quantity = float(request.form.get('quantity'))
        total_price = float(request.form.get('total_price'))
        delivery_date = request.form.get('delivery_date')
        payment_method = request.form.get('payment_method')
        terms = request.form.get('terms')
        
        contract = {
            'product_id': product_id,
            'farmer_id': product['farmer_id'],
            'buyer_id': session['user_id'],
            'quantity': quantity,
            'total_price': total_price,
            'delivery_date': delivery_date,
            'payment_method': payment_method,
            'terms': terms,
            'status': 'pending',
            'created_at': datetime.now()
        }
        
        result = db.contracts.insert_one(contract)
        contract_id = str(result.inserted_id)
        
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'status': 'pending_contract'}}
        )
        
        notification = {
            'user_id': product['farmer_id'],
            'type': 'contract_request',
            'content': f"A buyer {buyer['name']} has requested a contract for your {product['name']}.",
            'read': False,
            'contract_id': contract_id,
            'created_at': datetime.now()
        }
        db.notifications.insert_one(notification)
        
        flash('Contract request sent successfully!')
        return redirect(url_for('view_contract', contract_id=contract_id))
    
    return render_template('contract/create_contract.html', product=product, farmer=farmer)

@app.route('/contract/<contract_id>')
def view_contract(contract_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    contract = db.contracts.find_one({'_id': ObjectId(contract_id)})
    product = db.products.find_one({'_id': ObjectId(contract['product_id'])})
    farmer = db.users.find_one({'_id': ObjectId(contract['farmer_id'])})
    buyer = db.users.find_one({'_id': ObjectId(contract['buyer_id'])})
    
    return render_template('contract/view_contract.html', 
                         contract=contract, 
                         product=product, 
                         farmer=farmer, 
                         buyer=buyer,
                         current_date = datetime.now())

@app.route('/approve_contract/<contract_id>')
def approve_contract(contract_id):
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('auth.login'))
    
    contract = db.contracts.find_one({'_id': ObjectId(contract_id)})
    
    if contract and contract['farmer_id'] == session['user_id']:
        db.contracts.update_one(
            {'_id': ObjectId(contract_id)},
            {'$set': {'status': 'approved'}}
        )
        
        db.products.update_one(
            {'_id': ObjectId(contract['product_id'])},
            {'$set': {'status': 'contracted'}}
        )
        
        notification = {
            'user_id': contract['buyer_id'],
            'type': 'contract_approved',
            'content': 'Your contract request has been approved by the farmer.',
            'read': False,
            'contract_id': contract_id,
            'created_at': datetime.now()
        }
        db.notifications.insert_one(notification)
        
        flash('Contract approved successfully!')
    else:
        flash('You are not authorized to approve this contract.')
    
    return redirect(url_for('view_contract', contract_id=contract_id))

@app.route('/download_contract/<contract_id>')
def download_contract(contract_id):
    flash('Contract download feature will be implemented soon.')
    return redirect(url_for('view_contract', contract_id=contract_id))

# Notification route
@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    notifications = list(db.notifications.find({
        'user_id': session['user_id'],
        'read': False
    }).sort('created_at', -1))
    
    db.notifications.update_many(
        {'user_id': session['user_id'], 'read': False},
        {'$set': {'read': True}}
    )
    
    return render_template('notifications.html', notifications=notifications, current_date=datetime.now())

if __name__ == '__main__':
    app.run(debug=True)