

# Assured Contract Farming System

## Overview  
The Assured Contract Farming System is a web-based platform designed to connect farmers and buyers in a trusted contract farming ecosystem. Built using Flask and MongoDB, the application facilitates product listings, auctions, contract negotiations, messaging, and notifications, fostering sustainable agricultural trade. The system supports two primary user roles—farmers and buyers—each with tailored dashboards and functionalities to streamline the contract farming process.

## Project Purpose  
The platform aims to:

- Enable farmers to list agricultural products and create auctions.  
- Allow buyers to browse products, place bids, and request contracts.  
- Provide secure communication and contract management between parties.  
- Deliver real-time notifications for key activities like bids, contracts, and messages.  
- Promote transparency and trust in agricultural transactions.

## System Architecture  
The application follows a modular, Blueprint-based Flask architecture with a MongoDB backend. Key components include:

### Backend  

- **Flask Framework**: Handles routing, request processing, and template rendering.  
- **MongoDB**: Stores user data, products, auctions, contracts, messages, and notifications. Collections include `users`, `products`, `auctions`, `contracts`, `messages`, and `notifications`.  
- **Blueprints**: Organizes routes into modular components for authentication (`auth`), farmer functionalities (`farmer`), buyer functionalities (`buyer`), messaging (`messaging`), and auctions (`auction`).  
- **Utilities**: A separate utility module manages shared functions, such as file upload validation.

### Frontend  

- **Jinja2 Templates**: Dynamic HTML templates for rendering pages like dashboards, product listings, and forms.  
- **CSS with Font Awesome**: Provides a modern, responsive UI with icons for enhanced user experience.  
- **JavaScript**: Adds interactivity, such as form validation, flash message auto-hiding, and responsive navigation.

## File Structure  

