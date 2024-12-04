from flask import Flask, request, jsonify, session
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
from jobs import get_jobs
from internships import get_internships

app = Flask(__name__)
app.secret_key = "MY_SECRET_KEY"  
CORS(app)  # Enable Cross-Origin Resource Sharing for React frontend

# MongoDB setup
# client = MongoClient("mongodb://localhost:27017/")
# db = client["jobscraperdb"]

uri = ""    # URL here
client = MongoClient(uri, server_api=ServerApi('1'))
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
    location = data.get("location")
    phone = data.get("phone")

    # Validate required fields
    if not all([name, email, username, password, location,phone]):
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
        "password": password,
        "location": location,
        "phone": phone
    }
    db.users.insert_one(new_user)

    # Store username in session
    session["username"] = username

    return jsonify({"success": True, "message": "Signup successful", "username": username}), 201

@app.post("/login")
def login():
    # Get data from the frontend request
    data = request.json  # Expecting JSON input
    username = data.get("username")
    password = data.get("password")
    
    # Check if the username exists in the database
    user = db.users.find_one({"username": username})  
    
    if not user:
        return jsonify({"success": False, "message": "Incorrect username or password"}), 401
    
    # Validate the password
    if user["password"] != password:
        return jsonify({"success": False, "message": "Incorrect username or password"}), 401
    
    # Store username in session
    session["username"] = username
    return jsonify({"success": True, "message": "Login successful", "username": username}), 200

@app.get("/logout")
def logout():
    # Clear the session
    session.pop("username", None)
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

@app.get("/jobs")
def jobs():
    # Check if the user is logged in
    if "username" not in session:
        return jsonify({"success": False, "message": "Please login first"}), 401
    
    # Get the search query from request arguments
    search_query = request.args.get("search")
    
    # Call the get_jobs function and return the results
    jobs_list = get_jobs(search_query)
    
    return jsonify({"success": True, "jobs": jobs_list}), 200

@app.get("/internships")
def internships():
    # Check if the user is logged in
    if "username" not in session:
        return jsonify({"success": False, "message": "Please login first"}), 401
    
    # Get the search query from request arguments
    search_query = request.args.get("search")
    
    # Call the get_jobs function and return the results
    jobs_list = get_internships(search_query)
    
    return jsonify({"success": True, "jobs": jobs_list}), 200

if __name__ == "__main__":
    app.run(debug=True)
