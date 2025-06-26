# -----------------------------------------------------------------------------------------
# ---------------------------------------- SETUP ------------------------------------------
# -----------------------------------------------------------------------------------------


import mysql.connector

from modele import (
    getAllStudents,
    getStudentById,
    userCount,
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
    getUserInfo,
    getUpdateInfo,
    saveUpdateInfo,
    addStudent,
    editStudent,
    deleteStudent,
    addFilm,
    editFilm,
    deleteFilm,
    addGenre,
    editGenre,
    deleteGenre,
    addDirector,
    editDirector,
    deleteDirector,
    getStudentByIdFull,
    getFilmByIdWithLinks,
    getGenreById,
    getDirectorById,
    getAllFilms,
    getAllGenres,
    getAllDirectors,
    getAllStudentsShort,
    getStudentsPaginated,
    countStudents
)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

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


@app.route("/api/user-count")
def userCount_api():
    total = userCount()
    return jsonify({"total_users": total})


# -----------------------------------------------------------------------------------------
# ------------------------------------- AUTHENTICATION ------------------------------------
# -----------------------------------------------------------------------------------------


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        result = create_user(
            request.form["username"],
            request.form["password"],
            request.form["confirm-password"],
        )
        if result:
            session["username"] = request.form["username"]
            return account()
        else:
            return render_template(
                "pages/user/signup.html",
                message=result,
            )
    return render_template("pages/user/signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            session["username"] = username
            return admin()

        if verify_user(username, password):
            session["username"] = username
            return account()
        else:
            return render_template(
                "pages/user/login.html",
                message="Nom d'utilisateur ou mot de passe incorrect.",
            )
    return render_template("pages/user/login.html")


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
        user = getUserInfo(username)
        return render_template("pages/user/account.html", user=user)
    else:
        return login()


@app.route("/update", methods=["GET", "POST"])
def update_account():
    if "username" not in session:
        return login()
    
    username = session["username"]

    if request.method == "POST":
        prenom = request.form["prenom"]
        nom = request.form["nom"]
        id_film = request.form["film"]
        id_genre = request.form["genre"]
        saveUpdateInfo(username, prenom, nom, id_film, id_genre)
        return account()
    
    user = getUserInfo(username)
    update = getUpdateInfo()
    return render_template("pages/user/update.html", user=user, update=update)


# -----------------------------------------------------------------------------------------
# ---------------------------------------- ADMIN ------------------------------------------
# -----------------------------------------------------------------------------------------


@app.route("/admin", methods=["GET", "POST"])
def admin():
    action = request.args.get("action")
    edit_id = request.args.get("id", type=int)

    # Traitement des formulaires POST
    if request.method == "POST":
        form_type = request.form.get("form_type")
        
        # Ajouter un étudiant
        if form_type == "add_student":
            prenom = request.form["prenom"]
            nom = request.form["nom"]
            id_film = request.form["id_film"]
            id_genre = request.form["id_genre"]
            addStudent(prenom, nom, id_film, id_genre)

        # Modifier un étudiant
        if form_type == "edit_student":
            id = request.form["id"]
            prenom = request.form["prenom"]
            nom = request.form["nom"]
            id_film = request.form["id_film"]
            id_genre = request.form["id_genre"]
            editStudent(id, prenom, nom, id_film, id_genre)

        # Supprimer un étudiant
        if form_type == "delete_student":
            id = request.form["id"]
            deleteStudent(id)

        # Ajouter un film
        if form_type == "add_film":
            nom = request.form["nom"]
            annee = request.form["annee"]
            addFilm(nom, annee)

        # Modifier un film
        if form_type == "edit_film":
            id = request.form["id"]
            nom = request.form["nom"]
            annee = request.form["annee"]
            genres_ids = request.form.getlist("genres")
            directors_ids = request.form.getlist("directors")
            editFilm(id, nom, annee, genres_ids, directors_ids)

        # Supprimer un film
        if form_type == "delete_film":
            id = request.form["id"]
            deleteFilm(id)

        # Ajouter un genre
        if form_type == "add_genre":
            nom = request.form["nom"]
            addGenre(nom)

        # Modifier un genre
        if form_type == "edit_genre":
            id = request.form["id"]
            nom = request.form["nom"]
            editGenre(id, nom)

        # Supprimer un genre
        if form_type == "delete_genre":
            id = request.form["id"]
            deleteGenre(id)

        # Ajouter un réalisateur
        if form_type == "add_director":
            nom = request.form["nom"]
            addDirector(nom)

        # Modifier un réalisateur
        if form_type == "edit_director":
            id = request.form["id"]
            nom = request.form["nom"]
            editDirector(id, nom)

        # Supprimer un réalisateur
        if form_type == "delete_director":
            id = request.form["id"]
            deleteDirector(id)

    # Pour modification/suppression d'un étudiant
    edit_student = getStudentByIdFull(edit_id) if action in ["edit_student", "delete_student"] and edit_id else None

    # Pour modification/suppression d'un film
    edit_film = getFilmByIdWithLinks(edit_id) if action in ["edit_film", "delete_film"] and edit_id else None

    # Pour modification/suppression d'un genre
    edit_genre = getGenreById(edit_id) if action in ["edit_genre", "delete_genre"] and edit_id else None

    # Pour modification/suppression d'un réalisateur
    edit_director = getDirectorById(edit_id) if action in ["edit_director", "delete_director"] and edit_id else None
    
    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    students = getStudentsPaginated(offset=offset, limit=per_page)
    total = countStudents()
    has_next = offset + per_page < total

    # Pour les formulaires
    films = getAllFilms()
    genres = getAllGenres()
    directors = getAllDirectors()
    all_students = getAllStudentsShort()

    for etu in all_students:
        etu['display'] = f"{etu['prenom']} {etu['nom']} (ID : {etu['id']})"

    if session.get("username") == "admin":
        return render_template(
            "pages/user/admin.html",
            all_students=all_students,
            students=students,
            page=page,
            has_next=has_next,
            action=action,
            films=films,
            genres=genres,
            directors=directors,
            edit_id=edit_id,
            edit_student=edit_student,
            edit_film=edit_film,
            edit_genre=edit_genre,
            edit_director=edit_director,
        )
    else:
        return login()