- **Root**: Contains the main application file (`app.py`), utility module (`utils.py`), and configuration files (e.g., `requirements.txt`, `.env`).  
- **routes/**: Houses Blueprint modules (`auth.py`, `farmer.py`, `buyer.py`, `messaging.py`, `auction.py`) for route definitions.  
- **templates/**: Stores Jinja2 templates, organized by feature (e.g., `auth/`, `farmer/`, `contract/`).  
- **static/**: Includes CSS (`css/style.css`), JavaScript (`js/main.js`), and uploaded files (`uploads/` for product images).  
- **models/**: Defines database interaction logic (assumed to handle MongoDB connections).

## Features  

### Authentication  

- **User Registration**: Separate registration flows for farmers and buyers, capturing details like name, email, password, and location. Passwords are hashed for security.  
- **Login/Logout**: Secure session-based authentication with redirects to role-specific dashboards.  
- **Profile Management**: Users can update personal details (name, phone, location).

### Farmer Functionalities  

- **Dashboard**: Displays the farmer’s listed products and unread message count.  
- **Product Management**: Farmers can add products with details (name, description, quantity, price, image) and manage their status (e.g., available, in auction).  
- **Messages**: View and respond to buyer messages in a conversation-based interface.  
- **Auctions**: Create auctions for products, specifying start price, minimum bid increment, and end date.  
- **Contract Management**: Approve or view contracts initiated by buyers.

### Buyer Functionalities  

- **Dashboard**: Lists available products and active auctions with options to view details or bid.  
- **Product Details**: View product information and initiate contract requests or send messages to farmers.  
- **Messages**: Communicate with farmers in a conversation-based interface.  
- **Bidding**: Place bids on active auctions with validation for minimum increments.  
- **Contract Requests**: Submit contract proposals with quantity, price, and delivery terms.

### Messaging  

- **Conversation Interface**: Users can send and receive messages, grouped by conversation partner.  
- **Read Status**: Messages are marked as read when viewed, with unread counts displayed on dashboards.

### Auctions  

- **Creation**: Farmers create auctions with product details, start price, and end date.  
- **Bidding**: Buyers place bids, with automatic validation for bid amount and auction status.  
- **Completion**: When an auction ends, the system creates a contract for the highest bidder (if any) or marks the product as available if no bids are placed.

### Contracts  

- **Creation**: Buyers initiate contracts via product details or auction wins, specifying quantity, price, delivery date, and terms.  
- **Approval**: Farmers approve or reject contracts, updating product status accordingly.  
- **Viewing**: Both parties can view contract details, with a placeholder for future download functionality.

### Notifications  

- **Real-Time Alerts**: Users receive notifications for events like new bids, contract requests, auction wins, and messages.  
- **Unified Interface**: Notifications are displayed in a dedicated page, marked as read when viewed.

### Additional Features  

- **File Uploads**: Supports image uploads for products with validation for file types (PNG, JPG, JPEG, GIF).  
- **Responsive Design**: The UI adapts to various screen sizes, with a mobile-friendly navigation menu.  
- **Theme Toggle**: Users can switch between light and dark themes.  
- **Language Selector**: Supports multiple languages (English, Hindi, Telugu, Tamil, Marathi) via a dropdown.  
- **Chatbot Placeholder**: A button links to a future chatbot feature (not yet implemented).

## Security Considerations  

- **Password Hashing**: User passwords are securely hashed using `bcrypt`.  
- **Session Management**: Flask’s session handling ensures secure user authentication.  
- **File Upload Validation**: Restricts uploads to safe file types and uses secure filenames.  
- **Environment Variables**: Sensitive data like MongoDB URI and secret key are stored in a `.env` file.

## Setup and Installation  

### Prerequisites  

- Python 3.8 or higher  
- MongoDB Atlas account (or local MongoDB instance)  
- Git (for cloning the repository)  
- pip (Python package manager)

### Steps to Start the Project  

**Clone the Repository:**

Clone the project to your local machine:

```bash
git clone <repository-url>
cd assured-contract-farming-system
```

**Set Up a Virtual Environment:**

Create and activate a Python virtual environment to isolate dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install Dependencies:**

Install the required Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:

- Flask: Web framework  
- pymongo: MongoDB driver  
- bcrypt: Password hashing  
- werkzeug: File upload utilities  
- python-dotenv: Environment variable management

**Configure Environment Variables:**

Create a `.env` file in the project root to store sensitive configuration:

```bash
echo "MONGO_URI=your_mongo_url" > .env
echo "FLASK_SECRET_KEY=assured_contract_farming_secret_key" >> .env
```

Replace `your_mongo_url` with your MongoDB connection string (e.g., from MongoDB Atlas).

The `MONGO_URI` connects to the MongoDB database, and `FLASK_SECRET_KEY` secures Flask sessions.

**Set Up MongoDB:**

Ensure your MongoDB instance is running and accessible via the `MONGO_URI`.  
The application uses a database named `assured_contract_farming` with collections for `users`, `products`, `auctions`, `contracts`, `messages`, and `notifications`.

**Run the Application:**

Start the Flask development server:

```bash
python app.py
```

The application will be available at `http://localhost:5000`.

**Access the Application:**

Open a web browser and navigate to `http://localhost:5000`.  
Register as a farmer or buyer to explore the platform’s features.

## Troubleshooting Setup  

- **MongoDB Connection Issues**: Verify the `MONGO_URI` is correct and your MongoDB instance is accessible. Check network settings or MongoDB Atlas whitelist.  
- **Dependency Errors**: Ensure all packages in `requirements.txt` are installed. Run `pip list` to verify.  
- **Port Conflicts**: If port 5000 is in use, Flask will fail to start. Change the port in `app.py` by adding `app.run(debug=True, port=5001)`.

## Usage  

- **Register/Login**: Create an account as a farmer or buyer, then log in to access role-specific dashboards.

**Farmers:**

- Add products via the "Add Product" page, including images and details.  
- Create auctions for products to attract bids.  
- Respond to messages and approve contracts.

**Buyers:**

- Browse products and auctions on the dashboard.  
- Place bids or request contracts for products.  
- Communicate with farmers via the messaging system.

- **Notifications**: Check the notifications page for updates on bids, contracts, and messages.  
- **Responsive UI**: Use the theme toggle and language selector for a personalized experience.

## Future Improvements  

- **Chatbot Integration**: Implement the chatbot feature linked in the UI.  
- **Contract Downloads**: Enable PDF generation and download for contracts.  
- **Advanced Search**: Add search and filter options for products and auctions.  
- **Analytics**: Provide dashboards with sales, bidding, and contract