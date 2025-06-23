import mysql.connector

from modele import getAllStudents, getStudentById

from flask import Flask, render_template, request

app = Flask(__name__)

def index():
    return render_template("index.html")

@app.route("/")
def home():
    return render_template("pages/home.html")