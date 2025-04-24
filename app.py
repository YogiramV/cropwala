from flask import Flask, jsonify, render_template, request, redirect, send_from_directory, url_for, flash, session
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
import google.generativeai as genai
import json
import random
import logging
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

#Get Gemini Api key
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

#Inintialize the gemini client 
model = genai.GenerativeModel('gemini-2.0-flash')

# System prompt for the chatbot
system_prompt = """
You are FarmHelper, a friendly, expert virtual farming assistant.
You know everything about agriculture: crop care, fertilizers, NPK values, water needs, pests, soil health, and weather impact.
Respond in the language the user speaks.
Keep your responses structured in short bullet points for easy reading (but not always).
Begin your messages with a friendly farmer emoji 👨‍🌾 to set the tone.
Tailor your advice to the user's specific growing zone and climate when available.
Provide practical, actionable advice that farmers can implement immediately.
For pest issues, always suggest both organic and conventional solutions.
For soil health questions, emphasize sustainable practices.
If the user sends an image, analyze it for plant health, disease, or pest issues.
If uncertain about specific details, acknowledge limitations but provide general best practices.
"""

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.assured_contract_farming

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store conversation history
conversation_history = {}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Chatbot routes and its subroutes

#

@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")

# Route for handling chat messages
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "").strip()
        session_id = data.get("session_id", "default_session")
        user_location = data.get("location", "default")
        language = data.get("language", "en")

        logger.info(f"Received message from {session_id}: {user_message}")

        # Initialize conversation history for new session
        if session_id not in conversation_history:
            conversation_history[session_id] = [
                {"role": "system", "content": system_prompt}
            ]

        # Append user message to conversation history
        conversation_history[session_id].append({
            "role": "user",
            "content": user_message
        })

        # Prepare context with location
        context = f"User location: {user_location}\nUser language: {language}\n"
        
        # Create prompt for Gemini API
        full_prompt = f"{system_prompt}\n\n{context}\nUser message: {user_message}"

        # Generate response using Gemini API
        try:
            response = model.generate_content(full_prompt)
            bot_response = response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            bot_response = "👨‍🌾 Sorry, I'm having trouble processing your request. Please try again or ask something else."

        # Append bot response to conversation history
        conversation_history[session_id].append({
            "role": "assistant",
            "content": bot_response
        })

        # Keep only the last 10 messages to manage memory
        if len(conversation_history[session_id]) > 10:
            conversation_history[session_id] = conversation_history[session_id][-10:]

        # Generate suggestion chips using Gemini
        suggestions = generate_suggestions(user_message)

        return jsonify({
            "response": bot_response,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "response": "👨‍🌾 An error occurred. Please try again.",
            "suggestions": [],
            "timestamp": datetime.now().isoformat()
        }), 500

# Helper function to generate suggestion chips using Gemini instead of hardcoded values
def generate_suggestions(user_message):
    try:
        suggestion_prompt = f"""
        Based on this user message about farming: "{user_message}"
        Generate exactly 3 follow-up question suggestions related to farming, agriculture, or gardening.
        Each suggestion should be brief (under 7 words if possible) and practical.
        Format your response as a plain list of 3 items, one per line, no bullets or numbers.
        If the user message doesn't contain enough context, provide general farming-related suggestions.
        """
        
        response = model.generate_content(suggestion_prompt)
        suggestions_text = response.text.strip()
        
        # Split the response into individual suggestions
        suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
        
        # Ensure we have 3 suggestions at most
        suggestions = suggestions[:3]
        
        # If somehow we got no suggestions, use some defaults
        if not suggestions:
            suggestions = [
                "Best planting times",
                "Natural pest control",
                "Soil health tips"
            ]
            
        return suggestions
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        return [
            "Best planting times",
            "Natural pest control",
            "Soil health tips"
        ]

