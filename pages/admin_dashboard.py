import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bcrypt
import time
from datetime import datetime
import pandas as pd
import plotly.express as px

# -----------------------------
# 🔥 FIREBASE SETUP
# -----------------------------
cred = credentials.Certificate(r"V:/boneage/firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# -----------------------------
# 🌐 PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="BONiii | Admin Dashboard", layout="wide")

# -----------------------------
# 🚫 AUTH CHECK
# -----------------------------
if "admin_authenticated" not in st.session_state or not st.session_state["admin_authenticated"]:
    st.warning("⚠️ Unauthorized Access. Please log in via the Admin Portal.")
    st.stop()

# -----------------------------
# ✉️ EMAIL CONFIG
# -----------------------------
ADMIN_EMAIL = "sathishkumar959788@gmail.com"
ADMIN_PASSWORD = "gthj unyk wgen yfwy"  # Gmail App Password
USER_PORTAL_URL = "https://boniii-user.streamlit.app"
LOGO_URL = "https://i.ibb.co/8KxZ5mR/boniii-logo.png"

# -----------------------------
# 📧 EMAIL TEMPLATE
# -----------------------------
def create_html_email(user_name, portal_url, logo_url):
    return f"""
    <html>
    <body style="font-family:'Poppins',sans-serif;background-color:#f6faff;padding:20px;">
        <div style="max-width:600px;margin:auto;background:white;border-radius:12px;
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);overflow:hidden;">
            <div style="background-color:#1E90FF;padding:15px 0;text-align:center;">
                <img src="{logo_url}" alt="BONiii Logo" style="height:60px;">
                <h2 style="color:white;margin:10px 0 0;">BONiii Account Approved 🎉</h2>
            </div>
            <div style="padding:30px;text-align:left;color:#333;">
                <p>Dear <strong>{user_name}</strong>,</p>
                <p>Your <strong>BONiii User Account</strong> has been approved by the admin!</p>
                <p style="text-align:center;margin:30px 0;">
                    <a href="{portal_url}" target="_blank" 
                    style="background-color:#1E90FF;color:white;padding:12px 25px;
                           border-radius:6px;text-decoration:none;font-weight:bold;">
                    🔗 Access BONiii Portal
                    </a>
                </p>
                <p>Best regards,<br><strong>The BONiii Admin Team</strong></p>
            </div>
            <div style="background-color:#f0f8ff;text-align:center;padding:10px;
                        color:#555;font-size:12px;">
                © 2025 BONiii Technologies — All Rights Reserved.
            </div>
        </div>
    </body>
    </html>
    """

def send_html_email(recipient_email, subject, html_body):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = ADMIN_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(ADMIN_EMAIL, ADMIN_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        st.error(f"❌ Email failed to send: {e}")
        return False

# -----------------------------
# 🧭 HEADER + LOGOUT BUTTON
# -----------------------------
col1, col2 = st.columns([8, 1])
with col1:
    st.markdown("<h2 style='text-align:center; color:#1E90FF;'>⚙️ BONiii Admin Dashboard</h2>", unsafe_allow_html=True)
with col2:
    logout = st.button("Logout", use_container_width=True)
if logout:
    st.session_state["admin_authenticated"] = False
    st.success("👋 Logged out successfully!")
    time.sleep(1)
    st.switch_page("Home.py")

st.markdown("---")

# -----------------------------
# 📂 FIRESTORE COLLECTIONS
# -----------------------------
pending_ref = db.collection("user_requests")
registered_ref = db.collection("registered_users")
patients_ref = db.collection("patients")
downloads_ref = db.collection("download_history")

pending_snaps = list(pending_ref.stream())
registered_snaps = list(registered_ref.stream())
patients_snaps = list(patients_ref.stream())
download_snaps = list(downloads_ref.stream())

# -----------------------------
# 🧭 DASHBOARD TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    f"🕓 Pending Requests ({len(pending_snaps)})",
    f"✅ Registered Users ({len(registered_snaps)})",
    f"🦴 Patient Records ({len(patients_snaps)})",
])

