import mysql.connector

from modele import getAllStudents, getStudentById

from flask import Flask, render_template, request

app = Flask(__name__)

def index():
    return render_template("index.html")

@app.route("/", methods=["GET"])
def home():
    return index()

@app.route("/student", methods=["GET"])
def student():
    return render_template("student.html", students=getAllStudents())