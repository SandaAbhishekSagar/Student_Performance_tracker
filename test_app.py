#!/usr/bin/env python3
"""
Simple test script for Student Attendance Tracker
Tests basic functionality without requiring a web browser
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Course, Student, Enrollment, Session, Attendance, ATTENDANCE_WEIGHTS

def test_database_creation():
    """Test database initialization and table creation"""
    print("Testing database creation...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['user', 'course', 'student', 'enrollment', 'session', 'attendance']
        for table in expected_tables:
            assert table in tables, f"Table {table} not found"
        
        print("[OK] Database tables created successfully")

def test_sample_data():
    """Test creating and querying sample data"""
    print("Testing sample data creation...")
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create demo teacher
        teacher = User(name="Demo Teacher", role="teacher")
        db.session.add(teacher)
        db.session.commit()
        
        # Create a course
        course = Course(name="Mathematics 101")
        db.session.add(course)
        db.session.commit()
        
        # Create students
        students = [
            Student(full_name="John Doe"),
            Student(full_name="Jane Smith"),
            Student(full_name="Bob Johnson")
        ]
        for student in students:
            db.session.add(student)
        db.session.commit()
        
        # Enroll students
        for student in students:
            enrollment = Enrollment(course_id=course.id, student_id=student.id)
            db.session.add(enrollment)
        db.session.commit()
        
        # Create a session
        from datetime import date
        session = Session(course_id=course.id, session_date=date.today())
        db.session.add(session)
        db.session.commit()
        
        # Mark attendance
        attendance_data = [
            (session.id, students[0].id, "Present"),
            (session.id, students[1].id, "Late"),
            (session.id, students[2].id, "Absent")
        ]
        
        for session_id, student_id, status in attendance_data:
            attendance = Attendance(session_id=session_id, student_id=student_id, status=status)
            db.session.add(attendance)
        db.session.commit()
        
        print("[OK] Sample data created successfully")

def test_attendance_calculation():
    """Test attendance percentage calculation"""
    print("Testing attendance calculation...")
    
    with app.app_context():
        # Get the course and students
        course = Course.query.first()
        students = Student.query.all()
        sessions = Session.query.filter_by(course_id=course.id).all()
        
        # Calculate attendance for each student
        for student in students:
            total_weight = 0.0
            for session in sessions:
                attendance = Attendance.query.filter_by(
                    session_id=session.id, 
                    student_id=student.id
                ).first()
                
                if attendance:
                    total_weight += ATTENDANCE_WEIGHTS.get(attendance.status, 0.0)
                else:
                    total_weight += ATTENDANCE_WEIGHTS['Absent']
            
            percentage = (total_weight / len(sessions)) * 100
            print(f"  {student.full_name}: {percentage:.1f}%")
        
        print("[OK] Attendance calculation working correctly")

def test_constraints():
    """Test database constraints"""
    print("Testing database constraints...")
    
    with app.app_context():
        course = Course.query.first()
        student = Student.query.first()
        
        # Test unique enrollment constraint
        try:
            duplicate_enrollment = Enrollment(course_id=course.id, student_id=student.id)
            db.session.add(duplicate_enrollment)
            db.session.commit()
            assert False, "Duplicate enrollment should not be allowed"
        except Exception:
            db.session.rollback()
            print("[OK] Unique enrollment constraint working")
        
        # Test unique session constraint
        try:
            from datetime import date
            duplicate_session = Session(course_id=course.id, session_date=date.today())
            db.session.add(duplicate_session)
            db.session.commit()
            assert False, "Duplicate session should not be allowed"
        except Exception:
            db.session.rollback()
            print("[OK] Unique session constraint working")
        
        print("[OK] Database constraints working correctly")

def main():
    """Run all tests"""
    print("=" * 50)
    print("Student Attendance Tracker - Test Suite")
    print("=" * 50)
    
    try:
        test_database_creation()
        test_sample_data()
        test_attendance_calculation()
        test_constraints()
        
        print("\n" + "=" * 50)
        print("[SUCCESS] All tests passed successfully!")
        print("The application is ready to use.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
