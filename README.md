# 🚗 Vehicle Parking App - V2

A comprehensive multi-user parking management system built with Vue.js and Flask. Manages multiple parking lots, real-time spot availability, and user reservations for 4-wheeler parking.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Vue.js](https://img.shields.io/badge/Vue.js-3.2.x-green)
![Flask](https://img.shields.io/badge/Flask-2.x-red)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.x-purple)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Background Tasks](#background-tasks)
- [Contributing](#contributing)

## ✨ Features

### For Users
- 🏢 **Parking Lot Discovery** - Browse available parking locations
- ⚡ **Quick Booking** - One-click reservation system
- 📊 **Reservation Management** - Track active and historical bookings
- 💰 **Automatic Billing** - Cost calculation based on parking duration
- 📤 **Data Export** - Download parking history as CSV

### For Administrators
- 🏗️ **Lot Management** - Create, update, and delete parking facilities
- 👥 **User Management** - View and manage registered users
- 📈 **Analytics Dashboard** - Revenue and utilization insights
- 🔍 **Advanced Search** - Query system by various criteria
- 📱 **Real-time Monitoring** - Live parking spot status

### Technical Features
- 🔐 **Secure Authentication** - JWT-based user authentication
- 📱 **Responsive Design** - Works on desktop and mobile
- ⚡ **Real-time Updates** - Live data without page refresh
- 🚀 **Background Tasks** - Automated reminders and reports
- 📊 **Data Visualization** - Charts and analytics

## 🛠️ Tech Stack

### Backend
- **Python 3.x** - Core programming language
- **Flask 2.x** - Web framework for API development
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication system
- **Celery** - Background task processing
- **SQLite** - Database (development)

### Frontend
- **Vue.js 3.2.x** - Progressive JavaScript framework
- **Bootstrap 5.3.x** - CSS framework
- **Chart.js 4.5.x** - Data visualization
- **Axios** - HTTP client for API calls
- **FontAwesome** - Icon library

### Development Tools
- **Vue CLI** - Frontend build tools
- **Flask-SQLAlchemy** - Database operations
- **Flask-JWT-Extended** - JWT implementation
- **Flask-Mail** - Email functionality

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Node.js 14+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dotcomaki/parking-app.git
   cd parking-app
   ```

2. **Use the setup scripts**
   ```bash
   # Make scripts executable
   chmod +x start.sh start_demo.sh
   
   # For full setup and start
   ./start.sh
   
   # OR for demo mode
   ./start_demo.sh
   ```

3. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:5000

## 📁 Project Structure

```
parkingapp/
├── 📁 backend/                 # Flask API server
│   ├── 📄 app.py              # Main Flask application
│   ├── 📄 models.py           # Database models
│   ├── 📄 config.py           # Configuration settings
│   ├── 📄 tasks.py            # Celery background tasks
│   ├── 📄 requirements.txt    # Python dependencies
│   └── 📁 routes/             # API route definitions
│       ├── 📄 auth.py         # Authentication routes
│       ├── 📄 user.py         # User routes
│       └── 📄 admin.py        # Admin routes
├── 📁 frontend/               # Vue.js client application
│   ├── 📄 package.json       # Node.js dependencies
│   ├── 📁 src/               # Source code
│   │   ├── 📄 App.vue        # Main Vue component
│   │   ├── 📄 main.js        # Application entry point
│   │   └── 📁 components/    # Vue components
│   └── 📁 public/            # Static assets
├── 📄 start.sh               # Production startup script
├── 📄 start_demo.sh          # Demo startup script
├── 📄 run_daily_reminder.py  # Daily notification script
├── 📄 run_monthly_report.py  # Monthly report script
└── 📄 README.md              # This file
```

## 🔧 Setup Instructions

### Method 1: Using Startup Scripts (Recommended)

The easiest way to get started:

```bash
# Demo mode with sample data
./start_demo.sh

# Full production setup
./start.sh
```

### Method 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

5. **Create admin user**
   ```bash
   python create_admin.py
   ```

6. **Start Flask server**
   ```bash
   python app.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run serve
   ```

#### Celery Setup (Optional - for background tasks)

1. **Start Celery worker**
   ```bash
   cd backend
   celery -A celery_app.celery worker --loglevel=info
   ```

2. **Start Celery beat (for scheduled tasks)**
   ```bash
   celery -A celery_app.celery beat --loglevel=info
   ```

## 🏃‍♂️ Running the Application

### Development Mode

1. **Start backend** (Terminal 1)
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. **Start frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run serve
   ```

3. **Optional: Start Celery** (Terminal 3)
   ```bash
   cd backend
   celery -A celery_app.celery worker --loglevel=info
   ```

### Production Mode

Use the provided startup script:
```bash
./start.sh
```

This script will:
- Set up the backend with proper configuration
- Build the frontend for production
- Start all necessary services
- Initialize the database with sample data

## 📚 API Documentation

### Authentication Endpoints
```
POST /auth/register    # User registration
POST /auth/login      # User login
POST /auth/logout     # User logout
GET  /auth/me         # Get current user
```

### User Endpoints
```
GET  /user/lots                 # List parking lots
POST /user/reservations        # Create reservation
GET  /user/reservations        # Get user reservations
PUT  /user/reservations/<id>   # Update reservation
GET  /user/summary            # User statistics
```

### Admin Endpoints
```
GET    /admin/lots         # Manage parking lots
POST   /admin/lots         # Create parking lot
GET    /admin/users        # View all users
GET    /admin/summary      # System analytics
```

### Response Format
```json
{
  "data": {...},
  "message": "Success",
  "error": null
}
```

## 🤖 Background Tasks

### Daily Reminders
Send Google Chat notifications to users who haven't parked:
```bash
python run_daily_reminder.py
```

### Monthly Reports
Generate and email monthly analytics:
```bash
python run_monthly_report.py
```

### Setup Automated Tasks

**Linux/Mac (Crontab):**
```bash
# Daily reminders at 9 AM
0 9 * * * cd /path/to/project && python run_daily_reminder.py

# Monthly reports on 1st day at 8 AM
0 8 1 * * cd /path/to/project && python run_monthly_report.py
```

## 🎯 Default Admin

After running the setup, you can login with:

**Admin User:**
- Username: `admin`
- Password: `adminadmin`


## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
GOOGLE_CHAT_WEBHOOK_URL=your-webhook-url
```

### Database Configuration
- Development: SQLite (default)
- Production: PostgreSQL (recommended)

## 🛠️ Development

### Adding New Features

1. **Backend**: Add routes in `backend/routes/`
2. **Frontend**: Add components in `frontend/src/components/`
3. **Database**: Update models in `backend/models.py`

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm run test
```

## 📖 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Mohammad Akif**  


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/dotcomaki/parking-app/issues) page
2. Create a new issue with detailed information
3. Include error logs and steps to reproduce

---