# Route for handling image uploads and analysis
@app.route("/analyze_image", methods=["POST"])
def analyze_image():
    try:
        if 'file' not in request.files:
            logger.error("No file provided in image analysis request")
            return jsonify({
                "response": "👨‍🌾 Please upload an image.",
                "analysis": []
            }), 400

        file = request.files['file']
        session_id = request.form.get("session_id", "default_session")
        user_location = request.form.get("location", "default")

        if file and allowed_file(file.filename):
            # Securely save the file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            # Read image file for Gemini API
            with open(file_path, "rb") as image_file:
                image_data = image_file.read()

            # Prepare prompt for image analysis
            analysis_prompt = f"""
            Analyze this plant image for health, diseases, or pest issues.
            User location: {user_location}
            Provide a structured response with:
            - Plant identification
            - Health status
            - Identified issues (if any)
            - Recommendations (both organic and conventional)
            Respond in a friendly tone with the 👨‍🌾 emoji.
            """

            try:
                # Send image and prompt to Gemini API
                response = model.generate_content([analysis_prompt, {"mime_type": file.mimetype, "data": image_data}])
                analysis_result = response.text.strip()

                # Clean up the saved file
                os.remove(file_path)

                # Append to conversation history
                if session_id not in conversation_history:
                    conversation_history[session_id] = [
                        {"role": "system", "content": system_prompt}
                    ]
                conversation_history[session_id].append({
                    "role": "user",
                    "content": "Image upload for plant analysis"
                })
                conversation_history[session_id].append({
                    "role": "assistant",
                    "content": analysis_result
                })

                return jsonify({
                    "response": analysis_result,
                    "analysis": analysis_result.split("\n"),
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"Gemini API error in image analysis: {str(e)}")
                os.remove(file_path)
                return jsonify({
                    "response": "👨‍🌾 Sorry, I couldn't analyze the image. Please try again.",
                    "analysis": [],
                    "timestamp": datetime.now().isoformat()
                }), 500

        else:
            logger.error("Invalid file type uploaded")
            return jsonify({
                "response": "👨‍🌾 Please upload a valid image file (PNG, JPG, JPEG).",
                "analysis": [],
                "timestamp": datetime.now().isoformat()
            }), 400

    except Exception as e:
        logger.error(f"Error in image analysis endpoint: {str(e)}")
        return jsonify({
            "response": "👨‍🌾 An error occurred. Please try again.",
            "analysis": [],
            "timestamp": datetime.now().isoformat()
        }), 500

# Route for handling location-based recommendations
@app.route("/location_recommendations", methods=["POST"])
def location_recommendations():
    try:
        data = request.json
        session_id = data.get("session_id", "default_session")
        user_location = data.get("location", "default")
        language = data.get("language", "en")

        logger.info(f"Location recommendation request from {session_id} for {user_location}")

        prompt = f"""
        Provide farming recommendations based on the following:
        - Location: {user_location}
        
        Consider typical weather patterns, soil conditions, and agricultural practices for this location.
        
        Suggest:
        - Suitable crops for the current season (it's currently {datetime.now().strftime('%B')}, so focus on seasonal crops)
        - Weather-specific farming tips relevant to this location
        - Potential pest or disease concerns for this region
        - Local agricultural best practices
        
        Respond in a friendly tone with the 👨‍🌾 emoji.
        Use {language} language for your response.
        """

        try:
            response = model.generate_content(prompt)
            recommendations = response.text.strip()

            # Append to conversation history
            if session_id not in conversation_history:
                conversation_history[session_id] = [
                    {"role": "system", "content": system_prompt}
                ]
            conversation_history[session_id].append({
                "role": "user",
                "content": f"Location-based recommendations for {user_location}"
            })
            conversation_history[session_id].append({
                "role": "assistant",
                "content": recommendations
            })

            return jsonify({
                "response": recommendations,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Gemini API error in location recommendations: {str(e)}")
            return jsonify({
                "response": "👨‍🌾 Sorry, I couldn't generate recommendations. Please try again.",
                "timestamp": datetime.now().isoformat()
            }), 500

    except Exception as e:
        logger.error(f"Error in location recommendations endpoint: {str(e)}")
        return jsonify({
            "response": "👨‍🌾 An error occurred. Please try again.",
            "timestamp": datetime.now().isoformat()
        }), 500

# Route for serving uploaded files (if needed)
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
# Harishwa - FAQ , About-US

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/FAQ")
def FAQ():
    return render_template('FAQ.html')


if __name__ == '__main__':
    app.run(debug=True)