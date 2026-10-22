import streamlit as st
from datetime import datetime, date
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="Review & Save", layout="centered")
st.title("🩺 Review & Save Patient Details")

# -----------------------------
# Firebase Initialization
# -----------------------------
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(r"V:/boneage/firebase-key.json")  # Update your path
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    st.error(f"Firebase initialization failed: {e}")

# -----------------------------
# Check session_state
# -----------------------------
required_keys = [
    "patient_name", "gender", "dob", "patient_id",
    "height", "weight", "predicted_bone_age", "uploaded_file", "patient_age"
]
missing = [k for k in required_keys if k not in st.session_state or st.session_state[k] == ""]

if missing:
    st.warning("⚠️ Patient data missing. Please fill the form first on the 'Patient Details' page.")
else:
    # -----------------------------
    # Review Section
    # -----------------------------
    st.subheader("📋 Patient Details")
    st.write(f"**Full Name:** {st.session_state.patient_name}")
    st.write(f"**Gender:** {st.session_state.gender}")
    st.write(f"**Date of Birth:** {st.session_state.dob}")
    st.write(f"**Patient Age:** {st.session_state.patient_age}")
    st.write(f"**Patient ID:** {st.session_state.patient_id}")
    st.write(f"**Height (cm):** {st.session_state.height}")
    st.write(f"**Weight (kg):** {st.session_state.weight}")
    st.write(f"**Predicted Bone Age:** {st.session_state.predicted_bone_age:.2f} years")

    if st.session_state.uploaded_file:
        image = Image.open(st.session_state.uploaded_file).convert("L")
        st.image(image, caption="Uploaded X-ray Image", use_column_width=True)

    # -----------------------------
    # 🧬 Growth Assessment (NEW SECTION)
    # -----------------------------
    st.subheader("🧬 Growth Assessment")

    # Convert patient’s chronological age from text (e.g., “10 years, 3 months”) to numeric years
    age_text = st.session_state.patient_age

    # --- Handle both string and numeric formats ---
    try:
        if isinstance(age_text, (int, float)):  # Direct numeric input
            years = int(age_text)
            months = int((age_text - years) * 12)
        elif isinstance(age_text, str):
            import re
            match = re.search(r"(\d+)\s*years?", age_text)
            years = int(match.group(1)) if match else 0

            match_months = re.search(r"(\d+)\s*months?", age_text)
            months = int(match_months.group(1)) if match_months else 0
        else:
            years, months = 0, 0
    except Exception:
        years, months = 0, 0

    chronological_age_months = years * 12 + months
    predicted_bone_age_months = st.session_state.predicted_bone_age * 12
    age_difference = predicted_bone_age_months - chronological_age_months


    # Classification Logic
    if abs(age_difference) <= 12:
        growth_status = "🟢 Normal Growth"
        growth_color = "#2ECC71"
    elif age_difference < -12:
        growth_status = "🔵 Delayed Growth"
        growth_color = "#3498DB"
    else:
        growth_status = "🔴 Advanced Growth"
        growth_color = "#E74C3C"

    # Display Growth Summary Card
    st.markdown(f"""
        <div style="background-color:{growth_color}; padding:15px; border-radius:12px; color:white; text-align:center;">
            <h3>Growth Status: {growth_status}</h3>
            <p><b>Chronological Age:</b> {chronological_age_months/12:.2f} years</p>
            <p><b>Predicted Bone Age:</b> {predicted_bone_age_months/12:.2f} years</p>
            <p><b>Difference:</b> {abs(age_difference):.1f} months</p>
        </div>
    """, unsafe_allow_html=True)

    # -----------------------------
    # Buttons
    # -----------------------------
    col_back, col_save = st.columns([1, 1])

    with col_back:
        if st.button("⬅ Back"):
            st.switch_page("pages/user.py")

    with col_save:
        if st.button("💾 Save to Firebase"):
            try:
                patient_data = {
                    "patient_id": st.session_state.patient_id,
                    "name": st.session_state.patient_name,
                    "gender": st.session_state.gender,
                    "dob": str(st.session_state.dob),
                    "patient_age": st.session_state.patient_age,
                    "height_cm": float(st.session_state.height),
                    "weight_kg": float(st.session_state.weight),
                    "bone_age_prediction": float(st.session_state.predicted_bone_age),
                    "chronological_age_years": chronological_age_months / 12,  # 🆕
                    "age_difference_months": age_difference,  # 🆕
                    "growth_status": growth_status,  # 🆕
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                db.collection("patients").document(st.session_state.patient_id).set(patient_data)
                st.success("✅ Patient details (including Growth Assessment) saved successfully to Firebase!")

                # Optional: Clear session after saving
                for key in [
                    "patient_name", "gender", "dob", "patient_id", "height",
                    "weight", "uploaded_file", "predicted_bone_age", "patient_age"
                ]:
                    st.session_state[key] = "" if key != "dob" else date(2000, 1, 1)

                st.switch_page("pages/user.py")

            except Exception as e:
                st.error(f"Error saving to Firebase: {e}")
