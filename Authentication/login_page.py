import streamlit as st
from .auth import signup_user, login_user

def login_page():
    st.title("🔐 GamifiED Login")

    choice = st.radio("Choose an action:", ["Login", "Sign Up"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if choice == "Sign Up":
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("I am a:", ["Learner", "Instructor"])
        username = st.text_input("Choose a Username")

        if st.button("Create Account"):
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif email and password and username:
                result = signup_user(email, password, role.lower(), username)
                if result["success"]:
                    st.success("✅ Account created! Please log in.")
                else:
                    st.error(f"Error: {result['error']}")
            else:
                st.warning("Please fill all fields.")
    
    else:  # Login
        if st.button("Login"):
            if email and password:
                result = login_user(email, password)
                if result["success"]:
                    user_data = result["user"]

                    # Ensure all needed fields exist
                    st.session_state["user"] = {
                        "email": user_data.get("email", ""),
                        "uid": user_data.get("uid", ""),
                        "username": user_data.get("username", "User"),
                        "role": user_data.get("role", "Learner").capitalize(),  # Capitalized for routing
                    }
                    st.session_state["authenticated"] = True

                    st.success(f"Welcome back, {st.session_state['user']['username']}!")
                    st.balloons()
                    st.rerun()
                else:
                    error = result["error"]
                    if "EMAIL_NOT_FOUND" in error:
                        st.warning("Email not registered. Please sign up.")
                    elif "INVALID_PASSWORD" in error:
                        st.error("Incorrect password. Try again or reset.")
                    else:
                        st.error(error)

# Ensure the function runs when the file is executed
if __name__ == "__main__":
    login_page()
