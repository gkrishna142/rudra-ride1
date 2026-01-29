# Rudra Admin Dashboard

A comprehensive admin dashboard for managing a ride-sharing platform (Rudra Ride) that supports multiple vehicle types including cabs, bikes, and auto-rickshaws. This full-stack application provides administrators with powerful tools to manage users, drivers, rides, payments, promotions, and more.

## 🚀 Features

### Core Functionality
- **Dashboard Analytics**: Real-time statistics and insights including:
  - Service type statistics (Cab, Bike, Auto)
  - Daily ride analytics with revenue tracking
  - Active rides and drivers monitoring
  - Revenue reports and trends
  - User activity metrics

- **User Management**: 
  - Customer profile management
  - User status tracking (Active, Inactive, Suspended)
  - User activity monitoring

- **Driver Management**:
  - Driver profile management
  - Driver activation status tracking
  - Driver performance analytics
  - Revenue tracking per driver

- **Ride Management**:
  - Complete ride lifecycle tracking
  - Ride status monitoring (Pending, Active, Completed, Cancelled)
  - Ride history and analytics
  - Service type filtering

- **Payment Management**:
  - Payment transaction tracking
  - Revenue analytics
  - Payment history

- **Promotion Management**:
  - Promo code creation and management
  - Discount configuration (Percentage/Fixed)
  - Usage tracking and limits
  - Expiration date management

- **Additional Features**:
  - Vehicle management
  - Complaint handling system
  - Notification management
  - Role-based permissions
  - Settings configuration
  - Theme customization (Light/Dark mode)

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 6.0
- **API**: Django REST Framework 3.16.1
- **Authentication**: Django REST Framework Simple JWT 5.5.1
- **Database**: PostgreSQL
- **Database Driver**: psycopg 3.3.2

### Frontend
- **Framework**: React 19.2.0
- **Routing**: React Router DOM 7.10.0
- **Icons**: React Icons 5.5.0
- **Build Tool**: Create React App (react-scripts 5.0.1)
- **Testing**: React Testing Library

## 📁 Project Structure

```
Rudra_Admin/
├── backend/
│   └── dist/
│       ├── admin_backend/          # Django project settings
│       │   ├── settings.py
│       │   ├── urls.py
│       │   ├── wsgi.py
│       │   └── asgi.py
│       ├── admin-frontend/         # Django app
│       │   ├── models.py           # Data models
│       │   ├── serializers.py      # API serializers
│       │   ├── views.py             # API views
│       │   ├── urls.py              # API routes
│       │   └── migrations/          # Database migrations
│       ├── manage.py
│       ├── requirements.txt
│       └── DASHBOARD_API_ENDPOINTS.md
│
└── frontend/
    └── dist/
        ├── src/
        │   ├── components/         # Reusable components
        │   │   ├── Layout/         # Layout components
        │   │   └── ThemeSettings/  # Theme configuration
        │   ├── context/            # React context providers
        │   ├── pages/              # Page components
        │   │   ├── Dashboard.js
        │   │   ├── UserManagement.js
        │   │   ├── DriverManagement.js
        │   │   ├── RideManagement.js
        │   │   ├── CustomerManagement.js
        │   │   ├── Payments.js
        │   │   ├── Promotions.js
        │   │   ├── Vehicles.js
        │   │   ├── Complaints.js
        │   │   ├── Notifications.js
        │   │   ├── Settings.js
        │   │   └── RolesPermissions.js
        │   ├── styles/             # Global styles
        │   ├── App.js              # Main app component
        │   └── index.js            # Entry point
        ├── public/                 # Static files
        ├── package.json
        └── README.md
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python**: 3.8 or higher
- **Node.js**: 14.x or higher
- **npm** or **yarn**: Latest version
- **PostgreSQL**: 12.x or higher
- **Git**: For version control

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Rudra_Admin
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend/dist

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration

1. Create a PostgreSQL database:
```sql
CREATE DATABASE rudraride_db;
```

2. Update database settings in `backend/dist/admin_backend/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rudraride_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. Run migrations:
```bash
python manage.py migrate
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd ../../frontend/dist

# Install dependencies
npm install
```

## 🚀 Running the Application

### Start Backend Server

```bash
# From backend/dist directory
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### Start Frontend Development Server

```bash
# From frontend/dist directory
npm start
```

The frontend application will be available at `http://localhost:3000`

## 📡 API Documentation

The API documentation is available in `backend/dist/DASHBOARD_API_ENDPOINTS.md`. 

### Key API Endpoints

#### Dashboard Endpoints
- `GET /api/dashboard/overview/` - Complete dashboard overview
- `GET /api/dashboard/service-types/` - Service type statistics
- `GET /api/dashboard/total-rides-daily/` - Daily ride statistics
- `GET /api/dashboard/active-stats-today/` - Today's active statistics
- `GET /api/dashboard/today-revenue/` - Today's revenue
- `GET /api/dashboard/active-users/` - Active users statistics
- `GET /api/dashboard/cab-driver-stats/` - Cab driver statistics

#### Resource Endpoints
- `GET /api/rides/` - List all rides
- `GET /api/drivers/` - List all drivers
- `GET /api/users/` - List all users

For detailed API documentation, refer to `backend/dist/DASHBOARD_API_ENDPOINTS.md`.

## ⚙️ Configuration

### Environment Variables

For production deployment, consider using environment variables for sensitive settings:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: List of allowed hostnames
- Database credentials
- JWT secret keys

### Security Settings

⚠️ **Important**: Before deploying to production:

1. Change the `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS` appropriately
4. Set up proper CORS configuration
5. Use environment variables for sensitive data
6. Enable HTTPS

## 🧪 Testing

### Backend Tests

```bash
cd backend/dist
python manage.py test
```

### Frontend Tests

```bash
cd frontend/dist
npm test
```

## 📦 Building for Production

### Frontend Build

```bash
cd frontend/dist
npm run build
```

This creates an optimized production build in the `build` directory.

### Backend Deployment

For production deployment:
1. Set `DEBUG = False` in settings
2. Configure static files serving
3. Set up a production WSGI server (e.g., Gunicorn)
4. Configure a reverse proxy (e.g., Nginx)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 👥 Support

For support, email [your-email@example.com] or create an issue in the repository.

## 🔄 Version History

- **v0.1.0** (Current)
  - Initial release
  - Core dashboard functionality
  - User, driver, and ride management
  - Payment and promotion management
  - Theme customization

---

**Built with ❤️ for Rudra Ride Administration**
