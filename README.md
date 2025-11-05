# HealthBridge 360 - Healthcare Web Application

A comprehensive, mobile-first healthcare web application designed for rural Indian users. HealthBridge 360 provides a simple, multilingual system that allows users to search for medicines locally, upload prescriptions, set medicine reminders, place orders, and access emergency help.

## 🌟 Features

### 👤 User Features
- **Multi-language Support**: English, Hindi, Marathi
- **Medicine Search**: Find medicines and nearby pharmacies
- **Prescription Upload**: Upload prescription images for medicine orders
- **Advance Orders**: Order medicines not currently in stock with payment upfront
- **Medicine Reminders**: Set reminders with customizable alerts and automated notifications
- **Order Management**: Track order history and live status
- **Emergency Mode**: Quick access to 24x7 pharmacies and essential medicines
- **Shopping Cart**: Add medicines to cart and checkout
- **User Profile**: Manage personal information and preferences

### 🏥 Pharmacist Features
- **Pharmacy Dashboard**: Overview of orders, inventory, and statistics
- **Inventory Management**: Add, edit, and manage medicine stock
- **Order Management**: Process and update order status
- **Advance Order Processing**: Handle advance orders for out-of-stock medicines
- **Stock Alerts**: Low stock and expiry notifications
- **Medicine Alternatives**: Manage alternative medicine relationships

### 🔧 Technical Features
- **Mobile-First Design**: Responsive design optimized for mobile devices
- **Real-time Notifications**: Toast notifications and email alerts
- **Automated Reminder System**: Background scheduler for medication reminders
- **AJAX Integration**: Smooth user experience with asynchronous requests
- **Session Management**: Shopping cart and user session handling
- **Database Management**: Comprehensive data models and relationships
**Email Integration**: SendGrid-based email notifications for orders and reminders

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7 (Python)
- **Database**: PostgreSQL (via Render)
- **Frontend**: Next.js 15.2.4 (React, TypeScript), HTML5, CSS3, JavaScript (Tailwind CSS)
- **Package Manager**: pnpm
- **Authentication**: Django's built-in authentication system
- **File Upload**: Image upload for prescriptions
- **Geolocation**: Pharmacy location services
- **Caching**: Django's cache framework
- **Pagination**: Django pagination for large datasets

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd healthbridge360
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Install Frontend Dependencies
```bash
pnpm install
```

### 7. Run Development Servers
```bash
# Terminal 1: Django backend
python manage.py runserver

# Terminal 2: Next.js frontend
pnpm dev
```

The application will be available at:
- **Backend API**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`

## 📱 Application Structure

```
healthbridge360/
├── app/                      # Next.js components
├── components/               # UI components
├── core/                     # Core application views
├── healthkart360/           # Main Django project
├── medicines/               # Medicine management app
├── notifications/           # Notification management app
├── orders/                  # Order management app
├── pharmacy/                # Pharmacy management app
├── reminders/               # Reminder management app
├── users/                   # User management app
├── static/                  # Static files (CSS, JS, images)
├── templates/               # HTML templates
├── scripts/                 # Automation and initialization scripts
├── locale/                  # Translation files
├── media/                   # User uploaded files
└── manage.py               # Django management script
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY='your-strong-secret-key'
DEBUG=True
DATABASE_URL='sqlite:///db.sqlite3' # For local development
# Or for PostgreSQL:
# DATABASE_URL='postgres://user:password@localhost:5432/healthbridge360'

SENDGRID_API_KEY='your-sendgrid-api-key'
DEFAULT_FROM_EMAIL='noreply@healthbridge360.com'
```

### Database Configuration
Update `healthkart360/settings.py` with your database credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'healthbridge360',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🔒 Security Features

- **CSRF Protection**: All forms protected against Cross-Site Request Forgery attacks
- **SQL Injection Prevention**: Django ORM prevents SQL injection attacks
- **XSS Protection**: Automatic HTML escaping and Content Security Policy (CSP) headers
- **Secure File Upload**: File type, size, and content validation for prescription uploads (max 5MB, 10 files)
- **Rate Limiting**: Prevents brute force attacks with configurable request limits (1000 requests/hour)
- **Security Headers**: HSTS, X-Frame-Options, X-Content-Type-Options, and CSP headers
- **Session Security**: HttpOnly and Secure cookie flags, session expiration (24 hours)
- **Input Validation**: Comprehensive validation for user inputs, phone numbers, and usernames
- **Password Security**: Strong password requirements with minimum length and complexity
- **Logging**: Security event logging for suspicious activities and authentication failures
- **Environment Variables**: Sensitive settings stored securely via environment variables
- **HTTPS Enforcement**: SSL redirect and secure cookie settings for production
- **Credential Security**: All API keys, secrets, and passwords stored in environment variables
- **Git Security**: Sensitive files (.env, API keys) properly excluded from version control
- **Middleware Security**: Custom security middleware for request monitoring and XSS detection
- **File Upload Security**: Restricted file types and size limits for prescription uploads

## 🌐 Internationalization

The application supports multiple languages:
- English (en)
- Hindi (hi)
- Marathi (mr)

Language preferences are stored per user and can be changed in the profile settings.

## 🚀 Deployment

### Render Deployment
The application is configured for deployment on Render with the following services:
- **Backend**: Django application deployed as a web service
- **Frontend**: Next.js application deployed as a web service
- **Database**: PostgreSQL database

### Production Setup
1. Set `DEBUG = False` in settings
2. Configure production database (PostgreSQL on Render)
3. Set up static file serving
4. Configure environment variables in Render dashboard
5. Deploy using `render.yaml` configuration file
6. Set up SSL certificate (handled by Render)

## 📞 Support & Contact

For support or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**HealthBridge 360** - Empowering rural healthcare through technology! 🏥💊
