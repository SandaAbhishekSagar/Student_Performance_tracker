from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os
import csv
import io
import logging
import threading
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# Handle postgres:// URLs (convert to postgresql:// for SQLAlchemy)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///student_tracker.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Models
class User(db.Model):
    __tablename__ = 'user'  # Explicit table name for PostgreSQL compatibility
    __table_args__ = {'quote': True}  # Quote table name since 'user' is a PostgreSQL reserved keyword
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='teacher')  # teacher, student, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        if not self.password_hash:
            return True  # Allow login without password for backward compatibility
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', backref='courses')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Student {self.full_name}>'

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='enrollments')
    student = db.relationship('Student', backref='enrollments')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('course_id', 'student_id', name='unique_enrollment'),)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    topic = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='sessions')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('course_id', 'session_date', name='unique_session'),)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Late, Excused
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = db.relationship('Session', backref='attendance_records')
    student = db.relationship('Student', backref='attendance_records')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('session_id', 'student_id', name='unique_attendance'),)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    assignment_name = db.Column(db.String(200), nullable=False)
    grade_value = db.Column(db.Float, nullable=False)
    max_points = db.Column(db.Float, default=100.0)
    assignment_type = db.Column(db.String(50), nullable=True)  # exam, quiz, homework, project
    due_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='grades')
    student = db.relationship('Student', backref='grades')

# Attendance status weights
ATTENDANCE_WEIGHTS = {
    'Present': 1.0,
    'Late': 0.75,
    'Excused': 0.5,
    'Absent': 0.0
}

