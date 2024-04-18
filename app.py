from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Connect to PostgreSQL database
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="newpassword",
        host="localhost",
        port="5432"
    )
    print("Connected to the database successfully!")
except psycopg2.Error as e:
    print("Unable to connect to the database:", e)

# Create users table if not exists
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(50) NOT NULL,
        role VARCHAR(20) NOT NULL
    )
""")
conn.commit()
# Create enrolled_courses table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS enroll_course (
        id SERIAL PRIMARY KEY,
        student_username VARCHAR(50),  -- Change data type to VARCHAR to store usernames
        course_id INTEGER REFERENCES courses(id)
    )
""")
conn.commit()


# Create courses table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id SERIAL PRIMARY KEY,
        course_name VARCHAR(100) NOT NULL,
        course_code VARCHAR(20) NOT NULL,
        course_description TEXT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL
    )
""")
conn.commit()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    cur = conn.cursor()

    # Query the database for user credentials
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cur.fetchone()

    if user:
        if user[3] == 'student':
            return redirect(url_for('student_dashboard'))
        elif user[3] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('signup'))

# Rename the original signup function to signup_page
@app.route('/signup')
def signup_page():
    return render_template('signup.html')

# Define the new signup function for handling form submissions
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        conn.commit()
        print("User {} signed up successfully!".format(username))
        return redirect(url_for('login'))
    except psycopg2.Error as e:
        conn.rollback()
        error_message = "Error occurred while signing up. Please try again."
        print("Error occurred while signing up:", e)
        return render_template('signup.html', error=error_message)


# @app.route('/student_dashboard')
# def student_dashboard():
#     return render_template('student_dashboard.html')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')
@app.route('/course_creation', methods=['GET', 'POST'])
def course_creation():
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_code = request.form['course_code']
        course_description = request.form['course_description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO courses (course_name, course_code, course_description, start_date, end_date) VALUES (%s, %s, %s, %s, %s)", (course_name, course_code, course_description, start_date, end_date))
            conn.commit()
            print("Course {} created successfully!".format(course_name))
            return redirect(url_for('teacher_dashboard'))
        except psycopg2.Error as e:
            conn.rollback()
            error_message = "Error occurred while creating the course. Please try again."
            print("Error occurred while creating the course:", e)
            return render_template('course_creation.html', error=error_message)

    else:
        return render_template('course_creation.html')
# Create a route to handle the form submission
@app.route('/create_course', methods=['POST'])
def create_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_code = request.form['course_code']
        course_description = request.form['course_description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Insert the course details into the database
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO courses (course_name, course_code, course_description, start_date, end_date) VALUES (%s, %s, %s, %s, %s)", (course_name, course_code, course_description, start_date, end_date))
            conn.commit()
            print("Course {} created successfully!".format(course_name))
            return redirect(url_for('teacher_dashboard'))  # Redirect to teacher dashboard after successful submission
        except psycopg2.Error as e:
            conn.rollback()
            error_message = "Error occurred while creating the course. Please try again."
            print("Error occurred while creating the course:", e)
            # You can handle the error as needed, such as displaying an error message to the user
            return render_template('error.html', error=error_message)
# Function to fetch courses from the database
def fetch_courses():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="newpassword",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM courses")
        courses = cur.fetchall()
        cur.close()
        conn.close()
        return courses
    except psycopg2.Error as e:
        print("Error fetching courses:", e)
        return None

@app.route('/student_dashboard')
def student_dashboard():
    courses = fetch_courses()
    # Fetch student's username from the database (replace this with your actual query)
    student_username = get_student_username()  # Implement get_student_username() function to retrieve the student's username
    if courses and student_username:
        return render_template('student_dashboard.html', courses=courses, student_username=student_username)
    else:
        return "Error fetching courses or student username. Please try again later."

# Function to fetch student's username from the database
def get_student_username():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="newpassword",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE role = 'student'")  # Assuming there's only one student in the database
        student_username = cur.fetchone()[0]  # Fetch the first student's username
        cur.close()
        conn.close()
        return student_username
    except psycopg2.Error as e:
        print("Error fetching student username:", e)
        return None
@app.route('/enroll_course', methods=['POST'])
def enroll_course():
    if request.method == 'POST':
        print("Form Data:", request.form)
        if 'username' in request.form and 'course_id' in request.form:
            student_username = request.form['username']
            course_id = request.form['course_code']

            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO enroll_course (student_username, course_code) VALUES (%s, %s)", (student_username, course_id))
                conn.commit()
                cur.close()
                return redirect(url_for('student_dashboard'))  # Redirect to student dashboard after enrollment
            except psycopg2.Error as e:
                print("Error enrolling course:", e)
                return "Error enrolling course. Please try again later."
        else:
            return "Incomplete data. Please provide both username and course_id."


if __name__ == '__main__':
    app.run(debug=True)
