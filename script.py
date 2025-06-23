import mysql.connector

from modele import getAllStudents, getStudentById

from flask import Flask, render_template, request

app = Flask(__name__)

def index():
    return render_template("index.html")

@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/students")
def students():
    students = getAllStudents()
    return render_template("pages/students.html", students=students)

@app.route("/student/<int:id>")
def student(id):
    student = getStudentById(id)
    if student:
        return render_template("pages/student.html", student=student)
    else:
        return "Student not found", 404