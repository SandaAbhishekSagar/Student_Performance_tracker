# Student Attendance & Performance Tracker

A comprehensive web application for universities to manage courses, student enrollment, daily attendance, and performance insights. This MVP focuses on teacher workflows with a clean, modern interface built using Flask and Bootstrap 5.

## 🚀 Features

### Core Functionality
- **Course Management**: Create and manage courses with codes and descriptions
- **Student Enrollment**: Enroll students in courses with duplicate prevention
- **Bulk Enrollment**: Import students from CSV files
- **Session Management**: Create attendance sessions for specific dates with topics
- **Attendance Marking**: Mark attendance with four statuses (Present, Late, Excused, Absent) with notes
- **Performance Reports**: Generate detailed attendance percentage reports with weighted scoring
- **CSV Export**: Export students and attendance data to CSV for analysis
- **Responsive UI**: Modern Bootstrap 5 interface with mobile support

### Student Portal (NEW)
- **Personal Dashboard**: View all enrolled courses with attendance percentages
- **Attendance History**: See recent attendance records for each course
- **Grade Viewing**: View all grades and calculate overall averages
- **Real-time Updates**: See attendance status and performance metrics

### Gradebook Integration (NEW)
- **Grade Management**: Add, view, and manage student grades
- **Assignment Tracking**: Track different assignment types (exam, quiz, homework, project)
- **Grade Analytics**: Calculate student averages and total points
- **Organized View**: View grades by student or by assignment

### Security & Authentication (NEW)
- **Password Hashing**: Secure password storage using Werkzeug
- **CSRF Protection**: Built-in CSRF protection via Flask-WTF
- **Role-Based Access**: Teacher and student role separation
- **Session Management**: Secure session handling
- **Error Handling**: Comprehensive error handling and logging

### Attendance System
- **Weighted Scoring**: Present (100%), Late (75%), Excused (50%), Absent (0%)
- **Real-time Updates**: Live status indicators and progress tracking
- **Bulk Actions**: Mark all present/absent with one click
- **Data Persistence**: SQLite database with automatic initialization

## 🛠️ Technology Stack

- **Backend**: Python Flask 2.3.3
- **Security**: Flask-WTF 1.2.1 (CSRF protection), Werkzeug 2.3.7 (password hashing)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5.3.0, Bootstrap Icons
- **Templates**: Jinja2 templating engine
- **Data Export**: CSV import/export functionality
- **Styling**: Custom CSS with responsive design
- **Logging**: Built-in Python logging for error tracking

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Navigate to your project directory
cd D:\Phani_project

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Application
Open your browser and navigate to: `http://localhost:5000`

## 📖 User Guide

### Teacher Workflow

1. **Login**: Use any name and select "Teacher" role (password optional for demo mode)
2. **Create Course**: Click "New Course" and enter course details (name, code, description)
3. **Enroll Students**: 
   - Click "Enroll Student" to add individual students
   - Or use "Import from CSV" to bulk enroll students
4. **Create Session**: Click "New Session" to create an attendance session with optional topic
5. **Mark Attendance**: Select attendance status for each student with optional notes
6. **View Reports**: Click "Report" on any course to see attendance percentages
7. **Export Data**: Use "Export CSV" to download student or attendance data
8. **Manage Grades**: Click "Gradebook" to add and manage student grades

### Student Workflow

1. **Login**: Use your name and select "Student" role (password optional for demo mode)
2. **View Dashboard**: See all enrolled courses with attendance percentages
3. **Check Attendance**: View recent attendance records for each course
4. **View Grades**: See all grades and calculate overall averages

### Attendance Statuses
- **Present** (100% weight): Student attended on time
- **Late** (75% weight): Student arrived late
- **Excused** (50% weight): Student had a valid excuse
- **Absent** (0% weight): Student did not attend

## 🎯 Demo Script (5 Minutes)

### 1. Introduction (30 seconds)
- "This is a Student Attendance & Performance Tracker built for universities"
- "It helps teachers manage courses, enroll students, and track attendance with detailed reporting"

