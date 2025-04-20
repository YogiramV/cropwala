from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson import ObjectId
from datetime import datetime, timedelta
from models import db

auction = Blueprint('auction', __name__)

@auction.route('/create_auction/<product_id>', methods=['GET', 'POST'])
def create_auction(product_id):
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('auth.login'))
    
    product = db.products.find_one({'_id': ObjectId(product_id)})
    
    if request.method == 'POST':
        start_date = datetime.now()
        end_date_str = request.form.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
        starting_price = float(request.form.get('starting_price'))
        min_increment = float(request.form.get('min_increment'))
        description = request.form.get('description')
        
        auction = {
            'product_id': product_id,
            'farmer_id': session['user_id'],
            'start_date': start_date,
            'end_date': end_date,
            'starting_price': starting_price,
            'current_price': starting_price,
            'min_increment': min_increment,
            'description': description,
            'status': 'active',
            'bids': [],
            'created_at': datetime.now()
        }
        
        result = db.auctions.insert_one(auction)
        
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'status': 'in_auction'}}
        )
        
        flash('Auction created successfully!')
        return redirect(url_for('farmer.farmer_dashboard'))
    
    return render_template('auction/create_auction.html', product=product)

@auction.route('/auction/<auction_id>')
def view_auction(auction_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    auction = db.auctions.find_one({'_id': ObjectId(auction_id)})
    product = db.products.find_one({'_id': ObjectId(auction['product_id'])})
    farmer = db.users.find_one({'_id': ObjectId(auction['farmer_id'])})
    
    if auction['end_date'] < datetime.now() and auction['status'] == 'active':
        if len(auction['bids']) > 0:
            winning_bid = auction['bids'][-1]
            
            contract = {
                'product_id': str(product['_id']),
                'farmer_id': auction['farmer_id'],
                'buyer_id': winning_bid['buyer_id'],
                'quantity': product['quantity'],
                'total_price': winning_bid['amount'],
                'delivery_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'payment_method': 'Cash on Delivery',
                'terms': f"Auction contract for {product['name']}",
                'status': 'pending',
                'created_at': datetime.now()
            }
            
            result = db.contracts.insert_one(contract)
            contract_id = str(result.inserted_id)
            
            db.auctions.update_one(
                {'_id': ObjectId(auction_id)},
                {'$set': {
                    'status': 'completed',
                    'contract_id': contract_id
                }}
            )
            
            db.products.update_one(
                {'_id': ObjectId(product['_id'])},
                {'$set': {'status': 'pending_contract'}}
            )
            
            notification = {
                'user_id': winning_bid['buyer_id'],
                'type': 'auction_won',
                'content': f"You have won the auction for {product['name']}!",
                'read': False,
                'contract_id': contract_id,
                'created_at': datetime.now()
            }
            db.notifications.insert_one(notification)
            
            auction['status'] = 'completed'
            auction['contract_id'] = contract_id
        else:
            db.auctions.update_one(
                {'_id': ObjectId(auction_id)},
                {'$set': {'status': 'completed'}}
            )
            
            db.products.update_one(
                {'_id': ObjectId(product['_id'])},
                {'$set': {'status': 'available'}}
            )
            
            auction['status'] = 'completed'
    
    return render_template('auction/bid_auction.html', 
                         auction=auction, 
                         product=product, 
                         farmer=farmer)

@auction.route('/place_bid/<auction_id>', methods=['POST'])
def place_bid(auction_id):
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('auth.login'))
    
    auction = db.auctions.find_one({'_id': ObjectId(auction_id)})
    
    if auction['status'] != 'active' or auction['end_date'] < datetime.now():
        flash('This auction has ended.')
        return redirect(url_for('auction.view_auction', auction_id=auction_id))
    
    bid_amount = float(request.form.get('bid_amount'))
    
    if bid_amount <= auction['current_price']:
        flash(f'Bid must be higher than current price (${auction["current_price"]})')
        return redirect(url_for('auction.view_auction', auction_id=auction_id))
    
    if bid_amount < auction['current_price'] + auction['min_increment']:
        flash(f'Bid must be at least ${auction["min_increment"]} higher than current price')
        return redirect(url_for('auction.view_auction', auction_id=auction_id))
    
    bid = {
        'buyer_id': session['user_id'],
        'buyer_name': session['name'],
        'amount': bid_amount,
        'timestamp': datetime.now()
    }
    
    db.auctions.update_one(
        {'_id': ObjectId(auction_id)},
        {
            '$push': {'bids': bid},
            '$set': {'current_price': bid_amount}
        }
    )
    
    notification = {
        'user_id': auction['farmer_id'],
        'type': 'new_bid',
        'content': f"A new bid of ${bid_amount} has been placed on your auction.",
        'read': False,
        'auction_id': auction_id,
        'created_at': datetime.now()
    }
    db.notifications.insert_one(notification)
    
    flash('Bid placed successfully!')
    return redirect(url_for('auction.view_auction', auction_id=auction_id))