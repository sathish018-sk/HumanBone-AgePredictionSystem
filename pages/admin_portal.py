import streamlit as st

# --- Page Setup ---
st.set_page_config(page_title="BONiii | Admin Portal", layout="centered")

# --- CSS Styling ---
st.markdown("""
    <style>
    body {
        background-color: #f6faff;
        font-family: 'Poppins', sans-serif;
    }

    h2 {
        text-align: center;
        color: #1E90FF;
        margin-top: 80px;
        font-weight: 700;
    }

    .stTextInput>div>div>input {
        border: 1.5px solid #1E90FF;
        border-radius: 6px;
    }

    .stButton>button {
        width: 100%;
        background-color: #1E90FF;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        transition: background-color 0.2s ease-in-out;
    }

    .stButton>button:hover {
        background-color: #187bcd;
    }
    </style>
""", unsafe_allow_html=True)

# --- Portal Header ---
st.markdown("<h2> BONiii Admin Portal</h2>", unsafe_allow_html=True)

# --- Admin Login Form ---
with st.form("admin_login_form", clear_on_submit=True):
    admin_code = st.text_input("Enter Admin Code", type="password", placeholder="Enter secure code...")
    submit = st.form_submit_button("Submit")

    if submit:
        if admin_code == "BONiii2025":  # Replace with your secure code
            st.toast("✅ Access Granted! Welcome, Admin.", icon="🎉")
            st.success("Redirecting to Admin Dashboard...")
            st.session_state["admin_authenticated"] = True
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.toast("❌ Invalid Code. Please try again.", icon="🚫")
            st.error("Incorrect admin code.")
## -----------------------------
# 🔙 Small Back Button (Bottom)
# -----------------------------
st.markdown("""
    <style>
            .fixed-back-btn {
            left: 20px;
            bottom: 20px;
            background-color: #1E90FF;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 6px 14px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.15);
            transition: background-color 0.3s ease, transform 0.2s ease;
            z-index: 100;
        }
        .fixed-back-btn:hover {
            background-color: #0077e6;
            transform: translateY(-2px);
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 5, 1])  # 👈 Adjusted ratio to push button to left
with col1:  # 👈 Moved button to the left column
    if st.button("⬅️ Back"):
        st.switch_page("home.py")
