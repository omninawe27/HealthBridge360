# 🏥 HealthKart 360

**Healthcare for Rural India** - A comprehensive mobile-first healthcare web application designed specifically for rural Indian communities.

![HealthKart 360 Logo](https://via.placeholder.com/800x200/2c5aa0/ffffff?text=HealthKart+360+-+Healthcare+for+Rural+India)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

HealthKart 360 is a comprehensive healthcare management system built specifically for rural Indian communities. It bridges the gap between patients and pharmacies by providing easy access to medicines, prescription management, and healthcare services in multiple Indian languages.

### 🎯 Key Objectives

- **Accessibility**: Mobile-first design optimized for rural internet connectivity
- **Language Support**: Multi-language interface (English, Hindi, Marathi)
- **Medicine Access**: Easy medicine search and availability checking
- **Prescription Management**: Digital prescription upload and processing
- **Health Reminders**: Personalized medicine reminder system
- **Emergency Support**: 24x7 pharmacy access during emergencies

## ✨ Features

### 👤 User Module

- **🔐 Authentication & Registration**
  - Secure user registration with phone number verification
  - Multi-language preference selection
  - Profile management

- **📱 User Dashboard**
  - Quick access to all features
  - Order history and status tracking
  - Active reminders overview
  - Emergency mode access

- **🔍 Medicine Search**
  - Real-time medicine availability
  - Price comparison across pharmacies
  - Alternative medicine suggestions
  - Pharmacy location and distance

### 🏥 Pharmacist Module

- **📊 Pharmacy Dashboard**
  - Inventory management
  - Order processing and status updates
  - Low stock alerts
  - Sales analytics

- **💊 Medicine Management**
  - Add/Edit/Delete medicines
  - Stock level monitoring
  - Expiry date tracking
  - Batch number management

- **📋 Order Management**
  - Order processing workflow
  - Status updates (Pending → Confirmed → Preparing → Ready → Delivered)
  - Customer communication

### 🧾 Prescription System

- **📸 Upload & Processing**
  - Image upload for prescriptions
  - OCR integration (ready for implementation)
  - Manual medicine selection
  - Alternative suggestions

### ⏰ Reminder System

- **🔔 Medicine Reminders**
  - Time-based reminders (Morning, Afternoon, Evening, Night)
  - Custom alert types (Tone, Vibrate, Visual)
  - Personalized notes and instructions
  - Active/Inactive status management

### 🆘 Emergency Mode

- **24x7 Support**
  - Emergency pharmacy locator
  - Essential medicines availability
  - Quick contact options
  - Priority order processing

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: MySQL 8.0+
- **Authentication**: Django Auth System
- **File Handling**: Django File Storage

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Bootstrap 5.1.3 + Custom CSS
- **JavaScript**: Vanilla JS + Bootstrap JS
- **Icons**: Font Awesome 6.0

### Additional Libraries
- **Image Processing**: Pillow 10.1.0
- **Database Connector**: mysqlclient 2.2.0
- **Configuration**: python-decouple 3.8

## 🚀 Installation

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

### Step 1: Clone Repository

\`\`\`bash
git clone https://github.com/yourusername/healthkart-360.git
cd healthkart-360
\`\`\`

### Step 2: Create Virtual Environment

\`\`\`bash
python -m venv venv

# On Windows
venv\\Scripts\\activate

# On macOS/Linux
source venv/bin/activate
\`\`\`

### Step 3: Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Step 4: Database Setup

1. **Create MySQL Database**
\`\`\`sql
CREATE DATABASE healthkart360;
CREATE USER 'healthkart_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON healthkart360.* TO 'healthkart_user'@'localhost';
FLUSH PRIVILEGES;
\`\`\`

2. **Update Database Configuration**
Edit \`healthkart360/settings.py\`:
\`\`\`python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'healthkart360',
        'USER': 'healthkart_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
\`\`\`

### Step 5: Run Migrations

\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### Step 6: Create Superuser

\`\`\`bash
python manage.py createsuperuser
\`\`\`

### Step 7: Initialize Sample Data

\`\`\`bash
python scripts/init_database.py
\`\`\`

### Step 8: Run Development Server

\`\`\`bash
python manage.py runserver
\`\`\`

Visit \`http://127.0.0.1:8000\` to access the application.

## ⚙️ Configuration

### Environment Variables

Create a \`.env\` file in the project root:

\`\`\`env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_NAME=healthkart360
DATABASE_USER=healthkart_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
\`\`\`

### Media Files Configuration

Ensure media directory exists:
\`\`\`bash
mkdir media
mkdir media/prescriptions
\`\`\`

### Static Files

Collect static files for production:
\`\`\`bash
python manage.py collectstatic
\`\`\`

## 📖 Usage

### For Users

1. **Registration**
   - Visit the homepage
   - Click "Get Started" or "Register"
   - Fill in personal details and select preferred language
   - Complete registration

2. **Medicine Search**
   - Use the search bar on dashboard
   - Browse available medicines
   - Check prices and pharmacy locations
   - View alternative medicines

3. **Prescription Upload**
   - Go to "Upload Prescription"
   - Take a photo or upload prescription image
   - Select medicines and quantities
   - Place order

4. **Set Reminders**
   - Navigate to "Reminders"
   - Add medicine name and timing
   - Choose alert type
   - Save reminder

### For Pharmacists

1. **Pharmacy Registration**
   - Click "Register Pharmacy"
   - Fill pharmacy and owner details
   - Submit license information
   - Wait for approval

2. **Inventory Management**
   - Access pharmacy dashboard
   - Add new medicines
   - Update stock levels
   - Monitor expiry dates

3. **Order Processing**
   - View incoming orders
   - Update order status
   - Communicate with customers
   - Track deliveries

## 📚 API Documentation

### Authentication Endpoints

- \`POST /users/login/\` - User login
- \`POST /users/register/\` - User registration
- \`POST /users/logout/\` - User logout

### Medicine Endpoints

- \`GET /medicines/search/?q=medicine_name\` - Search medicines
- \`GET /medicines/alternatives/?medicine_id=1\` - Get alternatives
- \`POST /medicines/add/\` - Add medicine (Pharmacist only)

### Order Endpoints

- \`POST /orders/create/\` - Create new order
- \`GET /orders/my-orders/\` - Get user orders
- \`POST /orders/update-status/\<id\>/\` - Update order status

### Reminder Endpoints

- \`GET /reminders/\` - List user reminders
- \`POST /reminders/add/\` - Add new reminder
- \`PUT /reminders/edit/\<id\>/\` - Edit reminder

## 🏗️ Project Structure

\`\`\`
healthkart360/
├── healthkart360/          # Main project directory
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── core/                  # Core app (dashboard, search)
├── users/                 # User management
├── pharmacy/              # Pharmacy management
├── medicines/             # Medicine management
├── orders/                # Order processing
├── reminders/             # Reminder system
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── media/                 # User uploaded files
├── scripts/               # Utility scripts
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
\`\`\`

## 🧪 Testing

Run tests:
\`\`\`bash
python manage.py test
\`\`\`

Run specific app tests:
\`\`\`bash
python manage.py test users
python manage.py test medicines
\`\`\`

## 🚀 Deployment

### Production Settings

1. **Update settings for production**
\`\`\`python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
\`\`\`

2. **Configure static files**
\`\`\`bash
python manage.py collectstatic --noinput
\`\`\`

3. **Set up web server** (Apache/Nginx)

### Docker Deployment

\`\`\`dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
\`\`\`

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create feature branch**
   \`\`\`bash
   git checkout -b feature/amazing-feature
   \`\`\`
3. **Commit changes**
   \`\`\`bash
   git commit -m 'Add amazing feature'
   \`\`\`
4. **Push to branch**
   \`\`\`bash
   git push origin feature/amazing-feature
   \`\`\`
5. **Open Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Write meaningful commit messages
- Add tests for new features
- Update documentation
- Ensure mobile responsiveness

## 🐛 Known Issues

- OCR integration pending for prescription processing
- SMS notifications not implemented
- Payment gateway integration pending
- Real-time notifications need WebSocket implementation

## 🔮 Future Enhancements

- [ ] **OCR Integration** - Automatic prescription reading
- [ ] **SMS Notifications** - Order and reminder SMS
- [ ] **Payment Gateway** - Online payment processing
- [ ] **Maps Integration** - Pharmacy navigation
- [ ] **Push Notifications** - Real-time updates
- [ ] **Telemedicine** - Video consultation feature
- [ ] **AI Recommendations** - Smart medicine suggestions
- [ ] **Inventory Analytics** - Advanced reporting

## 📞 Support

For support and queries:

- **Email**: support@healthkart360.com
- **Phone**: +91-XXXX-XXXX-XX
- **Documentation**: [Wiki](https://github.com/yourusername/healthkart-360/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/healthkart-360/issues)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Bootstrap Team** - For the excellent CSS framework
- **Django Community** - For the robust web framework
- **Font Awesome** - For beautiful icons
- **Rural Healthcare Workers** - For inspiration and requirements

## 📊 Statistics

- **Languages**: 3 (English, Hindi, Marathi)
- **Database Tables**: 8+ core tables
- **API Endpoints**: 15+ RESTful endpoints
- **Templates**: 20+ responsive templates
- **Features**: 25+ core features

---

**Made with ❤️ for Rural India**

*HealthKart 360 - Bridging the healthcare gap in rural communities*
