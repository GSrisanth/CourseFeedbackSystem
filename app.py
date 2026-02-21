import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# -------------------------------
# Database Connection Function
# -------------------------------
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
        ssl_disabled=True
    )


# -------------------------------
# Login Page
# -------------------------------
@app.route('/')
def home():
    return render_template("login.html")


# -------------------------------
# Login Logic
# -------------------------------
@app.route('/login', methods=['POST'])
def login():
    roll_no = request.form['roll_no']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT student_id, semester FROM students WHERE roll_no = %s",
        (roll_no,)
    )

    student = cursor.fetchone()
    conn.close()

    if student:
        student_id, semester = student
        return redirect(f"/courses/{student_id}/{semester}")
    else:
        return "Student Not Found"


# -------------------------------
# Show Courses (WITH Professor Name)
# -------------------------------
@app.route('/courses/<int:student_id>/<int:semester>')
def show_courses(student_id, semester):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT c.course_id, c.course_name, p.professor_name
    FROM courses c
    JOIN course_professor cp ON c.course_id = cp.course_id
    JOIN professors p ON cp.professor_id = p.professor_id
    WHERE c.semester = %s
    """, (semester,))
    

    courses = cursor.fetchall()
    conn.close()

    return render_template(
        "courses.html",
        courses=courses,
        student_id=student_id
    )


# -------------------------------
# Feedback Page
# -------------------------------
@app.route('/feedback/<int:student_id>/<int:course_id>')
def feedback_page(student_id, course_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.professor_id, p.professor_name
        FROM course_professor cp
        JOIN professors p ON cp.professor_id = p.professor_id
        WHERE cp.course_id = %s
    """, (course_id,))

    professor = cursor.fetchone()
    conn.close()

    # If no professor found, avoid crash
    if professor:
        professor_id = professor[0]
        professor_name = professor[1]
    else:
        professor_id = None
        professor_name = "Professor Not Assigned"

    return render_template(
        "feedback.html",
        student_id=student_id,
        course_id=course_id,
        professor_id=professor_id,
        professor_name=professor_name
    )

# -------------------------------
# Submit Feedback
# -------------------------------
@app.route('/submit', methods=['POST'])
def submit_feedback():

    student_id = request.form['student_id']
    course_id = request.form['course_id']
    professor_id = request.form['professor_id']
    course_rating = request.form['course_rating']
    professor_rating = request.form['professor_rating']
    comments = request.form['comments']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback
        (student_id, course_id, professor_id,
         course_rating, professor_rating, comments)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        student_id,
        course_id,
        professor_id,
        course_rating,
        professor_rating,
        comments
    ))

    conn.commit()
    conn.close()

    return render_template("success.html")


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)