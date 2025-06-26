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
    countStudents,
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


@app.route("/api/")
def home():
    return render_template("pages/home.html")


@app.route("/api/students")
def students():
    return jsonify(getAllStudents())


@app.route("/api/student/<int:id>")
def student(id):
    student = getStudentById(id)
    if student:
        return jsonify(student)
    else:
        return jsonify({"error": "Student not found"}), 404


@app.route("/api/film/<int:id>")
def film(id):
    film = oneFilm(id)
    if film:
        return jsonify(film)
    else:
        return jsonify({"error": "Film not found"}), 404


@app.route("/api/director/<int:id>")
def director(id):
    director = oneDirector(id)
    if director:
        return jsonify(director)
    else:
        return jsonify({"error": "Director not found"}), 404


@app.route("/api/genres")
def genres():
    return jsonify(allGenres())


# -----------------------------------------------------------------------------------------
# ---------------------------------------- TOP 5 ------------------------------------------
# -----------------------------------------------------------------------------------------


@app.route("/api/top5/films")
def top5_films():
    return jsonify(top5Film())


@app.route("/api/top5/genres")
def top5_genres():
    return jsonify(top5Genre())


@app.route("/api/top5/directors")
def top5_directors():
    return jsonify(top5Realisateur())


@app.route("/api/top5/decades")
def top5_decades():
    return jsonify(top5Decennies())


# -----------------------------------------------------------------------------------------
# ------------------------------------- USER COUNT ----------------------------------------
# -----------------------------------------------------------------------------------------


@app.route("/api/user-count")
def userCount_api():
    total = userCount()
    return jsonify({"total_users": total})


# -----------------------------------------------------------------------------------------
# ------------------------------------- AUTHENTICATION ------------------------------------
# -----------------------------------------------------------------------------------------


@app.route("/api/signup", methods=["POST"])
def signup_api():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    username = data.get("username")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    success, message = create_user(username, password, confirm_password)

    if success:
        return jsonify({"message": message}), 201
    else:
        return jsonify({"error": message}), 400


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Invalid data"}), 400

    username = data.get("username")
    password = data.get("password")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            return (
                jsonify(
                    {
                        "success": True,
                        "data": {
                            "message": "Admin login successful",
                            "user": {"username": "admin", "role": "admin"},
                        },
                    }
                ),
                200,
            )

        if verify_user(username, password):
            return (
                jsonify(
                    {
                        "success": True,
                        "data": {
                            "message": "Admin login successful",
                            "user": {"username": username, "role": "admin"},
                        },
                    }
                ),
                200,
            )

        return jsonify({"success": False, "error": "Invalid username or password"}), 401


@app.route("/api/logout")
def logout():
    return (
        jsonify({"message": "Logged out. Please delete your token client-side."}),
        200,
    )


# -----------------------------------------------------------------------------------------
# ---------------------------------------- USER -------------------------------------------
# -----------------------------------------------------------------------------------------


@app.route("/api/account/<string:username>", methods=["GET"])
def account_api(username):
    user_info = getUserInfo(username)
    if user_info:
        return jsonify(user_info), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route("/api/update/<string:username>", methods=["PUT"])
def update_account_api(username):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    prenom = data.get("prenom")
    nom = data.get("nom")
    id_film = data.get("id_film")
    id_genre = data.get("id_genre")

    if not all([prenom, nom, id_film, id_genre]):
        return jsonify({"error": "Missing required fields"}), 400

    saveUpdateInfo(username, prenom, nom, id_film, id_genre)
    return jsonify({"message": "Account updated successfully"}), 200


# -----------------------------------------------------------------------------------------
# ---------------------------------------- ADMIN ------------------------------------------
# -----------------------------------------------------------------------------------------


@app.route("/api/admin", methods=["GET", "POST"])
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
    edit_student = (
        getStudentByIdFull(edit_id)
        if action in ["edit_student", "delete_student"] and edit_id
        else None
    )

    # Pour modification/suppression d'un film
    edit_film = (
        getFilmByIdWithLinks(edit_id)
        if action in ["edit_film", "delete_film"] and edit_id
        else None
    )

    # Pour modification/suppression d'un genre
    edit_genre = (
        getGenreById(edit_id)
        if action in ["edit_genre", "delete_genre"] and edit_id
        else None
    )

    # Pour modification/suppression d'un réalisateur
    edit_director = (
        getDirectorById(edit_id)
        if action in ["edit_director", "delete_director"] and edit_id
        else None
    )

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
        etu["display"] = f"{etu['prenom']} {etu['nom']} (ID : {etu['id']})"

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
