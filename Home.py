import streamlit as st
import base64
import os

# --- Encode background image ---
def get_base64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# --- Background ---



# --- Page Configuration ---
st.set_page_config(page_title="BONiii | Home", layout="wide")

# --- Custom CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One&display=swap');



.stApp::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: rgba(0,0,0,0.55);
    z-index: 1;
}}

.stApp > div:first-child {{
    position: relative;
    z-index: 2;
}}

/* --- Logo Section --- */
.logo-container {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding-top: 15px;
    padding-bottom: 5px;
    text-align: center;
}}

.bone-text {{
    font-family: 'Fredoka One', cursive;
    font-size: 5.5em;
    letter-spacing: 6px;
    text-transform: uppercase;
    color: #f8f8f8;
    text-shadow:
        0 2px 2px #bfcad4,
        0 4px 4px #aeb9c4,
        0 6px 10px rgba(0,0,0,0.25),
        0 0 20px rgba(255,255,255,0.3);
    animation: glow 4s ease-in-out infinite;
}}

@keyframes glow {{
    0%, 100% {{
        filter: drop-shadow(0 0 8px rgba(255,255,255,0.3))
                drop-shadow(0 0 15px rgba(150,220,255,0.4));
    }}
    50% {{
        filter: drop-shadow(0 0 15px rgba(255,255,255,0.6))
                drop-shadow(0 0 25px rgba(150,220,255,0.7));
    }}
}}

.subtitle {{
    font-family: 'Poppins', sans-serif;
    font-size: 1.1em;
    color: #e6f8ff;
    text-shadow: 0 2px 6px rgba(0,0,0,0.5);
    margin-top: 2px;
    margin-bottom: 10px;
}}

/* --- Portal Section --- */
.portal-container {{
    display: flex;
    justify-content: center;
    gap: 25px;
    flex-wrap: wrap;
    width: 80%;
    margin: 10px auto 25px auto;
}}

.portal-card {{
    flex: 1 1 280px;
    background-color: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    padding: 25px 20px 30px 20px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    text-align: center;
    min-height: 230px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.portal-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 7px 16px rgba(0,0,0,0.12);
}}

.portal-card h3 {{
    color: #1E90FF;
    margin-bottom: 10px;
}}

.portal-card p {{
    color: #333;
    font-size: 0.98em;
    margin-bottom: 20px;
}}

.stButton > button {{
    background-color: #1E90FF;
    color: white;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 0.95em;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    margin-top: 5px;
}}

.stButton > button:hover {{
    background-color: #187bcd;
    transform: translateY(-2px);
}}

/* --- Info Section (Matched Width with Portal) --- */
.info-box {{
    width: 80%;
    margin: 25px auto;
    background-color: rgba(255, 255, 255, 0.92);
    border-radius: 12px;
    padding: 25px;
    text-align: left;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
}}

/* --- Footer (Matched Width with Portal) --- */
.footer-box {{
    width: 80%;
    margin: 20px auto 30px auto;
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    color: #333;
    font-size:15px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.05);
}}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="logo-container">
    <div class="bone-text">BONEAGE</div>
</div>
""", unsafe_allow_html=True)

# --- Portal Section ---
col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown("""
        <div class="portal-card">
            <h3>👤 User Portal</h3>
            <p>Clinicians can upload X-rays, view AI-based results, and generate diagnostic reports.</p>
        """, unsafe_allow_html=True)
        if st.button("🔑 Login as User", key="user_btn"):
            st.switch_page("pages/user_portal.py")
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("""
        <div class="portal-card">
            <h3>⚙️ Admin Portal</h3>
            <p>Admins can manage users, monitor AI performance, and deploy new models.</p>
        """, unsafe_allow_html=True)
        if st.button("🛠️ Login as Admin", key="admin_btn"):
            st.switch_page("pages/admin_Portal.py")
        st.markdown("</div>", unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown("""
        <div class="portal-card">
            <h3>🧍 Patient Portal</h3>
            <p>Patients can access their test results and download their results.</p>
        """, unsafe_allow_html=True)
        if st.button("📋 Login as Patient", key="patient_btn"):
            st.switch_page("pages/patients_result.py")
        st.markdown("</div>", unsafe_allow_html=True)

# --- Info Section ---
st.markdown("""
<div class="info-box">
<h3>🧠 About BONEAGE</h3>
<p><strong>BONEAGE</strong> is an advanced <strong>AI-powered Bone Age Estimation Platform</strong> that leverages deep learning to analyze hand and wrist X-ray images for precise skeletal maturity assessment.  
It aims to assist radiologists, clinicians, and researchers in diagnosing growth disorders with higher speed and consistency.</p>

<h4 style="color:#1E90FF; margin-top:20px;">🌟 Key Highlights</h4>
<ul style="list-style-type: '✅ '; padding-left:20px;">
<li><strong>Deep CNN-based Model:</strong> Delivers high-accuracy bone age prediction using state-of-the-art neural architectures.</li>
<li><strong>Automated Preprocessing:</strong> Intelligent cropping, noise reduction, and contrast enhancement for cleaner inputs.</li>
<li><strong>Multi-Format Support:</strong> Accepts <em>DICOM, PNG, JPG</em>, and other standard image formats.</li>
<li><strong>Confidence Estimation:</strong> Provides a confidence score to ensure transparency and reliability of AI predictions.</li>
<li><strong>Data Security:</strong> Encrypted cloud integration (Firebase) ensures medical data privacy and HIPAA compliance.</li>
</ul>

<h4 style="color:#1E90FF; margin-top:20px;">🧍‍♂️ Who Can Use BONiii?</h4>
<ul style="list-style-type: '👨‍⚕️ '; padding-left:20px;">
<li><strong>Doctors & Radiologists:</strong> To assist in diagnosis and reduce manual effort in bone age assessment.</li>
<li><strong>Hospitals & Clinics:</strong> For integrating automated skeletal maturity evaluation into their workflows.</li>
<li><strong>Researchers:</strong> To study bone growth patterns using AI-backed datasets.</li>
<li><strong>Patients:</strong> To easily access their reports and monitor growth milestones.</li>
</ul>

<h4 style="color:#1E90FF; margin-top:20px;">🚀 Mission</h4>
<p>Our mission is to make <strong>AI-assisted pediatric radiology</strong> accessible, efficient, and accurate — reducing the diagnostic burden and enabling data-driven healthcare decisions globally.</p>

</div>
""", unsafe_allow_html=True)

# --- Footer (Aligned with Portal Width) ---
st.markdown("""
<div class="footer-box">
    <p style="font-size:16px; font-weight:500; color:#1E90FF; margin-bottom:5px;">
        © 2025 <strong>BONiii</strong> | AI-Powered Bone Age Prediction System
    </p>
    <p style="margin:5px 0; color:#333;">Developed with ❤️ for next-gen medical diagnostics.</p>
    <hr style="border: 0; border-top: 1px solid #d9e6f2; margin: 10px auto; width: 70%;">
    <p style="color:#333; font-size:15px; line-height:1.6;">
        📧 <strong>Email:</strong> <a href="mailto:sathishkumar959788@gmail.com" style="color:#1E90FF; text-decoration:none;">sathishkumar959788@gmail.com</a><br>
        📞 <strong>Phone:</strong> <a href="tel:+919597881218" style="color:#1E90FF; text-decoration:none;">+91 95978 81218</a><br>
        📍 <strong>Location:</strong> Aruppukottai, Tamil Nadu, India
    </p>
</div>
""", unsafe_allow_html=True)
