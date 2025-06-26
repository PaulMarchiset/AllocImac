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
    addUser,
    editUser,
    deleteUser,
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
    getAllUsers,
    getUserById,
    getStudentsPaginated,
    countStudents,
    getTotalFilmRanking,
    getTotalGenreRanking,
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

@app.route("/cherrier")
def easterEgg():
    return render_template("pages/cherrier.html")

# Afficher tous les étudiants
@app.route("/students")
def students():
    students = getAllStudents()
    return render_template("pages/students.html", students=students)

# Afficher un étudiant spécifique
@app.route("/student/<int:id>")
def student(id):
    student = getStudentById(id)
    if student:
        # Récupérer le classement du film préféré de l'étudiant
        film_id = student["film"]["id"]
        film_ranking=getTotalFilmRanking()

        classement_film = None
        film_info = None
        for index, film in enumerate(film_ranking, start=1):
            if film["film_id"] == film_id:
                classement_film = index
                film_info = film
                break

        # Récupérer le classement du genre préféré de l'étudiant
        genre_id = student["genre"]["id"]
        genre_ranking = getTotalGenreRanking()

        classement_genre = None
        genre_info = None
        for index, genre in enumerate(genre_ranking, start=1):
            if genre["id_genre"] == genre_id:
                classement_genre = index
                genre_info = film
                break

        return render_template("pages/student.html", student=student, classement_film=classement_film, film_info=film_info, classement_genre=classement_genre, genre_info=genre_info)
    else:
        return "Student not found", 404

# Afficher un film spécifique
@app.route("/film/<int:id>")
def film(id):
    film = oneFilm(id)
    if film:
        return render_template("pages/film.html", film=film)
    else:
        return "Film not found", 404

# Afficher un réalisateur spécifique
@app.route("/director/<int:id>")
def director(id):
    director = oneDirector(id)
    if director:
        return render_template("pages/director.html", director=director)
    else:
        return "Director not found", 404

# Afficher tous les genres
@app.route("/genres")
def genres():
    genres = allGenres()
    return render_template("pages/genres.html", genres=genres)


# -----------------------------------------------------------------------------------------
# ---------------------------------------- TOP 5 ------------------------------------------
# -----------------------------------------------------------------------------------------

# Afficher le top 5 des films choisis par les étudiants
@app.route("/top5/films")
def top5_films():
    films = top5Film()
    return render_template("pages/top5/films.html", films=films)

# Afficher le top 5 des genres choisis par les étudiants
@app.route("/top5/genres")
def top5_genres():
    genres = top5Genre()
    return render_template("pages/top5/genres.html", genres=genres)

# Afficher le top 5 des réalisateurs par rapport aux films choisis par les étudiants
@app.route("/top5/directors")
def top5_directors():
    directors = top5Realisateur()
    return render_template("pages/top5/directors.html", directors=directors)

# Afficher le top 5 des décennies par rapport aux films choisis par les étudiants
@app.route("/top5/decades")
def top5_decades():
    decades = top5Decennies()
    return render_template("pages/top5/decades.html", decades=decades)


# -----------------------------------------------------------------------------------------
# ---------------------------------------- SEARCH ------------------------------------------
# -----------------------------------------------------------------------------------------

# Afficher les résultats de recherche par rapport à la requête de l'utilisateur sur la barre de recherche
@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("search", "").strip()
    films, directors, students = [], [], []

    # Rechercher dans la table films, réalisateurs et étudiants
    if q:
        films, directors, students = search_query(q)

    return render_template(
        "pages/search.html",
        query=q,
        films=films,
        directors=directors,
        students=students,
    )

# Afficher le nombre total d'utilisateurs en JSON
@app.route("/api/user-count")
def userCount_api():
    total = userCount()
    return jsonify({"total_users": total})


# -----------------------------------------------------------------------------------------
# ------------------------------------- AUTHENTICATION ------------------------------------
# -----------------------------------------------------------------------------------------

# Afficher la page d'inscription et traiter le formulaire d'inscription
@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        # Ajouter un nouvel utilisateur
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

# Afficher la page de connexion et traiter le formulaire de connexion
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Si l'utilisateur est admin, rediriger vers la page d'administration
        if username == "admin" and password == "admin":
            session["username"] = username
            return admin()

        # Vérifier les informations de l'utilisateur
        if verify_user(username, password):
            session["username"] = username
            return account()
        else:
            return render_template(
                "pages/user/login.html",
                message="Nom d'utilisateur ou mot de passe incorrect.",
            )
    return render_template("pages/user/login.html")


# Déconnecter l'utilisateur et rediriger vers la page d'accueil
@app.route("/logout")
def logout():
    session.pop("username", None)
    return index()


# -----------------------------------------------------------------------------------------
# ---------------------------------------- USER -------------------------------------------
# -----------------------------------------------------------------------------------------

# Afficher la page du compte utilisateur
@app.route("/account")
def account():
    # Si l'utilisateur est connecté, on affiche ses informations
    if "username" in session:
        username = session["username"]
        user = getUserInfo(username)
        return render_template("pages/user/account.html", user=user)
    else:
        return login()

# Afficher la page de mise à jour des informations utilisateur et traiter du formulaire de mise à jour
@app.route("/update", methods=["GET", "POST"])
def update_account():
    if "username" not in session:
        return login()
    
    username = session["username"]

    # Mis à jour des informations de l'utilisateur
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

