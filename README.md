# HealthKart 360 - Healthcare Web Application

A comprehensive, mobile-first healthcare web application designed for rural Indian users. HealthKart 360 provides a simple, multilingual system that allows users to search for medicines locally, upload prescriptions, set medicine reminders, place orders, and access emergency help.

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
- **Email Integration**: SMTP-based email notifications for orders and reminders

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7 (Python)
- **Database**: MySQL
- **Frontend**: Next.js 15.2.4 (React, TypeScript), HTML5, CSS3, JavaScript (Tailwind CSS)
- **Package Manager**: pnpm
- **Authentication**: Django's built-in authentication system
- **File Upload**: Image upload for prescriptions
- **Geolocation**: Pharmacy location services
- **Caching**: Django's cache framework
- **Pagination**: Django pagination for large datasets

## 📋 Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd healthkart360
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

### 4. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE healthkart360 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Update database settings in healthkart360/settings.py if needed
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Initialize Sample Data
```bash
python scripts/init_database.py
```

### 8. Install Frontend Dependencies
```bash
pnpm install
```

### 9. Run Development Servers
```bash
# Terminal 1: Django backend
python manage.py runserver

# Terminal 2: Next.js frontend
pnpm dev
```

The application will be available at:
- **Backend API**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`

## 👥 Default Login Credentials

### Regular Users
- **Username**: `john_doe` | **Password**: `password123`
- **Username**: `jane_smith` | **Password**: `password123`
- **Username**: `raj_patel` | **Password**: `password123`

### Pharmacy Owners
- **Username**: `pharmacy1` | **Password**: `password123`
- **Username**: `pharmacy2` | **Password**: `password123`
- **Username**: `pharmacy3` | **Password**: `password123`

## 📱 Application Structure

```
healthkart360/
├── app/                      # Next.js components (if using)
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
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=mysql://username:password@localhost/healthkart360
```

### Database Configuration
Update `healthkart360/settings.py` with your database credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'healthkart360',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 📊 Database Models

### Core Models
- **User**: Extended user model with phone number and language preferences
- **Pharmacy**: Pharmacy information with location and operating hours
- **Medicine**: Medicine details with stock and pricing information
- **Order**: Order management with status tracking and advance order support
- **OrderItem**: Individual items within orders with advance order flags
- **AdvanceOrder**: Special orders for out-of-stock medicines
- **Reminder**: Medicine reminder system with time slots and automated scheduling
- **Notification**: Email and system notification management

### Key Relationships
- Users can place orders and set reminders
- Pharmacies have medicines and receive orders
- Medicines can have alternatives and belong to pharmacies
- Orders contain multiple order items (medicines)
- Advance orders are linked to regular orders after payment
- Notifications are sent for orders, reminders, and system events

## 🎨 UI/UX Features

### Design Principles
- **Mobile-First**: Optimized for mobile devices
- **Touch-Friendly**: Large buttons and touch targets
- **Icon-Based**: Extensive use of icons and emojis
- **Color-Coded**: Status indicators with colors
- **Responsive**: Works on all screen sizes

### Color Scheme
- **Primary**: #2c5aa0 (Blue)
- **Secondary**: #28a745 (Green)
- **Accent**: #ffc107 (Yellow)
- **Danger**: #dc3545 (Red)
- **Dark**: #343a40 (Dark Gray)

## 🔍 Key Features Explained

### Medicine Search
- Search by medicine name, brand, or generic name
- Filter by medicine type, price range, and availability
- View nearby pharmacies with distance information
- See alternative medicines if primary is unavailable

### Emergency Mode
- Quick access to 24x7 pharmacies
- Essential medicines listing
- Emergency contact numbers
- Location sharing capabilities

### Reminder System
- Set reminders for different time slots (Morning, Afternoon, Evening, Night)
- Customizable alert types (Tone, Vibrate, Visual)
- Add notes for specific instructions
- Track medicine adherence

### Order Management
- Shopping cart functionality
- Prescription upload support
- Order status tracking
- Alternative medicine suggestions

### Advance Orders
- Order medicines that are currently out of stock
- Pay upfront for advance orders
- Automatic conversion to regular orders when stock becomes available
- Pharmacist notifications for advance order processing
- Separate tracking for advance vs regular orders

### Automated Reminder System
- Background scheduler for medication reminders
- Configurable reminder intervals (every 5-10 minutes)
- Email notifications for upcoming medication times
- Support for multiple reminder time slots (Morning, Afternoon, Evening, Night)
- Automated service management with Windows Task Scheduler and Linux Cron
- Comprehensive logging and monitoring

## 🚀 Deployment

### Production Setup
1. Set `DEBUG = False` in settings
2. Configure production database
3. Set up static file serving
4. Configure web server (Nginx/Apache)
5. Set up SSL certificate
6. Configure environment variables

### Docker Deployment (Optional)
```bash
# Build Docker image
docker build -t healthkart360 .

