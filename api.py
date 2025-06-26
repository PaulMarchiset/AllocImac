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
    create_user,
    verify_user,
    getUserInfo,
    saveUpdateInfo,
    getAllStudentsShort,
    getStudentsPaginated,
    countStudents,
    addStudent,
    editStudent,
    deleteStudent,
    getAllFilms,
    addFilm,
    editFilm,
    deleteFilm,
    getAllGenres,
    addGenre,
    editGenre,
    deleteGenre,
    getAllDirectors,
    addDirector,
    editDirector,
    deleteDirector,
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


# STUDENTS API
@app.route("/api/admin/students", methods=["GET"])
def get_students_api():
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    offset = (page - 1) * limit

    students = getStudentsPaginated(offset=offset, limit=limit)
    total = countStudents()

    return jsonify({
        "students": students,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "has_next": offset + limit < total
        }
    }), 200


@app.route("/api/admin/students", methods=["POST"])
def add_student_api():
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    prenom = data.get("prenom")
    nom = data.get("nom")
    id_film = data.get("id_film")
    id_genre = data.get("id_genre")

    if not all([prenom, nom, id_film, id_genre]):
        return jsonify({"error": "Missing required fields"}), 400
    addStudent(prenom, nom, id_film, id_genre)
    return jsonify({"message": "Student added successfully"}), 201

@app.route("/api/admin/students/<int:id>", methods=["PUT"])
def edit_student_api(id):
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    prenom = data.get("prenom")
    nom = data.get("nom")
    id_film = data.get("id_film")
    id_genre = data.get("id_genre")

    if not all([prenom, nom, id_film, id_genre]):
        return jsonify({"error": "Missing required fields"}), 400
    editStudent(id, prenom, nom, id_film, id_genre)
    return jsonify({"message": "Student updated successfully"}), 200

@app.route("/api/admin/students/<int:id>", methods=["DELETE"])
def delete_student_api(id):
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    deleteStudent(id)
    return jsonify({"message": "Student deleted successfully"}), 200


# FILMS API
@app.route("/api/admin/films", methods=["GET"])
def get_films_api():
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    films = getAllFilms()
    return jsonify(films), 200

@app.route("/api/admin/film", methods=["POST"])
def add_film_api():
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    nom = data.get("nom")
    annee = data.get("annee")
    genres_ids = data.get("genres", [])
    directors_ids = data.get("directors", [])

    if not all([nom, annee, genres_ids, directors_ids]):
        return jsonify({"error": "Missing required fields"}), 400
    addFilm(nom, annee, genres_ids, directors_ids)
    return jsonify({"message": "Film added successfully"}), 201

@app.route("/api/admin/film/<int:id>", methods=["PUT"])
def edit_film_api(id):
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    nom = data.get("nom")
    annee = data.get("annee")
    genres_ids = data.get("genres", [])
    directors_ids = data.get("directors", [])

    if not all([nom, annee, genres_ids, directors_ids]):
        return jsonify({"error": "Missing required fields"}), 400
    editFilm(id, nom, annee, genres_ids, directors_ids)
    return jsonify({"message": "film updated successfully"}), 200

@app.route("/api/admin/film/<int:id>", methods=["DELETE"])
def delete_film_api(id):
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    deleteFilm(id)
    return jsonify({"message": "Film deleted successfully"}), 200

# GENRES API
@app.route("/api/admin/genres", methods=["GET"])
def get_genres_api():
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    genres = getAllGenres()
    return jsonify(genres), 200

@app.route("/api/admin/genre", methods=["POST"])
def add_genre_api():
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    nom = data.get("nom")

    if not nom:
        return jsonify({"error": "Missing required fields"}), 400
    addGenre(nom)
    return jsonify({"message": "Genre added successfully"}), 201

@app.route("/api/admin/genre/<int:id>", methods=["PUT"])
def edit_genre_api(id):
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    nom = data.get("nom")

    if not nom:
        return jsonify({"error": "Missing required fields"}), 400
    editGenre(id, nom)
    return jsonify({"message": "genre updated successfully"}), 200

@app.route("/api/admin/genre/<int:id>", methods=["DELETE"])
def delete_genre_api(id):
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    deleteGenre(id)
    return jsonify({"message": "Genre deleted successfully"}), 200

# DIRECTORS API
@app.route("/api/admin/directors", methods=["GET"])
def get_directors_api():
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    directors = getAllDirectors()
    return jsonify(directors), 200

@app.route("/api/admin/director", methods=["POST"])
def add_director_api():
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    nom = data.get("nom")

    if not nom:
        return jsonify({"error": "Missing required fields"}), 400
    addDirector(nom)
    return jsonify({"message": "Director added successfully"}), 201

@app.route("/api/admin/director/<int:id>", methods=["PUT"])
def edit_director_api(id):
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    nom = data.get("nom")

    if not nom:
        return jsonify({"error": "Missing required fields"}), 400
    editDirector(id, nom)
    return jsonify({"message": "Director updated successfully"}), 200

@app.route("/api/admin/director/<int:id>", methods=["DELETE"])
def delete_director_api(id):
    if session.get("username") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    deleteDirector(id)
    return jsonify({"message": "Director deleted successfully"}), 200