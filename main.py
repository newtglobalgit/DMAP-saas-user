import streamlit as st
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from github import Github
import base64
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Validate environment variables
def validate_env_vars():
    required_vars = ['GITHUB_TOKEN', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'ADMIN_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

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

def create_branch_name(full_name):
    """
    Create a GitHub-compliant branch name from user's full name
    Example: 'John Peter' -> 'john-peter-saas-offer-terraform'
    """
    # Convert to lowercase and replace spaces with hyphens
    branch_name = full_name.lower().strip()
    # Replace multiple spaces with single hyphen
    branch_name = '-'.join(word for word in branch_name.split() if word)
    # Add suffix
    branch_name = f"{branch_name}-saas-offer-terraform"
    # Remove any special characters except hyphens
    branch_name = ''.join(c if c.isalnum() or c == '-' else '' for c in branch_name)
    # Remove multiple consecutive hyphens
    while '--' in branch_name:
        branch_name = branch_name.replace('--', '-')
    # Remove leading/trailing hyphens
    branch_name = branch_name.strip('-')
    return branch_name

def update_github_terraform_vars(user_data):
    """Update terraform variables in GitHub repository"""
    try:
        # Initialize GitHub client
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GitHub token not found in environment variables")
        
        g = Github(github_token)
        repo = g.get_repo("newtglobalgit/DMAP_SAAS_OFFER_TERRAFORM")
        
        # Get main branch
        main_branch = repo.get_branch("main")
        
        # Create new branch name using the standardized function
        branch_name = create_branch_name(user_data['full_name'])
        
        try:
            repo.create_git_ref(f"refs/heads/{branch_name}", main_branch.commit.sha)
        except:
            st.warning(f"Branch {branch_name} already exists, will update existing branch")
        
        # Get terraform.auto.tfvars file
        file_path = "terraform.auto.tfvars"
        file = repo.get_contents(file_path, ref="main")
        content = base64.b64decode(file.content).decode()
        
        # Parse and update tags
        try:
            # Find the tags section and update it
            lines = content.split('\n')
            new_lines = []
            in_tags = False
            for line in lines:
                if 'tags = {' in line:
                    in_tags = True
                    new_lines.append('tags = {')
                    new_lines.append(f'    "Owner"       = "{user_data["full_name"]}"')
                    new_lines.append(f'    "Email"       = "{user_data["email"]}"')
                    new_lines.append(f'    "Company"     = "{user_data["company"]}"')
                    new_lines.append(f'    "Designation" = "{user_data["designation"]}"')
                    if user_data["phone"]:
                        new_lines.append(f'    "Phone"       = "{user_data["phone"]}"')
                    new_lines.append('  }')
                    while in_tags and '}' not in line:
                        next
                    in_tags = False
                elif not in_tags:
                    new_lines.append(line)
            
            new_content = '\n'.join(new_lines)
            
            # Commit changes
            repo.update_file(
                file_path,
                f"Update tags with information for {user_data['full_name']}",
                new_content,
                file.sha,
                branch=branch_name
            )
            return True, branch_name
            
        except Exception as e:
            raise Exception(f"Error updating terraform vars: {str(e)}")
            
    except Exception as e:
        st.error(f"GitHub operation failed: {str(e)}")
        return False, None

if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if not validate_env_vars():
    st.stop()
st.title(" DMAP SaaS offer - Cloud Resource Request Form")
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
            success = False
            if send_approval_email(user_data):
                # Update GitHub repository
                github_success, branch_name = update_github_terraform_vars(user_data)
                if github_success:
                    st.session_state.form_submitted = True
                    st.markdown(f"""
                    <div class="success-message">
                        Thank you for your request! Our team will review it and get back to you soon.<br>
                        A new branch '{branch_name}' has been created with your information.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Failed to update GitHub repository. Please contact support.")
            else:
                st.error("There was an error submitting your request. Please try again later.")
if st.session_state.form_submitted:
    st.markdown("""
    <div class="success-message">
        Thank you for your request! Our team will review it and get back to you soon.
    </div>
    """, unsafe_allow_html=True)
