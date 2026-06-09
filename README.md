# Web-Based-Task-Management-Application-for-SME-s
The main aim of the study is to develop an orderly task management system which eases the manner in which tasks are generated, discussed and handled on real-time.
# ServiceLink

A production-ready web application that connects local service providers with clients who need their services.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Design Decisions](#design-decisions)
- [Security](#security)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

ServiceLink is a web-based platform designed to bridge the gap between local service providers (cleaners, handymen, tutors, plumbers, etc.) and clients seeking their services. The platform provides a secure, intuitive interface for service discovery, booking management, and quality assurance through a comprehensive review system.

## ✨ Features

### For Clients
- 🔍 **Search & Filter**: Find services by category, location, and price range
- 📅 **Easy Booking**: Book available time slots with just a few clicks
- ⭐ **Reviews & Ratings**: Read honest reviews and leave feedback after service completion
- 📊 **Dashboard**: Manage all bookings in one place
- 🔔 **Status Tracking**: Monitor booking status (pending, confirmed, completed)

### For Service Providers
- 💼 **Service Management**: Create, edit, and manage multiple service offerings
- 📆 **Availability Control**: Set and manage available time slots
- 📈 **Booking Management**: View and manage incoming booking requests
- ⭐ **Reputation Building**: Build credibility through customer reviews
- 💰 **Flexible Pricing**: Set your own rates for services

### Platform Features
- 🔐 **Secure Authentication**: Password hashing and session management
- 👥 **Role-Based Access**: Separate interfaces for clients and providers
- 🛡️ **CSRF Protection**: Security against cross-site request forgery
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🚀 **RESTful API**: JSON endpoints for integration possibilities
- ✅ **Input Validation**: Comprehensive client and server-side validation

## 🛠️ Technology Stack

### Backend
- **Flask 3.0**: Modern Python web framework
- **SQLAlchemy 2.0**: Powerful ORM for database operations
- **Flask-Login**: User session management
- **Flask-Migrate**: Database migration management
- **Flask-WTF**: Form handling and validation
- **Werkzeug**: Password hashing and security utilities

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with custom properties
- **Bootstrap 5**: Responsive design framework
- **JavaScript (ES6+)**: Client-side interactivity
- **Jinja2**: Server-side templating

### Database
- **SQLite**: Development database (easy setup)
- **PostgreSQL**: Production-ready (via configuration)

### Testing
- **Pytest**: Comprehensive testing framework
- **Pytest-Flask**: Flask-specific test utilities

## 📁 Project Structure

```
servicelink/
│
├── app/
│   ├── __init__.py              # Application factory
│   ├── models.py                # Database models
│   ├── routes.py                # Route definitions and controllers
│   ├── forms.py                 # WTForms form classes
│   ├── errors.py                # Error handlers
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Custom styles
│   │   ├── js/
│   │   │   └── main.js          # JavaScript functionality
│   │   └── images/              # Static images
│   └── templates/
│       ├── base.html            # Base template
│       ├── index.html           # Homepage
│       ├── about.html           # About page
│       ├── search.html          # Search results
│       ├── service_detail.html  # Service detail page
│       ├── auth/                # Authentication templates
│       ├── client/              # Client dashboard templates
│       ├── provider/            # Provider dashboard templates
│       └── errors/              # Error page templates
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Test configuration and fixtures
│   └── test_app.py              # Unit tests
│
├── scripts/
│   └── seed_data.py             # Database seeding script
│
├── migrations/                   # Database migrations (generated)
│
├── config.py                     # Configuration settings
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd servicelink
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Seed the database (optional but recommended)**
   ```bash
   flask seed-db
   ```

## ⚙️ Configuration

The application supports three environments: development, testing, and production.

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database (for production)
DATABASE_URL=postgresql://username:password@localhost/servicelink

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
```

### Configuration Classes

- **DevelopmentConfig**: Debug mode enabled, SQLite database
- **TestingConfig**: Testing mode, in-memory database
- **ProductionConfig**: Production settings, PostgreSQL recommended

## 🏃 Running the Application

### Development Server

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Sample Credentials (after seeding)

**Clients:**
- Username: `john_doe` | Password: `password123`
- Username: `jane_smith` | Password: `password123`

**Providers:**
- Username: `clean_pro` | Password: `password123`
- Username: `handy_helper` | Password: `password123`

## 🧪 Testing

The application includes comprehensive unit tests covering:

1. User registration and authentication
2. Login functionality
3. Booking creation
4. Double booking prevention
5. Review submission

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_app.py -v

# Run specific test
pytest tests/test_app.py::TestUserAuthentication::test_user_registration -v
```

### Test Coverage

The test suite covers:
- ✅ User registration validation
- ✅ Authentication and authorization
- ✅ Booking creation and cancellation
- ✅ Double booking prevention
- ✅ Review submission for completed bookings
- ✅ Service management
- ✅ API endpoints

## 📡 API Documentation

### REST API Endpoints

#### Get Services List
```http
GET /api/services
```

**Query Parameters:**
- `category` (optional): Filter by service category
- `location` (optional): Filter by provider location
- `page` (optional): Page number for pagination
- `per_page` (optional): Items per page (default: 10)

**Response:**
```json
{
  "services": [
    {
      "id": 1,
      "service_name": "House Cleaning",
      "description": "Professional house cleaning",
      "category": "cleaning",
      "price": 45.0,
      "provider": {
        "id": 2,
        "username": "clean_pro",
        "location": "New York, NY"
      },
      "average_rating": 4.8,
      "created_at": "2026-02-16T10:30:00"
    }
  ],
  "total": 16,
  "page": 1,
  "pages": 2,
  "per_page": 10
}
```

#### Get Service Details
```http
GET /api/service/:id
```

**Response:**
```json
{
  "id": 1,
  "service_name": "House Cleaning",
  "description": "Professional house cleaning service",
  "category": "cleaning",
  "price": 45.0,
  "provider": {
    "id": 2,
    "username": "clean_pro",
    "location": "New York, NY",
    "bio": "Professional cleaning service...",
    "average_rating": 4.8
  },
  "average_rating": 4.9,
  "created_at": "2026-02-16T10:30:00",
  "available_slots": [
    {
      "id": 1,
      "date": "2026-02-17",
      "start_time": "09:00",
      "end_time": "10:00"
    }
  ]
}
```

## 🎨 Design Decisions

### Why Flask?

**Flask was chosen for several compelling reasons:**

1. **Lightweight & Flexible**: Flask's minimalist core allows us to add only the extensions we need, keeping the application lean and maintainable.

2. **Pythonic**: Flask follows Python idioms and conventions, making the codebase intuitive for Python developers.

3. **Excellent Documentation**: Comprehensive official documentation and a large community make problem-solving easier.

4. **Scalability**: While simple to start with, Flask scales well with proper architecture (blueprints, application factory pattern).

5. **Ecosystem**: Rich ecosystem of extensions (Flask-Login, Flask-SQLAlchemy, Flask-Migrate) that integrate seamlessly.

### Why SQLAlchemy?

**SQLAlchemy ORM provides significant advantages:**

1. **Database Abstraction**: Write Python code instead of SQL, making the application database-agnostic (easy switch from SQLite to PostgreSQL).

2. **Relationship Management**: Elegant handling of foreign keys and relationships between models.

3. **Query Building**: Intuitive query interface with method chaining for complex queries.

4. **Type Safety**: Python type hints and IDE autocompletion improve development experience.

5. **Migration Support**: Flask-Migrate (built on Alembic) provides robust database versioning.

### Why Bootstrap 5?

**Bootstrap was selected for frontend development:**

1. **Rapid Development**: Pre-built components and utilities accelerate UI development.

2. **Responsive by Default**: Mobile-first approach ensures compatibility across devices.

3. **Customizable**: CSS variables and Sass support allow easy theming.

4. **Well-Documented**: Extensive documentation with examples.

5. **Accessibility**: Built-in ARIA attributes and keyboard navigation support.

6. **Browser Compatibility**: Tested across all major browsers.

### Architecture Patterns

#### Application Factory Pattern
The app is created using a factory function (`create_app()`), enabling:
- Multiple instances with different configurations
- Easier testing with isolated contexts
- Cleaner code organization

#### Blueprint Organization
Routes are organized into blueprints:
- **main**: Public pages
- **auth**: Authentication
- **provider**: Provider dashboard
- **client**: Client dashboard
- **api**: REST API endpoints

#### MVC Pattern
- **Models** (`models.py`): Database schema and business logic
- **Views** (`routes.py`): Request handling and response generation
- **Templates** (`templates/`): Presentation layer

## 🔒 Security

### Security Measures Implemented

1. **Password Security**
   - Passwords hashed using Werkzeug's `generate_password_hash`
   - Uses PBKDF2-SHA256 algorithm
   - Salt automatically generated per password

2. **CSRF Protection**
   - Flask-WTF provides CSRF tokens for all forms
   - Tokens validated on form submission
   - Configurable token lifetime

3. **Session Management**
   - Secure session cookies (HttpOnly, SameSite)
   - Configurable session lifetime (24 hours default)
   - Server-side session storage

4. **Input Validation**
   - Server-side validation using WTForms
   - Client-side validation using HTML5 attributes
   - SQL injection prevention through ORM parameterization
   - XSS prevention through Jinja2 auto-escaping

5. **Role-Based Access Control**
   - `@role_required` decorator enforces access rules
   - Clients cannot access provider routes and vice versa
   - Database-level foreign key constraints

6. **Error Handling**
   - Generic error messages (no sensitive information leaked)
   - Custom error pages (404, 500, 403, 400)
   - Logging of errors for debugging

### Security Best Practices for Production

```python
# Set in production environment
SECRET_KEY = os.environ.get('SECRET_KEY')  # Strong, random key
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # Prevent XSS
DATABASE_URL = 'postgresql://...'  # Use PostgreSQL
```

## 🚀 Deployment

### Preparing for Production

1. **Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=<strong-random-key>
   export DATABASE_URL=postgresql://user:pass@localhost/dbname
   ```

2. **Database Migration**
   ```bash
   flask db upgrade
   ```

3. **Static Files**
   - Configure a CDN or nginx for static file serving
   - Enable gzip compression

### Deployment Options

#### Option 1: Traditional Server (Ubuntu + Nginx + Gunicorn)

1. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx postgresql
   ```

2. **Setup application**
   ```bash
   cd /var/www/servicelink
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

3. **Configure Gunicorn**
   ```bash
   gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app('production')"
   ```

4. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /static {
           alias /var/www/servicelink/app/static;
       }
   }
   ```

#### Option 2: Platform as a Service (Heroku)

1. **Create Procfile**
   ```
   web: gunicorn "app:create_app('production')"
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   git push heroku main
   heroku run flask db upgrade
   ```

#### Option 3: Docker

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app('production')"]
   ```

2. **Build and run**
   ```bash
   docker build -t servicelink .
   docker run -p 8000:8000 servicelink
   ```

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Enable HTTPS
- [ ] Set up error logging
- [ ] Configure email for notifications
- [ ] Set up automated backups
- [ ] Configure firewall rules
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Enable rate limiting
- [ ] Configure CORS if needed

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Write docstrings for all functions and classes
- Add unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 👤 Author

Created by Akella

## 🙏 Acknowledgments

- Flask documentation and community
- Bootstrap team for the excellent CSS framework
- SQLAlchemy contributors
- All open-source contributors whose libraries make this project possible

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Email: info@servicelink.com

---

**Built with ❤️ using Flask and Bootstrap**