# Run container
docker run -p 8000:8000 healthkart360
```

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📈 Performance Optimization

### Database Optimization
- Use database indexes for frequently queried fields
- Implement database connection pooling
- Optimize queries with select_related and prefetch_related

### Frontend Optimization
- Minify CSS and JavaScript files
- Use CDN for external libraries
- Implement lazy loading for images
- Enable browser caching

## 🔒 Security Features

- **CSRF Protection**: All forms protected against Cross-Site Request Forgery attacks
- **SQL Injection Prevention**: Django ORM prevents SQL injection attacks
- **XSS Protection**: Automatic HTML escaping and Content Security Policy (CSP) headers
- **Secure File Upload**: File type, size, and content validation for prescription uploads
- **Rate Limiting**: Prevents brute force attacks with configurable request limits
- **Security Headers**: HSTS, X-Frame-Options, X-Content-Type-Options, and CSP headers
- **Session Security**: HttpOnly and Secure cookie flags, session expiration
- **Input Validation**: Comprehensive validation for user inputs, phone numbers, and usernames
- **Password Security**: Strong password requirements with minimum length and complexity
- **Logging**: Security event logging for suspicious activities and authentication failures
- **Environment Variables**: Sensitive settings stored securely via environment variables
- **HTTPS Enforcement**: SSL redirect and secure cookie settings for production

## 🌐 Internationalization

The application supports multiple languages:
- English (en)
- Hindi (hi)
- Marathi (mr)

Language preferences are stored per user and can be changed in the profile settings.

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

## 📝 Changelog

### Version 1.1.2
- Security enhancements implemented
- Added comprehensive security middleware (rate limiting, security logging)
- Enhanced input validation for user registration and forms
- Improved file upload security with content validation
- Added security headers (HSTS, CSP, X-Frame-Options)
- Implemented environment variable usage for sensitive settings
- Strengthened password validation requirements
- Added security event logging and monitoring
- Updated documentation with detailed security features

### Version 1.1.1
- Performance optimizations implemented
- Optimized reminder sending to filter by time window in database
- Added database indexes on frequently queried fields (14 indexes added)
- Implemented caching for expensive queries
- Added pagination to inventory views to handle large datasets
- Optimized database queries with select_related and prefetch_related
- Removed unnecessary files and directories for cleaner codebase
- Updated tech stack documentation to include Next.js frontend

### Version 1.1.0
- Added Advance Orders feature for out-of-stock medicines
- Implemented Automated Reminder System with background scheduling
- Added Notifications app for email and system notifications
- Enhanced Order model with advance order support
- Added comprehensive logging and monitoring for reminder system
- Improved pharmacist dashboard with advance order management
- Added Windows Task Scheduler and Linux Cron support for automation

### Version 1.0.0
- Initial release
- Core functionality implemented
- User and pharmacist dashboards
- Medicine search and ordering
- Reminder system
- Emergency mode

## 🔮 Future Enhancements

- **OCR Integration**: Automatic prescription reading
- **Payment Gateway**: Online payment integration
- **Push Notifications**: Real-time notifications
- **Telemedicine**: Video consultation features
- **AI Recommendations**: Medicine recommendations
- **Analytics Dashboard**: Advanced reporting
- **Mobile App**: Native mobile applications

---

**HealthKart 360** - Empowering rural healthcare through technology! 🏥💊 