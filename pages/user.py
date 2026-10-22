import streamlit as st
from datetime import date
from PIL import Image
import numpy as np
import joblib
import firebase_admin
from firebase_admin import credentials, firestore

# -----------------------------
# 🔥 Firebase Setup
# -----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(r"V:/boneage/firebase-key.json")  # your Firebase key path
    firebase_admin.initialize_app(cred)
db = firestore.client()

# -----------------------------
# Load Model
# -----------------------------
model = joblib.load("model.pkl")

st.set_page_config(page_title="Patient Details", layout="centered")

# -----------------------------
# Initialize Session State
# -----------------------------
for key in [
    "patient_name", "gender", "dob", "patient_id", "height", "weight",
    "uploaded_file", "predicted_bone_age", "patient_age",
    "show_profile", "user_name", "user_email", "user_role",
    "user_data", "user_id"
]:
    if key not in st.session_state:
        if key == "dob":
            st.session_state[key] = date(2000, 1, 1)
        elif key == "uploaded_file":
            st.session_state[key] = None
        elif key in ["show_profile"]:
            st.session_state[key] = False
        elif key == "user_data":
            st.session_state[key] = {}
        else:
            st.session_state[key] = ""

# -----------------------------
# Function: Get User Data from Firestore
# -----------------------------
def get_user_data(user_id):
    """Fetch user details from Firestore by user ID (registered_users collection)."""
    if not user_id:
        return None
    try:
        user_doc = db.collection("registered_users").document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return None


# -----------------------------
# 🔹 Top Bar with “Me” Button
# -----------------------------
st.markdown("""
    <style>
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background-color: #f0f2f6;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .app-title {
            font-size: 50px;
            font-weight: bold;
            color: #000000;
            padding-left: 80px;
        }
            }
        .app-titl {
            font-size: 30px;
            font-weight: bold;
            color: #000000;
            padding-left: 80px;
        }
        .me-btn {
            background-color: #1E90FF;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 6px 15px;
            cursor: pointer;
            font-size: 16px;
        }
        .me-btn:hover {
            background-color: #0077e6;
        }
    </style>
""", unsafe_allow_html=True)

col_top1, col_top2 = st.columns([0.9, 0.1])
with col_top1:
    st.markdown("<div class='app-title'>Patients Detail Form</div>", unsafe_allow_html=True)
with col_top2:
    if st.button("Me"):
        st.session_state.show_profile = not st.session_state.show_profile

