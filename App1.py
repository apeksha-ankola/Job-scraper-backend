from flask import Flask, request, jsonify, session, send_file
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
from flask_session import Session
from jobs import get_jobs
from internships import get_internships
from llm import generate_cover_letter, generate_resume
import os
from dotenv import load_dotenv
import secrets

#All imports present in requirements.txt

load_dotenv()

app = Flask(__name__)

# Generate a secure secret key
app.secret_key = secrets.token_hex(32)

# Configure session management
app.config['SESSION_TYPE'] = 'filesystem'  # Can also use 'redis' for scalability
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  # Cryptographically sign the cookies
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session

# Initialize Flask-Session
Session(app)

# Configure CORS with credentials support
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# MongoDB setup
url = os.getenv("MONGO_URL")
client = MongoClient(url, server_api=ServerApi('1'))
db = client["jobscraperdb"]

try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection error: {e}")

@app.post("/signup")
def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    location = data.get("location")
    phone = int(data.get("phone"))

    # Validate required fields
    if not all([name, email, username, password, location, phone]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    # Check for unique email and username
    if db.users.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already exists"}), 409
    if db.users.find_one({"username": username}):
        return jsonify({"success": False, "message": "Username already exists"}), 409

    # Insert the new user into the database
    new_user = {
        "name": name,
        "email": email,
        "username": username,
        "password": password,  # Note: In production, hash the password!
        "location": location,
        "phone": phone
    }
    db.users.insert_one(new_user)

    # Create a secure session
    session['username'] = username
    session['logged_in'] = True

    return jsonify({
        "success": True, 
        "message": "Signup successful", 
        "username": username
    }), 201

@app.post("/login")
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    # Check if the username exists in the database
    user = db.users.find_one({"username": username})  
    
    if not user:
        return jsonify({"success": False, "message": "Incorrect username or password"}), 401
    
    # Validate the password
    if user["password"] != password:
        return jsonify({"success": False, "message": "Incorrect username or password"}), 401
    
    # Create a secure session
    session['username'] = username
    session['logged_in'] = True

    return jsonify({
        "success": True, 
        "message": "Login successful", 
        "username": username
    }), 200

@app.get("/logout")
def logout():
    # Clear the session
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

@app.get("/check-auth")
def check_auth():
    # Check if the user is logged in
    if session.get('logged_in'):
        return jsonify({
            "success": True, 
            "username": session.get('username')
        }), 200
    return jsonify({"success": False}), 401

# Rest of the routes remain the same...

if __name__ == "__main__":
    app.run(debug=True)