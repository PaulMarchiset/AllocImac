# -----------------------------------------------------------------------------------------
# ---------------------------------------- SETUP ------------------------------------------
# -----------------------------------------------------------------------------------------


import mysql.connector

from modele import (
    getAllStudents,
    getStudentById,
    oneFilm,
    oneDirector,
    allGenres,
    top5Decennies,
    top5Genre,
    top5Film,
    top5Realisateur,
    search_query,
    create_user,
    verify_user,
    getUserName,
    getUpdateInfo,
)

from flask import Flask, render_template, request

app = Flask(__name__)

from flask import session
app.secret_key = "key"

# -----------------------------------------------------------------------------------------
# ---------------------------------------- ROUTES -----------------------------------------
# -----------------------------------------------------------------------------------------


def index():
    return render_template("pages/home.html")


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

# -----------------------------------------------------------------------------------------
# ---------------------------------------- TOP 5 ------------------------------------------
# -----------------------------------------------------------------------------------------


@app.route("/top5/films")
def top5_films():
    films = top5Film()
    return render_template("pages/top5/films.html", films=films)


@app.route("/top5/genres")
def top5_genres():
    genres = top5Genre()
    return render_template("pages/top5/genres.html", genres=genres)


@app.route("/top5/directors")
def top5_directors():
    directors = top5Realisateur()
    return render_template("pages/top5/directors.html", directors=directors)


@app.route("/top5/decades")
def top5_decades():
    decades = top5Decennies()
    return render_template("pages/top5/decades.html", decades=decades)


# -----------------------------------------------------------------------------------------
# ---------------------------------------- SEARCH ------------------------------------------
# -----------------------------------------------------------------------------------------

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("search", "").strip()
    films, directors, students = [], [], []

    if q:
        films, directors, students = search_query(q)

    return render_template(
        "pages/search.html",
        query=q,
        films=films,
        directors=directors,
        students=students,
    )

# -----------------------------------------------------------------------------------------
# ------------------------------------- AUTHENTICATION ------------------------------------
# -----------------------------------------------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        result = create_user(request.form["username"], request.form["password"], request.form["confirm-password"])
        return render_template("pages/signup.html", message=result)
    return render_template("pages/signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if verify_user(username, password):
            session["username"] = username
            return account()
        else:
            return render_template("pages/login.html", message="Nom d'utilisateur ou mot de passe incorrect.")
    return render_template("pages/login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return index()


# -----------------------------------------------------------------------------------------
# ---------------------------------------- USER -------------------------------------------
# -----------------------------------------------------------------------------------------

@app.route("/account")
def account():
    if "username" in session:
        username = session["username"]
        user = getUserName(username)
        return render_template("pages/account.html", user=user)
    else:
        return render_template("pages/login.html", message="Vous devez être connecté pour accéder à votre compte.")

@app.route("/update", methods=["GET", "POST"])
def update_account():
    if "username" in session:
        results = getUpdateInfo()
        return render_template("pages/update.html", results=results)
    else: 
        return render_template("pages/login.html", message="Vous devez être connecté pour mettre à jour votre compte.")