# Decorators
def login_required(f):
    """Require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Require user to be a teacher"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'teacher':
            flash('Access denied. Teacher access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Require user to be a student"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'student':
            flash('Access denied. Student access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@csrf.exempt  # Exempt for backward compatibility
def login():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'teacher')
        
        if not name:
            flash('Please enter your name', 'error')
            return render_template('login.html')
        
        # Find user
        user = User.query.filter_by(name=name, role=role).first()
        
        # If user doesn't exist, create one (backward compatibility)
        if not user:
            user = User(name=name, role=role)
            if password:
                user.set_password(password)
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {name} ({role})")
        else:
            # Check password if set
            if not user.check_password(password):
                flash('Invalid credentials', 'error')
                return render_template('login.html')
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_role'] = user.role
        
        if role == 'teacher':
            return redirect(url_for('teacher_dashboard', teacher_id=user.id))
        elif role == 'student':
            return redirect(url_for('student_dashboard', student_id=user.id))
        else:
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/teacher/<int:teacher_id>')
@login_required
@teacher_required
def teacher_dashboard(teacher_id):
    if session.get('user_id') != teacher_id:
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    try:
        courses = Course.query.filter_by(teacher_id=teacher_id).order_by(Course.created_at.desc()).all()
        recent_sessions = Session.query.join(Course).filter(
            Course.teacher_id == teacher_id
        ).order_by(Session.session_date.desc()).limit(5).all()
        
        # Calculate statistics
        total_students = db.session.query(Student).join(Enrollment).join(Course).filter(
            Course.teacher_id == teacher_id
        ).distinct().count()
        
        return render_template('teacher_dashboard.html', 
                             courses=courses, 
                             recent_sessions=recent_sessions,
                             teacher_name=session.get('user_name'),
                             total_students=total_students)
    except Exception as e:
        logger.error(f"Error in teacher_dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard', 'error')
        return redirect(url_for('index'))

@app.route('/student/<int:student_id>')
@login_required
@student_required
def student_dashboard(student_id):
    # student_id here is actually user_id from session
    if session.get('user_id') != student_id:
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    try:
        # Get user record
        user = User.query.get(student_id)
        if not user:
            flash('User record not found', 'error')
            return redirect(url_for('index'))
        
        # Find student record by matching user name to student full_name
        student = Student.query.filter_by(full_name=user.name).first()
        
        if not student:
            flash('Student record not found. Please contact your teacher to enroll you in courses.', 'error')
            return redirect(url_for('index'))
        
        # Get enrollments
        enrollments = Enrollment.query.filter_by(student_id=student.id).all()
        courses_data = []
        
        for enrollment in enrollments:
            course = enrollment.course
            course_sessions = Session.query.filter_by(course_id=course.id).order_by(Session.session_date).all()
            
            # Calculate attendance percentage
            total_sessions = len(course_sessions)
            if total_sessions == 0:
                percentage = 0.0
            else:
                total_weight = 0.0
                for course_session in course_sessions:
                    attendance = Attendance.query.filter_by(
                        session_id=course_session.id,
                        student_id=student.id
                    ).first()
                    if attendance:
                        total_weight += ATTENDANCE_WEIGHTS.get(attendance.status, 0.0)
                    else:
                        total_weight += ATTENDANCE_WEIGHTS['Absent']
                percentage = (total_weight / total_sessions) * 100
            
            # Get recent attendance
            recent_attendance = db.session.query(Attendance, Session).join(
                Session, Attendance.session_id == Session.id
            ).filter(
                Attendance.student_id == student.id,
                Session.course_id == course.id
            ).order_by(Session.session_date.desc()).limit(5).all()
            
            # Get grades
            grades = Grade.query.filter_by(
                course_id=course.id,
                student_id=student.id
            ).order_by(Grade.created_at.desc()).all()
            
            courses_data.append({
                'course': course,
                'percentage': round(percentage, 1),
                'total_sessions': total_sessions,
                'recent_attendance': recent_attendance,
                'grades': grades
            })
        
        return render_template('student_dashboard.html',
                             student=student,
                             courses_data=courses_data)
    except Exception as e:
        logger.error(f"Error in student_dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard', 'error')
        return redirect(url_for('index'))

@app.route('/course/new', methods=['GET', 'POST'])
@csrf.exempt  # Exempt for backward compatibility
@login_required
@teacher_required
def create_course():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Course name is required', 'error')
            return render_template('course_form.html')
        
        try:
            course = Course(
                name=name,
                code=code or None,
                description=description or None,
                teacher_id=session.get('user_id')
            )
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully!', 'success')
            logger.info(f"Course created: {name} by teacher {session.get('user_id')}")
            return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating course: {str(e)}")
            flash('An error occurred while creating the course', 'error')
            return render_template('course_form.html')
    
    return render_template('course_form.html')

@app.route('/student/new', methods=['GET', 'POST'])
@csrf.exempt  # Exempt for backward compatibility
@login_required
@teacher_required
def create_student():
    courses = Course.query.filter_by(teacher_id=session.get('user_id')).all()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        email = request.form.get('email', '').strip()
        course_id = request.form.get('course_id', type=int)
        
        if not full_name or not course_id:
            flash('Student name and course selection are required', 'error')
            return render_template('student_form.html', courses=courses)
        
        # Verify the course belongs to the current teacher
        course = Course.query.filter_by(id=course_id, teacher_id=session.get('user_id')).first()
        if not course:
            flash('Invalid course selection', 'error')
            return render_template('student_form.html', courses=courses)
        
        try:
            # Check if student already exists
            existing_student = Student.query.filter_by(full_name=full_name).first()
            if not existing_student:
                # Check for duplicate student_id if provided
                if student_id:
                    duplicate = Student.query.filter_by(student_id=student_id).first()
                    if duplicate:
                        flash(f'Student ID {student_id} already exists', 'error')
                        return render_template('student_form.html', courses=courses)
                
                # Create new student
                student = Student(
                    full_name=full_name,
                    student_id=student_id or None,
                    email=email or None
                )
                db.session.add(student)
                db.session.flush()
            else:
                student = existing_student
            
            # Check if already enrolled
            existing_enrollment = Enrollment.query.filter_by(
                course_id=course_id,
                student_id=student.id
            ).first()
            
            if existing_enrollment:
                flash('Student is already enrolled in this course', 'error')
                return render_template('student_form.html', courses=courses)
            
            # Create enrollment
            enrollment = Enrollment(course_id=course_id, student_id=student.id)
            db.session.add(enrollment)
            db.session.commit()
            
            flash('Student enrolled successfully!', 'success')
            logger.info(f"Student enrolled: {full_name} in course {course_id}")
            return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error enrolling student: {str(e)}")
            flash('An error occurred while enrolling the student', 'error')
            return render_template('student_form.html', courses=courses)
    
    return render_template('student_form.html', courses=courses)

@app.route('/session/new', methods=['GET', 'POST'])
@csrf.exempt  # Exempt for backward compatibility
@login_required
@teacher_required
def create_session():
    courses = Course.query.filter_by(teacher_id=session.get('user_id')).all()
    
    if request.method == 'POST':
        course_id = request.form.get('course_id', type=int)
        session_date_str = request.form.get('session_date', '')
        topic = request.form.get('topic', '').strip()
        
        if not course_id or not session_date_str:
            flash('Course and date are required', 'error')
            return render_template('session_form.html', courses=courses)
        
        # Verify the course belongs to the current teacher
        course = Course.query.filter_by(id=course_id, teacher_id=session.get('user_id')).first()
        if not course:
            flash('Invalid course selection', 'error')
            return render_template('session_form.html', courses=courses)
        
        try:
            session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('session_form.html', courses=courses)
        
        # Check if session already exists
        existing_session = Session.query.filter_by(
            course_id=course_id,
            session_date=session_date
        ).first()
        
        if existing_session:
            flash('Session already exists for this course and date', 'error')
            return render_template('session_form.html', courses=courses)
        
        try:
            session_obj = Session(
                course_id=course_id,
                session_date=session_date,
                topic=topic or None
            )
            db.session.add(session_obj)
            db.session.commit()
            flash('Session created successfully!', 'success')
            logger.info(f"Session created for course {course_id} on {session_date}")
            return redirect(url_for('mark_attendance', session_id=session_obj.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating session: {str(e)}")
            flash('An error occurred while creating the session', 'error')
            return render_template('session_form.html', courses=courses)
    
    return render_template('session_form.html', courses=courses)

@app.route('/attendance/<int:session_id>', methods=['GET', 'POST'])
@csrf.exempt  # Exempt for backward compatibility
@login_required
@teacher_required
def mark_attendance(session_id):
    session_obj = Session.query.get_or_404(session_id)
    course = Course.query.filter_by(id=session_obj.course_id, teacher_id=session.get('user_id')).first()
    
    if not course:
        flash('Access denied - You can only mark attendance for your own courses', 'error')
        return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
    
    # Get enrolled students
    enrollments = db.session.query(Enrollment, Student).join(
        Student, Enrollment.student_id == Student.id
    ).filter(Enrollment.course_id == session_obj.course_id).all()
    
    if request.method == 'POST':
        try:
            # Process attendance data
            for enrollment, student in enrollments:
                status = request.form.get(f'status_{student.id}')
                notes = request.form.get(f'notes_{student.id}', '').strip()
                
                if status:
                    # Check if attendance record exists
                    attendance = Attendance.query.filter_by(
                        session_id=session_id,
                        student_id=student.id
                    ).first()
                    
                    if attendance:
                        attendance.status = status
                        attendance.notes = notes or None
                        attendance.updated_at = datetime.utcnow()
                    else:
                        attendance = Attendance(
                            session_id=session_id,
                            student_id=student.id,
                            status=status,
                            notes=notes or None
                        )
                        db.session.add(attendance)
            
            db.session.commit()
            flash('Attendance saved successfully!', 'success')
            return redirect(url_for('mark_attendance', session_id=session_id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving attendance: {str(e)}")
            flash('An error occurred while saving attendance', 'error')
    
    # Get existing attendance records
    attendance_records = {}
    for attendance in Attendance.query.filter_by(session_id=session_id).all():
        attendance_records[attendance.student_id] = {
            'status': attendance.status,
            'notes': attendance.notes
        }
    
    return render_template('attendance_form.html', 
                         session=session_obj, 
                         course=course,
                         enrollments=enrollments,
                         attendance_records=attendance_records,
                         teacher_id=session.get('user_id'))

@app.route('/report/<int:course_id>')
@login_required
@teacher_required
def attendance_report(course_id):
    course = Course.query.filter_by(id=course_id, teacher_id=session.get('user_id')).first()
    if not course:
        flash('Access denied - You can only view reports for your own courses', 'error')
        return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
    
    try:
        # Get all sessions for this course
        course_sessions = Session.query.filter_by(course_id=course_id).order_by(Session.session_date).all()
        
        # Get enrolled students
        enrollments = db.session.query(Enrollment, Student).join(
            Student, Enrollment.student_id == Student.id
        ).filter(Enrollment.course_id == course_id).all()
        
        # Calculate attendance percentages
        student_reports = []
        for enrollment, student in enrollments:
            total_sessions = len(course_sessions)
            if total_sessions == 0:
                percentage = 0.0
            else:
                total_weight = 0.0
                for course_session in course_sessions:
                    attendance = Attendance.query.filter_by(
                        session_id=course_session.id,
                        student_id=student.id
                    ).first()
                    
                    if attendance:
                        total_weight += ATTENDANCE_WEIGHTS.get(attendance.status, 0.0)
                    else:
                        total_weight += ATTENDANCE_WEIGHTS['Absent']
                
                percentage = (total_weight / total_sessions) * 100
            
            student_reports.append({
                'student': student,
                'percentage': round(percentage, 1),
                'total_sessions': total_sessions
            })
        
        # Sort by percentage (descending)
        student_reports.sort(key=lambda x: x['percentage'], reverse=True)
        
        return render_template('attendance_report.html', 
                             course=course,
                             student_reports=student_reports,
                             total_sessions=len(course_sessions),
                             teacher_id=session.get('user_id'))
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        flash('An error occurred while generating the report', 'error')
        return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))

# CSV Import/Export Routes
@app.route('/export/students/<int:course_id>')
@login_required
@teacher_required
def export_students(course_id):
    """Export students for a course to CSV"""
    course = Course.query.filter_by(id=course_id, teacher_id=session.get('user_id')).first()
    if not course:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
    
    try:
        enrollments = db.session.query(Enrollment, Student).join(
            Student, Enrollment.student_id == Student.id
        ).filter(Enrollment.course_id == course_id).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student ID', 'Full Name', 'Email', 'Enrolled Date'])
        
        for enrollment, student in enrollments:
            writer.writerow([
                student.student_id or '',
                student.full_name,
                student.email or '',
                enrollment.enrolled_at.strftime('%Y-%m-%d') if enrollment.enrolled_at else ''
            ])
        
        output.seek(0)
        filename = f"{course.name.replace(' ', '_')}_students_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error exporting students: {str(e)}")
        flash('An error occurred while exporting students', 'error')
        return redirect(url_for('attendance_report', course_id=course_id))

@app.route('/export/attendance/<int:course_id>')
@login_required
@teacher_required
def export_attendance(course_id):
    """Export attendance data for a course to CSV"""
    course = Course.query.filter_by(id=course_id, teacher_id=session.get('user_id')).first()
    if not course:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
    
    try:
        course_sessions = Session.query.filter_by(course_id=course_id).order_by(Session.session_date).all()
        enrollments = db.session.query(Enrollment, Student).join(
            Student, Enrollment.student_id == Student.id
        ).filter(Enrollment.course_id == course_id).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        header = ['Student ID', 'Full Name']
        for sess in course_sessions:
            header.append(sess.session_date.strftime('%Y-%m-%d'))
        writer.writerow(header)
        
        # Data rows
        for enrollment, student in enrollments:
            row = [student.student_id or '', student.full_name]
            for sess in course_sessions:
                attendance = Attendance.query.filter_by(
                    session_id=sess.id,
                    student_id=student.id
                ).first()
                row.append(attendance.status if attendance else 'Absent')
            writer.writerow(row)
        
        output.seek(0)
        filename = f"{course.name.replace(' ', '_')}_attendance_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error exporting attendance: {str(e)}")
        flash('An error occurred while exporting attendance', 'error')
        return redirect(url_for('attendance_report', course_id=course_id))

@app.route('/import/students/<int:course_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def import_students(course_id):
    """Import students from CSV file"""
    course = Course.query.filter_by(id=course_id, teacher_id=session.get('user_id')).first()
    if not course:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided', 'error')
            return redirect(url_for('attendance_report', course_id=course_id))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('attendance_report', course_id=course_id))
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file', 'error')
            return redirect(url_for('attendance_report', course_id=course_id))
        
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            imported = 0
            skipped = 0
            errors = []
            
            for row in csv_reader:
                try:
                    full_name = row.get('Full Name', '').strip()
                    if not full_name:
                        skipped += 1
                        continue
                    
                    student_id = row.get('Student ID', '').strip()
                    email = row.get('Email', '').strip()
                    
                    # Find or create student
                    student = Student.query.filter_by(full_name=full_name).first()
                    if not student:
                        # Check for duplicate student_id
                        if student_id:
                            existing = Student.query.filter_by(student_id=student_id).first()
                            if existing:
                                student = existing
                            else:
                                student = Student(
                                    full_name=full_name,
                                    student_id=student_id or None,
                                    email=email or None
                                )
                                db.session.add(student)
                                db.session.flush()
                        else:
                            student = Student(full_name=full_name, email=email or None)
                            db.session.add(student)
                            db.session.flush()
                    
                    # Check if already enrolled
                    existing_enrollment = Enrollment.query.filter_by(
                        course_id=course_id,
                        student_id=student.id
                    ).first()
                    
                    if not existing_enrollment:
                        enrollment = Enrollment(course_id=course_id, student_id=student.id)
                        db.session.add(enrollment)
                        imported += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append(f"Row {full_name}: {str(e)}")
                    continue
            
            db.session.commit()
            flash(f'Successfully imported {imported} students. {skipped} skipped.', 'success')
            if errors:
                logger.warning(f"Import errors: {errors}")
            logger.info(f"Imported {imported} students to course {course_id}")
            return redirect(url_for('attendance_report', course_id=course_id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error importing students: {str(e)}")
            flash(f'Error importing students: {str(e)}', 'error')
            return redirect(url_for('attendance_report', course_id=course_id))
    
    return redirect(url_for('attendance_report', course_id=course_id))

# Gradebook Routes
@app.route('/grades/<int:course_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def manage_grades(course_id):
    """Manage grades for a course"""
    course = Course.query.filter_by(id=course_id, teacher_id=session.get('user_id')).first()
    if not course:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
    
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        assignment_name = request.form.get('assignment_name', '').strip()
        grade_value = request.form.get('grade_value', type=float)
        max_points = request.form.get('max_points', type=float) or 100.0
        assignment_type = request.form.get('assignment_type', '').strip()
        due_date_str = request.form.get('due_date', '')
        notes = request.form.get('notes', '').strip()
        
        if not student_id or not assignment_name or grade_value is None:
            flash('Student, assignment name, and grade are required', 'error')
            return redirect(url_for('manage_grades', course_id=course_id))
        
        try:
            due_date = None
            if due_date_str:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            grade = Grade(
                course_id=course_id,
                student_id=student_id,
                assignment_name=assignment_name,
                grade_value=grade_value,
                max_points=max_points,
                assignment_type=assignment_type or None,
                due_date=due_date,
                notes=notes or None
            )
            db.session.add(grade)
            db.session.commit()
            flash('Grade added successfully!', 'success')
            logger.info(f"Grade added for student {student_id} in course {course_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding grade: {str(e)}")
            flash('An error occurred while adding the grade', 'error')
    
    # Get enrolled students
    enrollments = db.session.query(Enrollment, Student).join(
        Student, Enrollment.student_id == Student.id
    ).filter(Enrollment.course_id == course_id).all()
    
    # Get all grades for this course
    grades = Grade.query.filter_by(course_id=course_id).order_by(
        Grade.assignment_name, Grade.created_at
    ).all()
    
    # Organize grades by student
    student_grades = {}
    for grade in grades:
        if grade.student_id not in student_grades:
            student_grades[grade.student_id] = []
        student_grades[grade.student_id].append(grade)
    
    return render_template('gradebook.html',
                         course=course,
                         enrollments=enrollments,
                         student_grades=student_grades,
                         grades=grades)

@app.route('/grades/<int:grade_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_grade(grade_id):
    """Delete a grade"""
    grade = Grade.query.get_or_404(grade_id)
    course = Course.query.filter_by(id=grade.course_id, teacher_id=session.get('user_id')).first()
    
    if not course:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard', teacher_id=session.get('user_id')))
    
    try:
        course_id = grade.course_id
        db.session.delete(grade)
        db.session.commit()
        flash('Grade deleted successfully', 'success')
        return redirect(url_for('manage_grades', course_id=course_id))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting grade: {str(e)}")
        flash('An error occurred while deleting the grade', 'error')
        return redirect(url_for('manage_grades', course_id=grade.course_id))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    flash('Page not found', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    flash('An internal error occurred', 'error')
    return redirect(url_for('index'))

# Initialize database
def init_db():
    """Initialize database tables and create default data if needed"""
    try:
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Create demo teacher if not exists
        try:
            if not User.query.filter_by(role='teacher').first():
                teacher = User(name='Demo Teacher', role='teacher')
                db.session.add(teacher)
                db.session.commit()
                logger.info("Created demo teacher")
        except Exception as e:
            logger.warning(f"Could not create demo teacher (tables might not exist yet): {str(e)}")
            db.session.rollback()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# Initialize database on first request (for gunicorn when start.py isn't used)
# Use a set to track which workers have initialized (thread-safe check)
_db_initialized = set()
_db_lock = threading.Lock()

@app.before_request
def ensure_db_initialized():
    """Ensure database is initialized before first request"""
    worker_id = threading.current_thread().ident
    with _db_lock:
        if worker_id not in _db_initialized:
            try:
                logger.info(f"Initializing database for worker {worker_id}")
                init_db()
                _db_initialized.add(worker_id)
                logger.info(f"Database initialized for worker {worker_id}")
            except Exception as e:
                logger.error(f"Failed to initialize database on startup: {str(e)}", exc_info=True)
                # Don't raise - let the app start and handle errors per-request

if __name__ == '__main__':
    init_db()
    # Only run in debug mode if not in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