### 2. Live Demo (3 minutes)
1. **Login**: Enter "Demo Teacher" and select Teacher role
2. **Create Course**: Add "Mathematics 101"
3. **Enroll Students**: Add "John Doe", "Jane Smith", "Bob Johnson"
4. **Create Session**: Create today's session
5. **Mark Attendance**: Mark John as Present, Jane as Late, Bob as Absent
6. **View Report**: Show the attendance percentage report

### 3. Key Features (1 minute)
- Weighted scoring system
- Real-time status updates
- Responsive design
- Data persistence

### 4. New Features (30 seconds)
- ✅ Authentication system with password hashing
- ✅ CSV import/export functionality
- ✅ Student portal with personal dashboard
- ✅ Gradebook integration
- ✅ Enhanced security with CSRF protection

## 📊 Database Schema

### Core Tables
- **User**: Teacher/student information with password hashing
- **Course**: Course details with code and description
- **Student**: Student information with student ID and email
- **Enrollment**: Student-course relationships
- **Session**: Attendance sessions per course/date with topics
- **Attendance**: Individual attendance records with notes
- **Grade**: Grade records with assignment details, types, and due dates (NEW)

### Key Constraints
- Unique enrollment per student-course pair
- Unique session per course-date combination
- Unique attendance record per session-student pair
- Unique student ID per student (optional)

## 🔧 Configuration

### Environment Variables
```bash
# Database URL (default: SQLite)
export DATABASE_URL=sqlite:///student_tracker.db

# Secret key for sessions
export SECRET_KEY=your-secret-key-here
```

### Database Setup

**No manual database setup required!** The application automatically:

- ✅ Creates the database file (SQLite) on first startup
- ✅ Creates all tables automatically
- ✅ Initializes with demo teacher account
- ✅ Works with PostgreSQL/MySQL (tables auto-created)

**For SQLite (default)**: Database file is created in `instance/student_tracker.db` automatically.

**For PostgreSQL/MySQL**: Tables are created automatically when the app starts if they don't exist. Just configure the `DATABASE_URL` in your `.env` file.

**Database initialization happens:**
- Automatically when using Docker (via `start.py` script)
- Automatically when using `python start.py`
- On first request when running Gunicorn directly

**Manual initialization (optional):**
```bash
python -c "from app import init_db; init_db()"
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] Create course successfully
- [ ] Enroll students without duplicates
- [ ] Create sessions for different dates
- [ ] Mark attendance with all statuses
- [ ] Verify percentage calculations
- [ ] Test data persistence after restart
- [ ] Validate responsive design

### Test Data
The application includes sample data initialization for demo purposes.

## 🚀 Deployment

### Quick Start (Docker Compose - Recommended)

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd Phani_project
   ```

2. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env and set SECRET_KEY
   # Generate secret key: python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Deploy** (Database initializes automatically - no manual setup needed!)
   ```bash
   # Using deployment script (Linux/Mac)
   chmod +x deploy.sh
   ./deploy.sh
   
   # Or using deployment script (Windows)
   .\deploy.ps1
   
   # Or manually with Docker Compose
   docker-compose up -d
   ```

4. **Access Application**
   - Open browser: `http://localhost:5000`
   - View logs: `docker-compose logs -f`
   - Stop: `docker-compose down`
   
   **Note**: The database is automatically created on first startup. No manual database setup required!

### Deployment Options

#### Option 1: Docker Compose (Recommended)
Best for production with automatic restarts and easy management.

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

#### Option 2: Docker Standalone
For single-container deployments.

```bash
# Build image
docker build -t student-tracker:latest .

# Run container
docker run -d \
  --name student_tracker \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/instance:/app/instance \
  --restart unless-stopped \
  student-tracker:latest

# View logs
docker logs -f student_tracker
```

#### Option 3: Gunicorn (Direct)
For deployments without Docker.

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run with startup script (automatically initializes database)
python start.py

# Or run Gunicorn directly (database will initialize on first request)
gunicorn -c gunicorn_config.py app:app

# Or with custom settings
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

**Note**: The startup script (`start.py`) automatically initializes the database before starting Gunicorn. If you run Gunicorn directly, the database will be created on first request.

### Production Configuration

#### Environment Variables
Create a `.env` file with the following:

