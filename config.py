# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'assured_contract_farming_secret_key'
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = "assured_contract_farming"