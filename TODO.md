# TODO: Secure Credentials and Push to GitHub

- [x] Update healthkart360/settings.py to use os.getenv for SECRET_KEY, DATABASES, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
- [x] Update healthkart360/razorpay_settings.py to use os.getenv for RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET
- [x] Create .env.example with placeholders for all sensitive variables
- [x] Update .gitignore to include healthkart360/razorpay_settings.py
- [x] Check git status and ensure sensitive files are not tracked
- [x] Add GitHub remote https://github.com/omninawe27/HealthBridge360.git if not present
- [x] Add all changes to git
- [x] Commit changes with message "Secure credentials by moving to environment variables"
- [x] Push to GitHub repo