# Afficher la page d'administration et traiter des formulaires d'administration
@app.route("/admin", methods=["GET", "POST"])
def admin():
    action = request.args.get("action")
    edit_id = request.args.get("id", type=int)

    # Traitement des formulaires POST
    if request.method == "POST":
        form_type = request.form.get("form_type")
        
        # Ajouter un utilisateur
        if form_type == "add_user":
            username = request.form["username"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
            id_etudiant = request.form.get("id_etudiant") or None
            success, msg = addUser(username, password, confirm_password, id_etudiant)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="add_user", page=request.args.get("page", 1)))

        # Modifier un utilisateur
        if form_type == "edit_user":
            id = request.form["id"]
            username = request.form["username"]
            password = request.form["password"]  # Peut être vide si pas de changement
            confirm_password = request.form["confirm_password"]
            id_etudiant = request.form.get("id_etudiant") or None
            success, msg = editUser(id, username, password, confirm_password, id_etudiant)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="edit_user", page=request.args.get("page", 1)))

        # Supprimer un utilisateur
        if form_type == "delete_user":
            id = request.form["id"]
            success, msg = deleteUser(id)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="delete_user", page=request.args.get("page", 1)))

        # Ajouter un étudiant
        if form_type == "add_student":
            prenom = request.form["prenom"]
            nom = request.form["nom"]
            id_film = request.form["id_film"]
            id_genre = request.form["id_genre"]
            success, msg = addStudent(prenom, nom, id_film, id_genre)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="add_student", page=request.args.get("page", 1)))

        # Modifier un étudiant
        if form_type == "edit_student":
            id = request.form["id"]
            prenom = request.form["prenom"]
            nom = request.form["nom"]
            id_film = request.form["id_film"]
            id_genre = request.form["id_genre"]
            success, msg = editStudent(id, prenom, nom, id_film, id_genre)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="edit_student", page=request.args.get("page", 1)))

        # Supprimer un étudiant
        if form_type == "delete_student":
            id = request.form["id"]
            success, msg = deleteStudent(id)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="delete_student", page=request.args.get("page", 1)))

        # Ajouter un film
        if form_type == "add_film":
            nom = request.form["nom"]
            annee = request.form["annee"]
            genres_ids = request.form.getlist("genres")
            directors_ids = request.form.getlist("directors")
            success, msg = addFilm(nom, annee, genres_ids, directors_ids)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="add_film", page=request.args.get("page", 1)))

        # Modifier un film
        if form_type == "edit_film":
            id = request.form["id"]
            nom = request.form["nom"]
            annee = request.form["annee"]
            genres_ids = request.form.getlist("genres")
            directors_ids = request.form.getlist("directors")
            success, msg = editFilm(id, nom, annee, genres_ids, directors_ids)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="edit_film", page=request.args.get("page", 1)))

        # Supprimer un film
        if form_type == "delete_film":
            id = request.form["id"]
            success, msg = deleteFilm(id)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="delete_film", page=request.args.get("page", 1)))

        # Ajouter un genre
        if form_type == "add_genre":
            nom = request.form["nom"]
            success, msg = addGenre(nom)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="add_genre", page=request.args.get("page", 1)))

        # Modifier un genre
        if form_type == "edit_genre":
            id = request.form["id"]
            nom = request.form["nom"]
            success, msg = editGenre(id, nom)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="edit_genre", page=request.args.get("page", 1)))

        # Supprimer un genre
        if form_type == "delete_genre":
            id = request.form["id"]
            success, msg = deleteGenre(id)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="delete_genre", page=request.args.get("page", 1)))

        # Ajouter un réalisateur
        if form_type == "add_director":
            nom = request.form["nom"]
            success, msg = addDirector(nom)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="add_director", page=request.args.get("page", 1)))

        # Modifier un réalisateur
        if form_type == "edit_director":
            id = request.form["id"]
            nom = request.form["nom"]
            success, msg = editDirector(id, nom)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="edit_director", page=request.args.get("page", 1)))

        # Supprimer un réalisateur
        if form_type == "delete_director":
            id = request.form["id"]
            success, msg = deleteDirector(id)
            flash(msg, "success" if success else "error")
            if success:
                return redirect(url_for("admin", page=request.args.get("page", 1)))
            else:
                return redirect(url_for("admin", action="delete_director", page=request.args.get("page", 1)))

    # Pour modification/suppression d'un utilisateur
    if action in ["edit_user", "delete_user"] and edit_id:
        edit_user = getUserById(edit_id)
    else: 
        edit_user = None

    # Pour modification/suppression d'un étudiant
    if action in ["edit_student", "delete_student"] and edit_id:
        edit_student = getStudentByIdFull(edit_id)
    else: 
        edit_student = None

    # Pour modification/suppression d'un film
    if action in ["edit_film", "delete_film"] and edit_id:
        edit_film = getFilmByIdWithLinks(edit_id) 
    else:
        edit_film = None

    # Pour modification/suppression d'un genre
    if action in ["edit_genre", "delete_genre"] and edit_id:
        edit_genre = getGenreById(edit_id)
    else:
        edit_genre = None

    # Pour modification/suppression d'un réalisateur
    if action in ["edit_director", "delete_director"] and edit_id:
        edit_director = getDirectorById(edit_id) 
    else: 
        edit_director = None
    
    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    students = getStudentsPaginated(offset=offset, limit=per_page)
    total = countStudents()
    has_next = offset + per_page < total

    # Pour les formulaires
    users = getAllUsers()
    films = getAllFilms()
    genres = getAllGenres()
    directors = getAllDirectors()
    all_students = getAllStudentsShort()

    for etu in all_students:
        etu['display'] = f"{etu['prenom']} {etu['nom']} (ID : {etu['id']})"

    # Si l'utilisateur est admin, afficher la page d'administration
    if session.get("username") == "admin":
        return render_template(
            "pages/user/admin.html",
            all_students=all_students,
            students=students,
            page=page,
            has_next=has_next,
            action=action,
            users=users,
            edit_user=edit_user,
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
