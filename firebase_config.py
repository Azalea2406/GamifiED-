import pyrebase

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

