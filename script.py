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
    getStudentsPaginated,
    countStudents,
    mycursor, 
    mydb,
    getUserName,
    getUpdateInfo,
)

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "ma_cle_ultra_secrete_123456"

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
        # result = verify_user(username, password)
        # return render_template("pages/login.html", message=result)

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

            mycursor.execute(
                "SELECT COUNT(*) AS nb FROM ETUDIANT WHERE prenom=%s AND nom=%s AND id_film=%s AND id_genre=%s",
                (prenom, nom, id_film, id_genre)
            )
            result = mycursor.fetchone()
            if result["nb"] > 0:
                flash("Un étudiant avec ce prénom, ce nom, ce film préféré et ce genre préféré existe déjà !", "error")
                return redirect(url_for("admin", action="add_student"))

            mycursor.execute(
                "INSERT INTO ETUDIANT (prenom, nom, id_film, id_genre) VALUES (%s ,%s, %s, %s)",
                (prenom, nom, id_film, id_genre)
            )
            mydb.commit()
            flash("Étudiant ajouté !")
            return redirect(url_for("admin"))
        
        # Modifier un étudiant
        if form_type == "edit_student":
            id = request.form["id"]
            prenom = request.form["prenom"]
            nom = request.form["nom"]
            id_film = request.form["id_film"]
            id_genre = request.form["id_genre"]
            mycursor.execute(
                "UPDATE ETUDIANT SET prenom=%s, nom=%s, id_film=%s, id_genre=%s WHERE id=%s",
                (prenom, nom, id_film, id_genre, id)
            )
            mydb.commit()
            flash("Étudiant modifié !")
            return redirect(url_for("admin"))
        
        # Supprimer un étudiant
        if form_type == "delete_student":
            id = request.form["id"]
            mycursor.execute("DELETE FROM ETUDIANT WHERE id=%s", (id,))
            mydb.commit()
            flash("Étudiant supprimé !")
            return redirect(url_for("admin"))
        
        # Ajouter un film
        if form_type == "add_film":
            nom = request.form["nom"]
            annee = request.form["annee"]

            # Vérifier si le film existe déjà (même nom et année)
            mycursor.execute(
                "SELECT COUNT(*) AS nb FROM FILM WHERE LOWER(nom)=LOWER(%s) AND annee=%s",
                (nom, annee)
            )
            result = mycursor.fetchone()
            if result["nb"] > 0:
                flash("Ce film existe déjà !", "error")
                return redirect(url_for("admin", action="add_film"))
    
            # Insérer le film
            mycursor.execute(
                "INSERT INTO FILM (nom, annee) VALUES (%s, %s)",
                (nom, annee)
            )
            film_id = mycursor.lastrowid

            # Récupérer les genres et réalisateurs sélectionnés
            genres_ids = request.form.getlist("genres")
            directors_ids = request.form.getlist("directors")

            # Insérer dans APPARTENANCE (film-genre)
            for genre_id in genres_ids:
                mycursor.execute(
                    "INSERT INTO APPARTENANCE (id_film, id_genre) VALUES (%s, %s)",
                    (film_id, genre_id)
                )
            # Insérer dans DIRECTION (film-réalisateur)
            for director_id in directors_ids:
                mycursor.execute(
                    "INSERT INTO DIRECTION (id_film, id_realisateur) VALUES (%s, %s)",
                    (film_id, director_id)
                )
            mydb.commit()
            flash("Film ajouté !")
            return redirect(url_for("admin"))
        
        # Modifier un film
        if form_type == "edit_film":
            id = request.form["id"]
            nom = request.form["nom"]
            annee = request.form["annee"]
            genres_ids = request.form.getlist("genres")
            directors_ids = request.form.getlist("directors")

            mycursor.execute(
                "UPDATE FILM SET nom=%s, annee=%s WHERE id=%s",
                (nom, annee, id)
            )

            # Mettre à jour les genres associés
            mycursor.execute("DELETE FROM APPARTENANCE WHERE id_film=%s", (id,))
            for genre_id in genres_ids:
                mycursor.execute(
                    "INSERT INTO APPARTENANCE (id_film, id_genre) VALUES (%s, %s)",
                    (id, genre_id)
                )

            # Mettre à jour les réalisateurs associés
            mycursor.execute("DELETE FROM DIRECTION WHERE id_film=%s", (id,))
            for director_id in directors_ids:
                mycursor.execute(
                    "INSERT INTO DIRECTION (id_film, id_realisateur) VALUES (%s, %s)",
                    (id, director_id)
                )

            mydb.commit()
            flash("Film modifié !")
            return redirect(url_for("admin"))
        
        # Supprimer un film
        if form_type == "delete_film":
            id = request.form["id"]
            # Vérifier si le film est utilisé par un étudiant
            mycursor.execute("SELECT COUNT(*) AS nb FROM ETUDIANT WHERE id_film=%s", (id,))
            used_by_student = mycursor.fetchone()["nb"]
            if used_by_student > 0:
                flash("Impossible de supprimer ce film : il est utilisé par un étudiant.", "error")
                return redirect(url_for("admin"))
            # Supprimer les liens avec les genres (APPARTENANCE)
            mycursor.execute("DELETE FROM APPARTENANCE WHERE id_film=%s", (id,))
            # Supprimer les liens avec les réalisateurs (DIRECTION)
            mycursor.execute("DELETE FROM DIRECTION WHERE id_film=%s", (id,))
            # Supprimer le film
            mycursor.execute("DELETE FROM FILM WHERE id=%s", (id,))
            mydb.commit()
            flash("Film supprimé !")
            return redirect(url_for("admin"))
        
        # Ajouter un genre
        if form_type == "add_genre":
            nom = request.form["nom"]

            # Vérifier si le genre existe déjà (même nom)
            mycursor.execute(
                "SELECT COUNT(*) AS nb FROM GENRE WHERE LOWER(nom)=LOWER(%s)",
                (nom,)
            )
            result = mycursor.fetchone()
            if result["nb"] > 0:
                flash("Ce genre existe déjà !", "error")
                return redirect(url_for("admin", action="add_genre"))

            mycursor.execute(
                "INSERT INTO GENRE (nom) VALUES (%s)",
                (nom,)
            )
            mydb.commit()
            flash("Genre ajouté !")
            return redirect(url_for("admin"))
        
        # Modifier un genre
        if form_type == "edit_genre":
            id = request.form["id"]
            nom = request.form["nom"]
            mycursor.execute(
                "UPDATE GENRE SET nom=%s WHERE id=%s",
                (nom, id)
            )
            mydb.commit()
            flash("Genre modifié !")
            return redirect(url_for("admin"))
        
        # Supprimer un genre
        if form_type == "delete_genre":
            id = request.form["id"]
            # Vérifier si le genre est utilisé par un film (table APPARTENANCE)
            mycursor.execute("SELECT COUNT(*) AS nb FROM APPARTENANCE WHERE id_genre=%s", (id,))
            used_by_film = mycursor.fetchone()["nb"]
            # Vérifier si le genre est utilisé par un étudiant
            mycursor.execute("SELECT COUNT(*) AS nb FROM ETUDIANT WHERE id_genre=%s", (id,))
            used_by_student = mycursor.fetchone()["nb"]
            if used_by_film > 0 or used_by_student > 0:
                flash("Impossible de supprimer ce genre : il est utilisé par un film ou un étudiant.", "error")
                return redirect(url_for("admin"))
            mycursor.execute("DELETE FROM GENRE WHERE id=%s", (id,))
            mydb.commit()
            flash("Genre supprimé !")
            return redirect(url_for("admin"))

        #Ajouter un réalisateur
        if form_type == "add_director":
            nom = request.form["nom"]
            
            # Vérifier si le réalisateur existe déjà (même nom)
            mycursor.execute(
                "SELECT COUNT(*) AS nb FROM REALISATEUR WHERE LOWER(nom)=LOWER(%s)",
                (nom,)
            )
            result = mycursor.fetchone()
            if result["nb"] > 0:
                flash("Ce réalisateur existe déjà !", "error")
                return redirect(url_for("admin", action="add_director"))
            
            mycursor.execute(
                "INSERT INTO REALISATEUR (nom) VALUES (%s)",
                (nom,)
            )
            mydb.commit()
            flash("Réalisateur ajouté !")
            return redirect(url_for("admin"))
        
        # Modifier un réalisateur
        if form_type == "edit_director":
            id = request.form["id"]
            nom = request.form["nom"]
            mycursor.execute(
                "UPDATE REALISATEUR SET nom=%s WHERE id=%s",
                (nom, id)
            )
            mydb.commit()
            flash("Réalisateur modifié !")
            return redirect(url_for("admin"))
        
        # Supprimer un réalisateur
        if form_type == "delete_director":
            id = request.form["id"]
            # Vérifier si le réalisateur est utilisé par un film (table DIRECTION)
            mycursor.execute("SELECT COUNT(*) AS nb FROM DIRECTION WHERE id_realisateur=%s", (id,))
            used_by_film = mycursor.fetchone()["nb"]
            if used_by_film > 0:
                flash("Impossible de supprimer ce réalisateur : il est utilisé par un film.", "error")
                return redirect(url_for("admin"))
            mycursor.execute("DELETE FROM REALISATEUR WHERE id=%s", (id,))
            mydb.commit()
            flash("Réalisateur supprimé !")
            return redirect(url_for("admin"))
            
    # Pour modification/suppression d'un étudiant
    edit_student = None
    if action in ["edit_student", "delete_student"] and edit_id:
        mycursor.execute("SELECT * FROM ETUDIANT WHERE id=%s", (edit_id,))
        edit_student = mycursor.fetchone()

    # Pour modification/suppression d'un film
    edit_film = None
    if action in ["edit_film", "delete_film"] and edit_id:
        mycursor.execute("SELECT * FROM FILM WHERE id=%s", (edit_id,))
        edit_film = mycursor.fetchone()
        if edit_film:
            # Récupérer les genres associés
            mycursor.execute("SELECT id_genre FROM APPARTENANCE WHERE id_film=%s", (edit_id,))
            edit_film["genres_ids"] = [row["id_genre"] for row in mycursor.fetchall()]
            # Récupérer les réalisateurs associés
            mycursor.execute("SELECT id_realisateur FROM DIRECTION WHERE id_film=%s", (edit_id,))
            edit_film["directors_ids"] = [row["id_realisateur"] for row in mycursor.fetchall()]

    # Pour modification/suppression d'un genre
    edit_genre = None
    if action in ["edit_genre", "delete_genre"] and edit_id:
        mycursor.execute("SELECT * FROM GENRE WHERE id=%s", (edit_id,))
        edit_genre = mycursor.fetchone()

    # Pour modification/suppression d'un réalisateur
    edit_director = None
    if action in ["edit_director", "delete_director"] and edit_id:
        mycursor.execute("SELECT * FROM REALISATEUR WHERE id=%s", (edit_id,))
        edit_director = mycursor.fetchone()

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    students = getStudentsPaginated(offset=offset, limit=per_page)
    total = countStudents()
    has_next = offset + per_page < total

    # Pour les formulaires
    mycursor.execute("SELECT id, nom FROM FILM")
    films = mycursor.fetchall()
    mycursor.execute("SELECT id, nom FROM GENRE")
    genres = mycursor.fetchall()
    mycursor.execute("SELECT id, nom FROM REALISATEUR")
    directors = mycursor.fetchall()

    return render_template(
        "pages/admin.html",
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
        edit_director=edit_director
    )