from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="newpassword",
    host="localhost",
    port="5432"
)

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
        return redirect(url_for('login'))
    except psycopg2.Error as e:
        conn.rollback()
        error_message = "Error occurred while signing up. Please try again."
        return render_template('signup.html', error=error_message)


@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
