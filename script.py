import mysql.connector

from modele import getAllStudents, getStudentById, oneFilm, oneDirector, allGenres, top5Decennies, top5Genre, top5Film, top5Realisateur

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
    
@app.route("/film/<int:id>")
def film(id):
    film = oneFilm(id)
    if film:
        return render_template("pages/film.html", film=film)
    else:
        return "Film not found", 404
    
@app.route("/director/<int:id>")
def director(id):
    director = oneDirector(id)
    if director:
        return render_template("pages/director.html", director=director)
    else:
        return "Director not found", 404
    
@app.route("/genres")
def genres():
    genres = allGenres()
    return render_template("pages/genres.html", genres=genres)

@app.route("/top5/film")
def top5_films():
    films = top5Film()
    return render_template("pages/top5/films.html", films=films)