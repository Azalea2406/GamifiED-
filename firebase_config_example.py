import pyrebase
firebaseConfig = {
    "apiKey": "your-api-key",
    "authDomain": "your-project-id.firebaseapp.com",
    "databaseURL": "https://your-project-id.firebaseio.com",
    "projectId": "your-project-id",
    "storageBucket": "your-project-id.appspot.com",
    "messagingSenderId": "your-messaging-sender-id",
    "appId": "your-app-id"
}
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
