import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import bcrypt
import time
import base64
import re
import os

# -----------------------------
# 🔥 Firebase Initialization
# -----------------------------
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(r"V:/boneage/firebase-key.json")
        firebase_admin.initialize_app(cred)
except Exception as e:
    st.error("⚠️ Firebase initialization failed.")
    print(f"Firebase Error: {e}")

if firebase_admin._apps:
    db = firestore.client()
    pending_ref = db.collection("user_requests")
    registered_ref = db.collection("registered_users")
else:
    db = None
    pending_ref = None
    registered_ref = None

# -----------------------------
# 🌐 Page Setup
# -----------------------------
st.set_page_config(page_title="BONiii | User Portal", layout="centered")

# -----------------------------
# 🌆 Background Styling
# -----------------------------
def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

background_path = r"V:/boneage/images/background.png"
base64_img = get_base64(background_path) if os.path.exists(background_path) else None

if base64_img:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{base64_img}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# 🌈 Modern CSS Styling
# -----------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Main Title */
    h2 {
        text-align: center;
        color: #1E90FF;
        font-weight: 700;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 25px;
    }

    /* Center Card Style */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        max-width: 450px;
        margin: 2rem auto;
        transition: transform 0.3s ease;
    }
    .glass-card:hover {
        transform: scale(1.02);
    }

    /* Input Fields */
    .stTextInput>div>div>input {
        border-radius: 10px;
        padding: 10px 14px;
        border: 1px solid #ccc;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #1E90FF;
        box-shadow: 0 0 0 2px rgba(30,144,255,0.2);
    }

    /* Buttons */
    div.stButton>button {
        background: linear-gradient(90deg, #1E90FF, #3ba4ff);
        color: white;
        border: none;
        font-weight: 600;
        border-radius: 25px;
        padding: 0.6rem 1.2rem;
        width: 100%;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(30,144,255,0.2);
    }
    div.stButton>button:hover {
        background: linear-gradient(90deg, #0077e6, #1E90FF);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30,144,255,0.3);
    }

    /* Navigation Tabs */
    .tab-btn {
        background: transparent;
        border: 2px solid #1E90FF;
        color: #1E90FF;
        border-radius: 20px;
        font-weight: 600;
        padding: 0.4rem 1rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    .tab-btn:hover {
        background: #1E90FF;
        color: white;
    }

    /* Back Button */
    .small-btn {
        display: inline-block;
        background: #1E90FF;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 5px 14px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .small-btn:hover {
        background-color: #0077e6;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# ⚙️ Session Management
# -----------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "login"

if st.session_state.get("logged_in", False):
    st.switch_page("pages/user_portal.py")

# -----------------------------
# 🧭 Header
# -----------------------------
st.markdown("<h2>👤 BONiii User Portal</h2>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Access your personalized dashboard securely</p>", unsafe_allow_html=True)

# -----------------------------
# 🔹 Tab Navigation
# -----------------------------

col1, col2 = st.columns(2)
with col1:
    if st.button("Login", key="tab_login", use_container_width=True):
        st.session_state.mode = "login"
        st.rerun()
with col2:
    if st.button("Sign Up", key="tab_signup", use_container_width=True):
        st.session_state.mode = "signup"
        st.rerun()

# -----------------------------
# 🔐 LOGIN SECTION
# -----------------------------
if st.session_state.mode == "login":
    
    st.subheader("Login with Your User ID")
    with st.form("login_form"):
        user_id = st.text_input("🆔 User ID")
        password = st.text_input("🔑 Password", type="password")
        login_submit = st.form_submit_button("Login")

        if login_submit:
            if not user_id or not password:
                st.warning("⚠️ Please enter your User ID and password.")
            elif not db:
                st.error("Database connection not established.")
            else:
                try:
                    user_doc = registered_ref.document(user_id).get()
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                        stored_hash = user_data.get("Password")
                        if stored_hash and bcrypt.checkpw(password.encode(), base64.b64decode(stored_hash)):
                            st.session_state.update({
                                "logged_in": True,
                                "user_name": user_data.get("Name", "User"),
                                "user_email": user_data.get("Email", "N/A"),
                                "user_id": user_id,
                                "user_phone": user_data.get("Phone", "N/A"),
                                "login_time": time.strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.toast(f"✅ Welcome back, {st.session_state['user_name']} 💙", icon="🎉")
                            time.sleep(1)
                            st.switch_page("pages/user.py")
                        else:
                            st.error("❌ Invalid User ID or password.")
                    else:
                        st.error("❌ No account found with that User ID.")
                except Exception as e:
                    st.error(f"⚠️ Login error: {e}")
    st.markdown("", unsafe_allow_html=True)

# -----------------------------
# 📝 SIGN UP SECTION
# -----------------------------
else:
    st.subheader("Create a New Account")
    with st.form("signup_form"):
        full_name = st.text_input("👤 Full Name")
        email = st.text_input("📧 Email ID")
        phone = st.text_input("📞 Phone Number")
        user_id = st.text_input("🆔 Create User ID")
        password = st.text_input("🔑 Create Password", type="password")
        signup_submit = st.form_submit_button("Apply")

        if signup_submit:
            if not (full_name and email and phone and user_id and password):
                st.warning("⚠️ Please fill all fields.")
            elif not re.match("^[A-Za-z0-9_]+$", user_id):
                st.warning("⚠️ User ID can only contain letters, numbers, or underscores.")
            elif len(user_id) < 6:
                st.warning("⚠️ User ID must be at least 6 characters.")
            elif not db:
                st.error("Database connection not established.")
            else:
                try:
                    if registered_ref.document(user_id).get().exists or pending_ref.document(user_id).get().exists:
                        st.warning("⚠️ This User ID already exists.")
                    else:
                        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                        hashed_pw_str = base64.b64encode(hashed_pw).decode()
                        pending_ref.document(user_id).set({
                            "Name": full_name,
                            "Email": email,
                            "Phone": phone,
                            "ID": user_id,
                            "Password": hashed_pw_str,
                            "Status": "Pending",
                            "Timestamp": firestore.SERVER_TIMESTAMP
                        })
                        st.toast("✅ Signup successful! Await admin approval.", icon="🕓")
                        time.sleep(1.2)
                        st.session_state.mode = "login"
                        st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Signup failed: {e}")
    

# -----------------------------
# 🔙 Back Button
# -----------------------------
col_back, _ = st.columns([0.25, 0.75])
with col_back:
    if st.session_state.mode == "signup":
        if st.button("⬅️ Back", key="back_to_login", use_container_width=True):
            st.session_state.mode = "login"
            st.rerun()
    else:
        if st.button("⬅️ Back", key="back_to_home", use_container_width=True):
            st.switch_page("home.py")
