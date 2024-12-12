from flask import Flask, request, jsonify, session, send_file
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
from jobs import get_jobs, get_internships
from llm2 import generate_cover_letter, generate_resume
from bcrypt import hashpw, gensalt, checkpw

import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "MY_SECRET_KEY" 
#Modified by ayaj to allwo react app to access it 
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Allow all origins during development
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "withCredentials": True
    }
})  # Enable Cross-Origin Resource Sharing for React frontend


# MongoDB setup
# client = MongoClient("mongodb://localhost:27017/")
# db = client["jobscraperdb"]

 
url = os.getenv("MONGO_URL")
client = MongoClient(url, server_api=ServerApi('1'))
db = client["jobscraperdb"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.post("/signup")
def signup():
    # Get user data from the request
    data = request.json
    name = data.get("name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    #location = data.get("location")
    #phone = int(data.get("phone"))

    # Validate required fields
    if not all([name, email, username, password]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    # Check for unique email and username
    if db.users.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already exists"}), 409
    if db.users.find_one({"username": username}):
        return jsonify({"success": False, "message": "Username already exists"}), 409
    
    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    # Insert the new user into the database
    new_user = {
        "name": name,
        "email": email,
        "username": username,
        "password": hashed_password.decode('utf-8'),        
    }
    db.users.insert_one(new_user)
    print("Entry inserted of username -> ", username)
    # Store username in session
    session["username"] = username

    return jsonify({"success": True, "message": "Signup successful", "username": username}), 201

@app.post("/login")
def login():
    # Get data from the frontend request
    print("hey")
    data = request.json  # Expecting JSON input
    username = data.get("username")
    password = data.get("password")
    
    # Check if the username exists in the database
    user = db.users.find_one({"username": username})  
    
    if not user:
        return jsonify({"success": False, "message": "Incorrect username or password"}), 401
    
    # Validate the password
    if not checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return jsonify({"success": False, "message": "Incorrect password"}), 401
    
    # Store username in session
    session["username"] = username
    print(f"Session after login: {dict(session)}")
    print(f"Username stored in session: {session.get('username')}")
    return jsonify({"success": True, "message": "Login successful", "username": username}), 200

@app.get("/logout")
def logout():
    # Clear the session
    session.pop("username", None)
    print("Session after logout:", dict(session))
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

@app.get("/jobs")
def jobs():
    print(session)
    # Check if the user is logged in
    #if "username" not in session:
        #return jsonify({"success": False, "message": "Please login first"}), 401
    
    # Get the search query from request arguments
    search_query = request.args.get("search")
    print("Running Scrapping for Jobs..")
    # Call the get_jobs function and return the results
    jobs_list = get_jobs(search_query)
    
    return jsonify({"success": True, "jobs": jobs_list}), 200

@app.get("/internships")
def internships():
    # Check if the user is loggedin
    #if "username" not in session:
        #return jsonify({"success": False, "message": "Please login first"}), 401
    
    # Get the search query from request arguments
    search_query = request.args.get("search")
    
    # Call the get_jobs function and return the results
    jobs_list = get_internships(search_query)
    
    return jsonify({"success": True, "jobs": jobs_list}), 200

@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter_route():
    try:
        data = request.json
        name = data.get('name')
        company_name = data.get('company_name')
        job_position = data.get('job_position')

        if not all([name, company_name, job_position]):
            return jsonify({"error": "Missing required fields"}), 400

        pdf_path = generate_cover_letter(name, company_name, job_position)
        return send_file(pdf_path, as_attachment=False, download_name='cover-letter.pdf', mimetype='application/pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Resume API
@app.route('/generate-resume', methods=['POST'])
def generate_resume_route():
    try:
        data = request.json
        name = data.get('name')
        job_position = data.get('job_position')

        if not all([name, job_position]):
            return jsonify({"error": "Missing required fields"}), 400

        pdf_path = generate_resume(name, job_position)
        return send_file(pdf_path, as_attachment=False, download_name='resume.pdf', mimetype='application/pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/profile")
def update_profile():
    # Get data from the request body
    data = request.json
    username = data.get("username")
    phone = data.get("phone")
    github = data.get("github")
    linkedin = data.get("linkedin")
    location = data.get("location")

    # Validate required fields
    if not all([username, phone, github, linkedin, location]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    # Check if the user exists in the database
    user = db.users.find_one({"username": username})

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # Add or update the profile in the user's data
    profile = {
        "phone": phone,
        "github": github,
        "linkedin": linkedin,
        "location": location
    }

    # Update the user's document with the new profile
    db.users.update_one(
        {"username": username},
        {"$set": {"profile": profile}}
    )

    # Fetch the updated user document
    updated_user = db.users.find_one({"username": username}, {"_id": 0})

    return jsonify({"success": True, "message": "Profile updated successfully", "user": updated_user}), 200



if __name__ == "__main__":
    app.run(debug=True)
