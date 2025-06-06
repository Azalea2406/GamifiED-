import pyrebase
import json

# Firebase configuration - Use your own project values
firebase_config = {
    "apiKey": "AIzaSyBAxO8ACbviAbFZEopMiW-MD5WZX17TE4c",
    "authDomain": "gamified-2064.firebaseapp.com",
    "databaseURL": "https://gamified-2064-default-rtdb.firebaseio.com", 
    "projectId": "gamified-2064",
    "storageBucket": "gamified-2064.firebasestorage.app",
    "messagingSenderId": "408735255781",
    "appId": "1:408735255781:web:fc9e41339a6feea8e1180c",
    "measurementId": "G-1JLQ89LZPC"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

def signup_user(email, password, role, username):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        user_id = user["localId"]
        
        user_data = {
            "email": email.strip(),
            "role": role.strip().lower(),
            "username": username.strip(),
            "uid": user_id  # Save UID explicitly
        }

        db.child("users").child(user_id).set(user_data)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": parse_error(e)}

def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_id = user["localId"]

        # Get stored user info
        user_data = db.child("users").child(user_id).get().val()

        # Return essential info inside user
        full_user = {
            "email": user_data.get("email", email),
            "username": user_data.get("username", "User"),
            "role": user_data.get("role", "learner").capitalize(),  # Capitalize for UI
            "uid": user_id
        }

        return {"success": True, "user": full_user}
    except Exception as e:
        return {"success": False, "error": parse_error(e)}

def send_reset_email(email):
    try:
        auth.send_password_reset_email(email)
        return {"status": "success", "message": f"Reset link sent to {email}"}
    except Exception as e:
        return {"status": "error", "message": parse_error(e)}

def parse_error(e):
    try:
        error_json = json.loads(e.args[1])
        return error_json["error"]["message"]
    except:
        return str(e)
