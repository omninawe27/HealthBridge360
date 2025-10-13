# TODO: Secure Credentials and Push to GitHub

- [ ] Update healthkart360/settings.py to use os.getenv for SECRET_KEY, DATABASES, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
- [ ] Update healthkart360/razorpay_settings.py to use os.getenv for RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET
- [ ] Create .env.example with placeholders for all sensitive variables
- [ ] Update .gitignore to include healthkart360/razorpay_settings.py
- [ ] Check git status and add remote if needed
- [ ] Commit changes with message "Secure credentials by moving to environment variables"
- [ ] Push to GitHub repo https://github.com/omninawe27/HealthBridge360.git