# -----------------------------
# 🔹 Show Logged-in User Profile (from Firestore)
# -----------------------------
if st.session_state.show_profile:
    user_id = st.session_state.get("user_id", None)

    if not user_id:
        st.warning("⚠️ No logged-in user found. Please log in again.")
    else:
        user_data = get_user_data(user_id)
        st.session_state.user_data = user_data or {}

        if user_data:
            display_name = user_data.get("Name") or user_data.get("name") or st.session_state.get("user_name", "N/A")
            display_email = user_data.get("Email") or user_data.get("email") or st.session_state.get("user_email", "N/A")
            created_on = user_data.get("CreatedAt") or user_data.get("created_at") or user_data.get("createdOn") or "N/A"

            with st.expander("👤 Logged-in User Details", expanded=True):
                st.markdown("### User Profile")
                st.write(f"**Name:** {display_name}")
                st.write(f"**Email:** {display_email}")
                st.write(f"**User ID:** {user_id}")
                st.write(f"**Registered On:** {created_on}")
                st.write("---")

                if st.button("🚪 Logout"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.switch_page("home.py")
        else:
            st.error(f"No user data found for your account (User ID: {user_id}).")

# -----------------------------
# Page Title
# -----------------------------

# -----------------------------
# Helper Functions
# -----------------------------
def clear_all():
    st.session_state.patient_name = ""
    st.session_state.gender = "Select"
    st.session_state.dob = date(2000, 1, 1)
    st.session_state.patient_id = ""
    st.session_state.height = ""
    st.session_state.weight = ""
    st.session_state.uploaded_file = None
    st.session_state.predicted_bone_age = ""
    st.session_state.patient_age = ""


def calculate_age(birth_date):
    today = date.today()
    years = today.year - birth_date.year
    months = today.month - birth_date.month
    if today.day < birth_date.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return years, months


# -----------------------------
# 🩻 Function: Validate if Image is X-ray
# -----------------------------
def is_xray_image(image):
    """Check if the uploaded image looks like an X-ray (low color variance + good contrast)."""
    img = np.array(image)

    # --- Option 1: Color variance check ---
    if len(img.shape) == 3:  # RGB image
        color_std = np.mean(np.std(img, axis=(0, 1)))
        if color_std > 20:  # too colorful, not an X-ray
            return False

    # --- Option 3: Contrast heuristic ---
    gray = np.array(image.convert("L"))
    contrast = gray.std()
    if contrast < 30:  # too flat, not an X-ray
        return False

    return True


# -----------------------------
# Patient Form
# -----------------------------
with st.form("patient_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.patient_name = st.text_input("Full Name", value=st.session_state.patient_name)
        gender_options = ["Select", "Male", "Female", "Other"]
        current_gender = st.session_state.gender if st.session_state.gender in gender_options else "Select"
        st.session_state.gender = st.selectbox("Gender", gender_options, index=gender_options.index(current_gender))
        st.session_state.dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today(), value=st.session_state.dob)

        years, months = calculate_age(st.session_state.dob)
        st.session_state.patient_age = f"{years} years, {months} months"
        st.text_input("Patient Age (auto-calculated)", value=st.session_state.patient_age, disabled=True)

    with col2:
        st.session_state.patient_id = st.text_input("Patient ID (unique)", value=st.session_state.patient_id)
        st.session_state.height = st.text_input("Height (cm)", value=st.session_state.height)
        st.session_state.weight = st.text_input("Weight (kg)", value=st.session_state.weight)

    st.session_state.uploaded_file = st.file_uploader("Upload X-ray image", type=["png", "jpg", "jpeg"])

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        predict_btn = st.form_submit_button("Predict Bone Age")
    with col_btn2:
        submit_btn = st.form_submit_button("Next")
    with col_btn3:
        clear_btn = st.form_submit_button("Clear", on_click=clear_all)

# -----------------------------
# 🧠 Bone Age Prediction (with X-ray validation)
# -----------------------------
if predict_btn:
    if st.session_state.uploaded_file:
        image = Image.open(st.session_state.uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # ✅ Validate X-ray before predicting
        if not is_xray_image(image):
            st.error("❌ This image doesn’t appear to be a valid X-ray. Please upload a proper hand X-ray.")
        else:
            image = image.convert("L")
            img = np.array(image.resize((224, 224))).flatten().reshape(1, -1)
            prediction = model.predict(img)[0]

            st.session_state.predicted_bone = prediction
            st.success(f"Predicted Bone Age: {prediction:.2f} months")

            prediction_years = prediction / 12
            st.session_state.predicted_bone_age = prediction_years
            st.info(f"Predicted Bone Age: {prediction_years:.2f} years")
            # -----------------------------
        # ⚖️ Compare Predicted vs Chronological Age
        # -----------------------------
        # Extract patient’s chronological age in months
        years, months = calculate_age(st.session_state.dob)
        chronological_age_months = years * 12 + months

        # Predicted bone age in months
        predicted_bone_age_months = prediction

        # Difference in months
        age_difference = predicted_bone_age_months - chronological_age_months

        # Classify growth status
        if abs(age_difference) <= 12:
            growth_status = "🟢 Normal Growth"
        elif age_difference < -12:
            growth_status = "🔵 Delayed Growth"
        else:
            growth_status = "🔴 Advanced Growth"

        # Display comparison
        st.subheader("Growth Assessment")
        st.write(f"**Chronological Age:** {chronological_age_months / 12:.2f} years")
        st.write(f"**Predicted Bone Age:** {predicted_bone_age_months / 12:.2f} years")
        st.write(f"**Difference:** {abs(age_difference):.1f} months")
        st.write(f"**Growth Status:** {growth_status}")

    else:
        st.warning("⚠️ Please upload an X-ray image first.")

# -----------------------------
# Navigate to Review Page
# -----------------------------
if submit_btn:
    required_fields = [
        st.session_state.patient_name,
        st.session_state.gender,
        st.session_state.patient_id,
        st.session_state.height,
        st.session_state.weight,
        st.session_state.predicted_bone_age
    ]
    if "" in required_fields or st.session_state.gender == "Select":
        st.warning("⚠️ Please fill all fields and predict bone age before proceeding.")
    else:
        st.success("✅ Patient details ready! Redirecting to Review & Save page...")
        st.switch_page("pages/review.py")
# -----------------------------
# 🔙 Small Back Button (Top Left)
# -----------------------------
st.markdown("""
    <style>
        .small-back-btn {
            background-color: #1E90FF;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 4px 12px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        .small-back-btn:hover {
            background-color: #0077e6;
            transform: translateY(-1px);
        }
    </style>
""", unsafe_allow_html=True)

col_back, _ = st.columns([0.15, 0.85])
with col_back:
    if st.button("⬅️ Back"):
        st.switch_page("home.py")
