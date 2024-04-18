import pytest
from app import app, conn  # Import your Flask app and database connection object

# Test user authentication
def test_authentication():
    client = app.test_client()
    
    # Test logging in with correct username and password
    response = client.post('/authenticate', data=dict(username='user1', password='password1'))
    assert response.status_code == 302  # Assuming successful authentication redirects to dashboard
    
    # Test logging in with incorrect username or password
    response = client.post('/authenticate', data=dict(username='user1', password='wrong_password'))
    assert response.status_code == 302  # Assuming unsuccessful authentication redirects to signup page
    
    # Test signing up with a new username and password
    response = client.post('/signup', data=dict(username='new_user', password='new_password', role='student'))
    assert response.status_code == 302  # Assuming successful signup redirects to login page
    
    # Test signing up with an existing username
    response = client.post('/signup', data=dict(username='user1', password='password1', role='student'))
    assert response.status_code == 200  # Assuming unsuccessful signup returns status code 200


# Test course creation
def test_course_creation():
    client = app.test_client()
    
    # Test creating a new course with valid data
    response = client.post('/create_course', data=dict(course_name='New Course', course_code='ABC123', 
                                                       course_description='Description', 
                                                       start_date='2024-05-01', end_date='2024-06-01'))
    assert response.status_code == 302  # Assuming successful course creation redirects to teacher dashboard
    
    # Test creating a new course with invalid data
    response = client.post('/create_course', data=dict(course_name='', course_code='ABC123', 
                                                       course_description='Description', 
                                                       start_date='2024-05-01', end_date='2024-06-01'))
    assert b'Error occurred while creating the course' in response.data  # Check for error message in response


# Test enrollment
def test_enrollment():
    client = app.test_client()
    
    # Test enrolling in a course as a student
    response = client.post('/enroll_course', data=dict(username='student1', course_id='1'))
    assert response.status_code == 302  # Assuming successful enrollment redirects to student dashboard
    
    # Test enrolling in a course without being logged in
    response = client.post('/enroll_course', data=dict(course_id='1'))
    assert b'User not logged in' in response.data  # Check for error message in response
    
    # Test enrolling in a course with invalid data
    response = client.post('/enroll_course', data=dict(username='student1'))
    assert b'Incomplete data' in response.data  # Check for error message in response


# Test dashboard
def test_dashboard():
    client = app.test_client()
    
    # Test viewing the student dashboard after enrolling in courses
    response = client.get('/student_dashboard')
    assert response.status_code == 200  # Assuming successful request returns status code 200
    
    # Test viewing the teacher dashboard after creating courses
    response = client.get('/teacher_dashboard')
    assert response.status_code == 200  # Assuming successful request returns status code 200


# Close the database connection after tests
def teardown_module(module):
    conn.close()
