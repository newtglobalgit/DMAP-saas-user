import streamlit as st
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

st.set_page_config(
    page_title="DMAP SaaS offering - Cloud Resource Request Form",
    layout="centered",
    initial_sidebar_state="collapsed"
)
st.markdown("""
<style>
    .stTextInput > div > div > input {
        padding: 15px 10px;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def validate_email(email):
    """Validate office email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format (optional)"""
    if not phone:  # Phone is optional
        return True
    pattern = r'^\+?[1-9]\d{9,14}$'
    return re.match(pattern, phone) is not None

def send_approval_email(user_data):
    """Send approval email to administrator"""
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    admin_email = os.getenv("ADMIN_EMAIL")
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = admin_email
    msg['Subject'] = f"DMAP SaaS - Cloud Resource Request from {user_data['full_name']}"
    body = f"""
    DMAP SaaS - Cloud Resource Request

    New resource request received:

    Full Name: {user_data['full_name']}
    Email: {user_data['email']}
    Phone: {user_data['phone'] if user_data['phone'] else 'Not provided'}
    Company: {user_data['company']}
    Designation: {user_data['designation']}

    Please review and approve/reject this request.
    """
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
st.title("☁️ DMAP SaaS offer - Cloud Resource Request Form")
st.markdown("Please fill out the form below to request Azure cloud resources.")
with st.form("resource_request_form"):
    full_name = st.text_input(
        "Full Name*",
        help="Enter your full name as per official records"
    )
    email = st.text_input(
        "Office Email*",
        help="Enter your corporate email address"
    )
    phone = st.text_input(
        "Phone Number (Optional)",
        help="Enter your contact number with country code (e.g., +1234567890)"
    )
    company = st.text_input(
        "Company Name*",
        help="Enter your company's registered name"
    )
    designation = st.text_input(
        "Designation*",
        help="Enter your current role/position"
    )
    submit_button = st.form_submit_button("Submit Request")
    if submit_button:
        if not all([full_name, email, company, designation]):
            st.error("Please fill in all required fields marked with *")
        elif not validate_email(email):
            st.error("Please enter a valid email address")
        elif phone and not validate_phone(phone):
            st.error("Please enter a valid phone number with country code")
        else:
            user_data = {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "company": company,
                "designation": designation
            }
            if send_approval_email(user_data):
                st.session_state.form_submitted = True
                st.success("Your request has been submitted successfully! You will receive a confirmation email shortly.")
                #st.experimental_rerun()
            else:
                st.error("There was an error submitting your request. Please try again later.")
if st.session_state.form_submitted:
    st.markdown("""
    <div class="success-message">
        Thank you for your request! Our team will review it and get back to you soon.
    </div>
    """, unsafe_allow_html=True)
