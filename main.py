from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "2aa0d190fe0e2510c3727c46da5f3e31"  # Required for session management

# Initialize Firebase Admin SDK
cred = credentials.Certificate("constructflow-947b1-firebase-adminsdk-fbsvc-2cf40bc4c7.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=["POST"])
def signup():
    id_token = request.form.get("id_token")
    user_type = request.form.get("user_type")  # "admin" or "user"

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token['email']

        print("Decoded Token:", decoded_token)  # Log the decoded token
        print("User Type:", user_type)  # Log the user type

        # Check if user already exists in Firestore
        user_ref = db.collection("users").document(uid)
        if user_ref.get().exists:
            return "User already exists", 400

        # Add user to Firestore with role
        user_ref.set({
            "email": email,
            "role": user_type  # "admin" or "user"
        })

        print("User added to Firestore:", uid, email, user_type)  # Log Firestore update

        # Store user information in session
        session['user'] = {"uid": uid, "email": email, "role": user_type}

        return redirect(url_for("admin" if user_type == "admin" else "user_dashboard"))
    except Exception as e:
        print("Error:", str(e))  # Log the error
        return f"Error: {str(e)}", 401

@app.route('/login', methods=["POST"])
def login():
    id_token = request.form.get("id_token")
    user_type = request.form.get("user_type")  # "admin" or "user"

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token['email']

        print("Decoded Token:", decoded_token)  # Log the decoded token
        print("User Type:", user_type)  # Log the user type

        # Check user role in Firestore
        user_ref = db.collection("users").document(uid)
        user_data = user_ref.get()

        if not user_data.exists:
            print("User not found in Firestore")  # Log if user not found
            return "User not found in Firestore", 404

        role = user_data.to_dict().get("role")
        print("User Role:", role)  # Log the user role

        # Verify role
        if user_type == "admin" and role != "admin":
            print("Unauthorized: Admin access required")  # Log unauthorized access
            return "Unauthorized: Admin access required", 403

        # Store user information in session
        session['user'] = {"uid": uid, "email": email, "role": role}

        return redirect(url_for("admin" if role == "admin" else "user_dashboard"))
    except Exception as e:
        print("Error:", str(e))  # Log the error
        return f"Error: {str(e)}", 401

@app.route('/admin')
def admin():
    # Check if the user is logged in and is an admin
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('index'))
    return render_template("admin.html")

@app.route('/admin/add-user', methods=["POST"])
def add_user():
    # Check if the user is logged in and is an admin
    if 'user' not in session or session['user']['role'] != 'admin':
        return "Unauthorized", 403

    email = request.form.get("email")
    password = "defaultPassword123"  # Set a default password (you can customize this)

    try:
        # Create the user in Firebase Authentication
        user = auth.create_user(email=email, password=password)

        # Add the user to Firestore with role "user"
        db.collection("users").document(user.uid).set({
            "email": email,
            "role": "user"
        })

        return f"User created: {email}", 200
    except Exception as e:
        print("Error:", str(e))  # Log the error
        return f"Error: {str(e)}", 400

@app.route('/user-dashboard')
def user_dashboard():
    # Check if the user is logged in
    if 'user' not in session or session['user']['role'] != 'user':
        return redirect(url_for('index'))
    return render_template("upload.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)