```bash
# Required
SECRET_KEY=your-secret-key-here  # Generate: python -c "import secrets; print(secrets.token_hex(32))"

# Database (SQLite for development)
DATABASE_URL=sqlite:///instance/student_tracker.db

# For PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost:5432/student_tracker

# For MySQL (production)
# DATABASE_URL=mysql://user:password@localhost:3306/student_tracker

# Gunicorn (optional)
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
```

#### Using PostgreSQL (Production)

1. **Update docker-compose.yml**: Uncomment the PostgreSQL service
2. **Update DATABASE_URL** in `.env`:
   ```bash
   DATABASE_URL=postgresql://student_tracker:password@db:5432/student_tracker
   ```
3. **Install PostgreSQL driver** (already in requirements.txt):
   ```bash
   pip install psycopg2-binary
   ```

### Deployment to Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI, then:
heroku create student-tracker-app
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set DATABASE_URL=postgresql://...
git push heroku main
```

#### DigitalOcean App Platform
1. Connect your GitHub repository
2. Select Python as runtime
3. Set environment variables in dashboard
4. Deploy automatically

#### AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 student-tracker

# Create and deploy
eb create student-tracker-env
eb deploy
```

#### Railway
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Production Considerations

- ✅ **Security**: CSRF protection enabled, password hashing implemented
- ✅ **Performance**: Gunicorn with multiple workers
- ✅ **Database**: Use PostgreSQL/MySQL for production (not SQLite)
- ✅ **SSL**: Set up SSL certificates (Let's Encrypt recommended)
- ✅ **Monitoring**: Add application monitoring (e.g., Sentry)
- ✅ **Backups**: Regular database backups
- ✅ **Logging**: Configure log rotation and aggregation

### Nginx Reverse Proxy (Optional)

For production with SSL and better performance:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Health Checks

The application includes health check endpoints:
- Main endpoint: `GET /`
- Health check: Docker healthcheck configured

### Troubleshooting Deployment

1. **Port already in use**
   ```bash
   # Find process
   lsof -i :5000  # Linux/Mac
   netstat -ano | findstr :5000  # Windows
   
   # Kill process or change port in docker-compose.yml
   ```

2. **Database errors**
   ```bash
   # Reset database (Docker)
   docker-compose down -v
   docker-compose up -d
   ```

3. **Permission errors**
   ```bash
   # Fix permissions
   chmod -R 755 instance
   chown -R appuser:appuser instance
   ```

## ✅ Implemented Enhancements (Finals)

### ✅ Phase 1: Authentication & Security
- ✅ Password hashing with Werkzeug
- ✅ Role-based access control (teacher/student decorators)
- ✅ Enhanced session management
- ✅ CSRF protection via Flask-WTF
- ✅ Comprehensive error handling and logging

### ✅ Phase 2: Data Management
- ✅ CSV import/export functionality for students and attendance
- ✅ Bulk student enrollment via CSV upload
- ✅ Data validation and error handling
- ✅ Export attendance reports to CSV

### ✅ Phase 3: Student Portal
- ✅ Student self-service portal with personal dashboard
- ✅ Personal attendance history per course
- ✅ Grade viewing with calculations
- ✅ Real-time attendance percentage tracking

### ✅ Phase 4: Gradebook Integration
- ✅ Complete gradebook system with assignment tracking
- ✅ Multiple assignment types (exam, quiz, homework, project, etc.)
- ✅ Grade analytics and averages
- ✅ Due date tracking
- ✅ Notes and additional information

## 🔮 Future Enhancements

### Advanced Features
- Email notifications for attendance and grades
- Mobile app support
- Advanced analytics and charts
- Backup and restore functionality
- Multi-semester support
- Course prerequisites and scheduling

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process using port 5000
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```

2. **Database errors**
   ```bash
   # Delete database file and restart
   rm student_tracker.db
   python app.py
   ```

3. **Module not found**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt
   ```

## 📝 License

This project is developed for educational purposes as part of a university course.

## 👥 Contributing

This is a student project. For production use, please implement proper security measures and testing.

## 📞 Support

For issues or questions, please refer to the project documentation or contact the development team.

---

**Note**: This is a production-ready application with comprehensive features including authentication, CSV import/export, student portal, and gradebook integration. For production deployment, ensure environment variables are properly configured and consider using PostgreSQL/MySQL instead of SQLite for better performance.