# ==========================================================
# 🕓 PENDING REQUESTS TAB
# ==========================================================
with tab1:
    st.subheader("Pending Account Requests")
    if not pending_snaps:
        st.info("No pending requests found.")
    else:
        for doc in pending_snaps:
            req = doc.to_dict()
            doc_id = doc.id
            user_id = req.get("UserID") or req.get("ID", "N/A")

            with st.container(border=True):
                st.write(f"**👤 Name:** {req.get('Name', 'N/A')}")
                st.write(f"**📧 Email:** {req.get('Email', 'N/A')}")
                st.write(f"**📞 Mobile:** {req.get('Phone', req.get('phone', 'N/A'))}")
                st.write(f"**🆔 User ID:** {user_id}")

                colA, colB = st.columns(2)
                with colA:
                    if st.button(f"✅ Approve {req.get('Name','User')}", key=f"approve_{doc_id}", use_container_width=True):
                        try:
                            email = req.get("Email")
                            hashed_pw = req.get("Password")

                            registered_ref.document(user_id).set({
                                "Name": req.get("Name"),
                                "Email": email,
                                "Phone": req.get("Phone", req.get("phone")),
                                "UserID": user_id,
                                "Password": hashed_pw,
                                "CreatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })

                            pending_ref.document(doc_id).delete()

                            html_body = create_html_email(req.get("Name"), USER_PORTAL_URL, LOGO_URL)
                            send_html_email(email, "Your BONiii Account is Approved 🎉", html_body)

                            st.toast(f"✅ Access granted & email sent to {req.get('Name')}", icon="📩")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error approving user: {e}")

                with colB:
                    if st.button(f"❌ Cancel {req.get('Name','User')}", key=f"cancel_{doc_id}", use_container_width=True):
                        try:
                            pending_ref.document(doc_id).delete()
                            st.toast(f"🚫 Request cancelled for {req.get('Name')}", icon="🗑️")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error cancelling request: {e}")

# ==========================================================
# ✅ REGISTERED USERS TAB
# ==========================================================
with tab2:
    st.subheader("Manage Registered Users")
    if not registered_snaps:
        st.info("No registered users found.")
    else:
        for doc in registered_snaps:
            user = doc.to_dict()
            doc_id = doc.id
            user_id = user.get("UserID") or user.get("ID", doc_id)

            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**👤 Name:** {user.get('Name', 'N/A')}")
                    st.write(f"**📧 Email:** {user.get('Email', 'N/A')}")
                    st.write(f"**📞 Phone:** {user.get('Phone', 'N/A')}")
                    st.write(f"**🆔 User ID:** {user_id}")
                    st.write(f"**🕓 Created:** {user.get('CreatedAt', 'N/A')}")
                with col2:
                    if st.button("❌ Revoke Access", key=f"del_{doc_id}", use_container_width=True):
                        try:
                            registered_ref.document(doc_id).delete()
                            st.toast(f"🗑️ Access revoked for {user.get('Name')}", icon="✅")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error revoking access: {e}")

# ==========================================================
# 🦴 PATIENT RECORDS TAB
# ==========================================================
with tab3:
    st.subheader("Patient Records Overview")
    if not patients_snaps:
        st.info("No patient records available yet.")
    else:
        for doc in patients_snaps:
            patient = doc.to_dict()
            with st.expander(f"🩺 {patient.get('name', 'Unnamed')} — ID: {patient.get('patient_id', 'N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
                    st.write(f"**Date of Birth:** {patient.get('dob', 'N/A')}")
                    st.write(f"**Age:** {patient.get('patient_age', 'N/A')} years")
                    st.write(f"**Height (cm):** {patient.get('height_cm', 'N/A')}")
                    st.write(f"**Weight (kg):** {patient.get('weight_kg', 'N/A')}")
                with col2:
                    st.write(f"**Predicted Bone Age:** {patient.get('bone_age_prediction', 'N/A')} years")
                    st.write(f"**Report Created:** {patient.get('created_at', 'N/A')}")
                    st.write(f"**Patient Code:** {doc.id}")
                st.markdown("---")
                if st.button(f"🗑️ Delete Record ({patient.get('name', 'N/A')})", key=f"del_patient_{doc.id}"):
                    try:
                        patients_ref.document(doc.id).delete()
                        st.toast(f"🗑️ Patient record deleted for {patient.get('name', 'N/A')}", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting record: {e}")

# ==========================================================
# 📊 COLLAPSIBLE DATA VISUALIZATION MODULE (robust age calc)
# ==========================================================
with st.expander("📊 Open Data Visualization Module", expanded=False):
    st.markdown("### 📈 Patient Data Insights Dashboard")

    # build dataframe from firestore patient docs
    data = [doc.to_dict() for doc in patients_snaps]
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("⚠️ No data available for visualization yet.")
    else:
        # --- Normalize column names to lower-case keys to avoid casing issues ---
        df.columns = [c if not isinstance(c, str) else c.strip() for c in df.columns]

        # --- Helper: attempt to parse numeric ages from strings like '10 yrs' ---
        def parse_age_value(x):
            try:
                if pd.isna(x):
                    return None
                # If already numeric
                if isinstance(x, (int, float)):
                    return float(x)
                s = str(x).strip()
                # Extract first integer/float in string
                m = re.search(r"(\d+(\.\d+)?)", s)
                if m:
                    return float(m.group(1))
                return None
            except Exception:
                return None

        # --- If patient_age column exists, coerce values to numeric where possible ---
        if "patient_age" in df.columns:
            df["patient_age_parsed"] = df["patient_age"].apply(parse_age_value)
        else:
            df["patient_age_parsed"] = pd.NA

        # --- If dob present and patient_age missing, compute from dob ---
        if "dob" in df.columns:
            def age_from_dob(dob_val):
                try:
                    dob_parsed = pd.to_datetime(dob_val, errors="coerce")
                    if pd.isna(dob_parsed):
                        return None
                    today = pd.Timestamp.now().normalize()
                    # age in years (float)
                    age_years = (today - dob_parsed).days / 365.25
                    return float(age_years)
                except Exception:
                    return None

            # compute ages from dob only where patient_age_parsed is missing/NaN
            dob_ages = df["dob"].apply(age_from_dob)
            # combine: prefer explicit patient_age_parsed, otherwise use dob_ages
            df["patient_age_final"] = df["patient_age_parsed"].where(
                df["patient_age_parsed"].notna(), dob_ages
            )
        else:
            df["patient_age_final"] = df["patient_age_parsed"]

        # --- Try other common age keys if still missing (e.g., 'age') ---
        if df["patient_age_final"].isna().all() and "age" in df.columns:
            df["patient_age_final"] = df["age"].apply(parse_age_value)

        # --- Ensure numeric types and drop impossible values ---
        df["patient_age_final"] = pd.to_numeric(df["patient_age_final"], errors="coerce")
        # remove negative or implausible ages
        df.loc[(df["patient_age_final"] < 0) | (df["patient_age_final"] > 120), "patient_age_final"] = pd.NA

        # --- Convert other numeric columns safely ---
        for col in ["bone_age_prediction", "height_cm", "weight_kg"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # --- Summary Metrics (show N/A if no valid numeric) ---
        def safe_mean_label(series, fmt="{:.1f}"):
            if series is None or series.dropna().empty:
                return "N/A"
            return fmt.format(series.dropna().mean())

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🧒 Avg Patient Age", safe_mean_label(df.get("patient_age_final")))
        col2.metric("🦴 Avg Bone Age", safe_mean_label(df.get("bone_age_prediction")))
        col3.metric("📏 Avg Height", safe_mean_label(df.get("height_cm")))
        col4.metric("⚖️ Avg Weight", safe_mean_label(df.get("weight_kg")))

        st.markdown("---")

        # --- 2️⃣ Gender Distribution ---
        if "gender" in df.columns and not df["gender"].dropna().empty:
            gender_count = df["gender"].fillna("Unknown").value_counts().reset_index()
            gender_count.columns = ["Gender", "Count"]
            fig2 = px.pie(
                gender_count,
                names="Gender",
                values="Count",
                title="👩‍🦰👨‍🦱 Gender Distribution of Patients",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig2, use_container_width=True)

        # --- 3️⃣ Height vs Weight ---
        if "height_cm" in df.columns and "weight_kg" in df.columns and not df[["height_cm","weight_kg"]].dropna(how="all").empty:
            fig3 = px.scatter(
                df,
                x="height_cm",
                y="weight_kg",
                color="gender" if "gender" in df.columns else None,
                title="📏 Height vs ⚖️ Weight of Patients",
                labels={"height_cm": "Height (cm)", "weight_kg": "Weight (kg)"}
            )
            st.plotly_chart(fig3, use_container_width=True)

        # --- 4️⃣ Reports Over Time ---
        if "created_at" in df.columns:
            df["created_at_ts"] = pd.to_datetime(df["created_at"], errors="coerce")
            time_data = df.dropna(subset=["created_at_ts"]).groupby(df["created_at_ts"].dt.date).size().reset_index(name="Count")
            if not time_data.empty:
                fig4 = px.bar(
                    time_data,
                    x="created_at_ts",
                    y="Count",
                    title="📆 Number of Reports Created Over Time",
                    labels={"created_at_ts": "Date", "Count": "Reports"},
                    color_discrete_sequence=["#1E90FF"]
                )
                st.plotly_chart(fig4, use_container_width=True)
