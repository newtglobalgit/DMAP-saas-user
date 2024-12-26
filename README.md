# DMAP-saas-user

A Streamlit-based web application for handling DMAP SaaS offering cloud resource requests. This application collects user information, creates a GitHub branch, and updates terraform configuration with user details.

## Features

- User-friendly web form for collecting resource request information
- Automatic GitHub branch creation with standardized naming convention
- Terraform variables update automation
- Email notification system for administrators
- Environment variable based configuration
- Secure credential management

## Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token with repository access
- SMTP-enabled email account for notifications

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DMAP-saas-user.git
   cd DMAP-saas-user
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your credentials:
   ```
   SENDER_EMAIL=your-email@example.com
   SENDER_PASSWORD=your-email-password
   ADMIN_EMAIL=admin@example.com
   GITHUB_TOKEN=your-github-pat-token
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run main.py
   ```

2. Fill out the resource request form with:
   - Full Name
   - Office Email
   - Phone Number (optional)
   - Company Name
   - Designation

3. Submit the form to:
   - Send an email notification to administrators
   - Create a new GitHub branch (format: `firstname-lastname-saas-offer-terraform`)
   - Update terraform variables with user information

## Branch Naming Convention

The application automatically creates GitHub branches following this format:
- Input: "John Peter"
- Output: "john-peter-saas-offer-terraform"

Features:
- Converts to lowercase
- Replaces spaces with hyphens
- Removes special characters
- Ensures GitHub naming compliance

## Security Considerations

- Store sensitive credentials in `.env` file
- Never commit `.env` file to version control
- Use fine-grained GitHub PAT with minimal permissions
- Regularly rotate credentials
- Environment variable validation on startup

## Repository Structure

```
DMAP-saas-user/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request