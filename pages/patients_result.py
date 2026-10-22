import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import io

# --------------------------------------------
# Page Configuration
# --------------------------------------------
st.set_page_config(page_title="🔍 Patient Results", layout="centered")
st.title("🔍 View Your Bone Age Results")

# --------------------------------------------
# Firebase Initialization
# --------------------------------------------
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(r"V:/boneage/firebase-key.json")  # ✅ Update your path
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    st.error(f"Firebase initialization failed: {e}")

# --------------------------------------------
# Patient Code Input
# --------------------------------------------
st.write("Please enter your **Patient Code** to view your report.")
patient_code = st.text_input("🧾 Enter Patient ID", placeholder="e.g. P12345")

get_btn = st.button("📄 Get Results")

# --------------------------------------------
# Fetch Results from Firebase
# --------------------------------------------
if get_btn:
    if patient_code.strip() == "":
        st.warning("⚠️ Please enter your patient ID first.")
    else:
        try:
            doc_ref = db.collection("patients").document(patient_code)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                st.success("✅ Record Found!")

                # 🧮 Format numeric values
                try:
                    bone_age = float(data.get("bone_age_prediction", 0))
                    bone_age_fmt = f"{bone_age:.2f}"
                except:
                    bone_age_fmt = data.get("bone_age_prediction", "N/A")

                try:
                    patient_age = float(data.get("patient_age", 0))
                    patient_age_fmt = f"{patient_age:.2f}"
                except:
                    patient_age_fmt = data.get("patient_age", "N/A")

                # --------------------------------------------
                # Display Patient Info
                # --------------------------------------------
                st.subheader("🩺 Patient Information")
                st.write(f"**Name:** {data.get('name', 'N/A')}")
                st.write(f"**Gender:** {data.get('gender', 'N/A')}")
                st.write(f"**Date of Birth:** {data.get('dob', 'N/A')}")
                st.write(f"**Patient Age:** {patient_age_fmt} years")
                st.write(f"**Height (cm):** {data.get('height_cm', 'N/A')}")
                st.write(f"**Weight (kg):** {data.get('weight_kg', 'N/A')}")
                st.write(f"**Predicted Bone Age:** {bone_age_fmt} years")
                st.write(f"**Report Created:** {data.get('created_at', 'N/A')}")

                st.markdown("---")
                st.success("🦴 Bone Age report successfully retrieved.")

                # --------------------------------------------
                # Generate PDF Report
                # --------------------------------------------
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=A4)
                width, height = A4

                # Title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(200, height - 80, "🩺 Bone Age Report")

                # Body
                c.setFont("Helvetica", 12)
                y = height - 130
                line_height = 25

                c.drawString(50, y, f"Patient ID: {patient_code}"); y -= line_height
                c.drawString(50, y, f"Name: {data.get('name', 'N/A')}"); y -= line_height
                c.drawString(50, y, f"Gender: {data.get('gender', 'N/A')}"); y -= line_height
                c.drawString(50, y, f"Date of Birth: {data.get('dob', 'N/A')}"); y -= line_height
                c.drawString(50, y, f"Patient Age: {patient_age_fmt} years"); y -= line_height
                c.drawString(50, y, f"Height (cm): {data.get('height_cm', 'N/A')}"); y -= line_height
                c.drawString(50, y, f"Weight (kg): {data.get('weight_kg', 'N/A')}"); y -= line_height
                c.drawString(50, y, f"Predicted Bone Age: {bone_age_fmt} years"); y -= line_height
                c.drawString(50, y, f"Report Created: {data.get('created_at', 'N/A')}")
                c.showPage()
                c.save()
                pdf_buffer.seek(0)

                # --------------------------------------------
                # Download Button
                # --------------------------------------------
                download_clicked = st.download_button(
                    label="⬇️ Download Report as PDF",
                    data=pdf_buffer,
                    file_name=f"BoneAgeReport_{patient_code}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error fetching data: {e}")
# --------------------------------------------
# Footer / Back Button
# --------------------------------------------
st.markdown("---")
if st.button("⬅ Back to Portal"):
    st.switch_page("Home.py")
