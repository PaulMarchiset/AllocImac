import mysql.connector

from modele import getAllStudents, getStudentById, oneFilm, oneDirector, allGenres, top5Decennies, top5Genre, top5Film, top5Realisateur, getStudentsPaginated, countStudents, search_query, mycursor, mydb

from flask import Flask, render_template, request, redirect, url_for, flash

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

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("search", "").strip()
    films, directors, students = [], [], []

    if q:
        films, directors, students = search_query(q)

    return render_template("pages/search.html", query=q, films=films, directors=directors, students=students)

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
            mycursor.execute(
                "UPDATE FILM SET nom=%s, annee=%s WHERE id=%s",
                (nom, annee, id)
            )
            mydb.commit()
            flash("Film modifié !")
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