# -----------------------------------------------------------------------------------------
# ----------------------------------- SETUP MYSQL -----------------------------------------
# -----------------------------------------------------------------------------------------

from werkzeug.security import generate_password_hash, check_password_hash

import mysql.connector

import re

import os

from flask import request, redirect, url_for, flash

mydb = mysql.connector.connect(
    host=os.getenv("DB_IP"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database="allocimac"
)

mycursor = mydb.cursor(dictionary=True)


# -----------------------------------------------------------------------------------------
# -------------------------------------- STUDENTS -----------------------------------------
# -----------------------------------------------------------------------------------------


def getAllStudents():
    mycursor.execute("SELECT * FROM etudiant ORDER BY nom, prenom ASC")
    students = mycursor.fetchall()
    return students


def getStudentById(id):
    mycursor.execute(
        """
        SELECT 
            e.prenom AS etu_prenom,
            e.nom AS etu_nom, 
            f.nom AS film_nom,
            f.id AS film_id, 
            g.nom AS genre_nom,
            g.id AS genre_id
        FROM etudiant e 
        JOIN film f ON e.id_film = f.id 
        JOIN genre g ON e.id_genre = g.id 
        WHERE e.id = %s
    """,
        (id,),
    )
    result = mycursor.fetchone()
    if result:
        return {
            "prenom": result["etu_prenom"],
            "nom": result["etu_nom"],
            "film": {"nom": result["film_nom"], "id": result["film_id"]},
            "genre": {"nom": result["genre_nom"], "id": result["genre_id"]},
        }
    return None

def userCount():
    mycursor.execute("SELECT COUNT(id) AS total FROM utilisateur")
    result = mycursor.fetchone()
    return result if result else 0

# -----------------------------------------------------------------------------------------
# ------------------------------------- GET film ------------------------------------------
# -----------------------------------------------------------------------------------------


def oneFilm(id):
    # Main film info
    mycursor.execute(
        """
        SELECT 
            f.nom AS film_nom, 
            f.annee AS film_annee,
            COUNT(DISTINCT e.id) AS nb_etudiants
        FROM film f
        LEFT JOIN etudiant e ON f.id = e.id_film
        WHERE f.id = %s
        GROUP BY f.nom, f.annee
    """,
        (id,),
    )
    film_info = mycursor.fetchone()

    # List of directors
    mycursor.execute(
        """
        SELECT r.id, r.nom
        FROM realisateur r
        JOIN direction d ON r.id = d.id_realisateur
        WHERE d.id_film = %s
    """,
        (id,),
    )
    realisateurs = [{"id": row["id"], "nom": row["nom"]} for row in mycursor.fetchall()]

    mycursor.execute(
        """
        SELECT g.id, g.nom
        FROM genre g
        JOIN appartenance a ON g.id = a.id_genre
        WHERE a.id_film = %s
    """,
        (id,),
    )
    genres = [{"id": row["id"], "nom": row["nom"]} for row in mycursor.fetchall()]

    if film_info:
        return {
            "nom": film_info["film_nom"],
            "annee": film_info["film_annee"],
            "realisateurs": realisateurs,
            "genres": genres,
            "nb_etudiants": film_info["nb_etudiants"],
        }
    return None


# -----------------------------------------------------------------------------------------
# ----------------------------------- GET DIRECTOR ----------------------------------------
# -----------------------------------------------------------------------------------------


def oneDirector(id):
    mycursor.execute(
        """
        SELECT
            r.nom AS realisateur_nom,
            COUNT(DISTINCT d.id_film) AS nb_films,
            COUNT(DISTINCT a.id_genre) AS nb_genres
        FROM realisateur r
        JOIN direction d ON r.id = d.id_realisateur
        JOIN appartenance a ON d.id_film = a.id_film
        WHERE r.id = %s
        GROUP BY r.nom
    """,
        (id,),
    )
    director_info = mycursor.fetchone()
    if director_info:
        return {
            "nom": director_info["realisateur_nom"],
            "nb_films": director_info["nb_films"],
            "nb_genres": director_info["nb_genres"],
        }
    return None


# -----------------------------------------------------------------------------------------
# ------------------------------------- GET GENRES ----------------------------------------
# -----------------------------------------------------------------------------------------


def allGenres():
    mycursor.execute(
        """
        SELECT 
            g.id AS genre_id,
            g.nom AS nom_genre, 
            f.id AS film_id, 
            f.nom AS nom_film
        FROM genre g 
        LEFT JOIN appartenance a ON g.id = a.id_genre 
        LEFT JOIN film f ON a.id_film = f.id
        ORDER BY g.nom
    """
    )
    rows = mycursor.fetchall()

    genres_dict = {}
    for row in rows:
        genre_id = row["genre_id"]
        if genre_id not in genres_dict:
            genres_dict[genre_id] = {
                "id": genre_id,
                "nom": row["nom_genre"],
                "nom_films": [],
            }
        genres_dict[genre_id]["nom_films"].append(
            {"id": row["film_id"], "nom": row["nom_film"]}
        )

    return list(genres_dict.values())


# -----------------------------------------------------------------------------------------
# ---------------------------------------- TOP 5 ------------------------------------------
# -----------------------------------------------------------------------------------------


def top5Film():
    mycursor.execute(
        """
        SELECT 
            film.id AS film_id,
            film.nom AS nom_film, 
            film.annee AS annee_film,
            COUNT(etudiant.id) AS nb_etudiants
        FROM film
        JOIN etudiant ON film.id = etudiant.id_film
        GROUP BY film.id
        ORDER BY nb_etudiants DESC
        LIMIT 5
    """
    )
    results = mycursor.fetchall()

    top_films = []
    for result in results:
        film_id = result["film_id"]
        mycursor.execute(
            """
            SELECT r.id, r.nom
            FROM realisateur r
            JOIN direction d ON r.id = d.id_realisateur
            WHERE d.id_film = %s
        """,
            (film_id,),
        )
        realisateurs = [
            {"id": row["id"], "nom": row["nom"]} for row in mycursor.fetchall()
        ]

        top_films.append(
            {
                "id": film_id,
                "nom": result["nom_film"],
                "annee": result["annee_film"],
                "realisateurs": realisateurs,
                "nb_etudiants": result["nb_etudiants"],
            }
        )

    return top_films


def top5Genre():
    mycursor.execute(
        """
        SELECT genre.id AS id_genre, genre.nom AS nom_genre, COUNT(etudiant.id) AS nb_etudiants
        FROM genre
        LEFT JOIN etudiant ON genre.id = etudiant.id_genre
        GROUP BY genre.id, genre.nom
        ORDER BY nb_etudiants DESC
        LIMIT 5
    """
    )
    results = mycursor.fetchall()

    top_genres = []
    for result in results:
        genre_name = result["nom_genre"]

        top_genres.append(
            {
                "id": result["id_genre"],
                "nom": genre_name,
                "nb_etudiants": result["nb_etudiants"],
            }
        )
    return top_genres


def top5Realisateur():
    mycursor.execute(
        """
        SELECT realisateur.id AS id_real, realisateur.nom AS nom_real, COUNT(etudiant.id) AS nb_etudiants
        FROM realisateur
        JOIN direction ON realisateur.id = direction.id_realisateur
        JOIN film ON direction.id_film = film.id
        JOIN etudiant ON film.id = etudiant.id_film
        GROUP BY realisateur.nom, realisateur.id
        ORDER BY nb_etudiants DESC
        LIMIT 5
    """
    )
    results = mycursor.fetchall()

    top_realisateurs = []
    for result in results:
        top_realisateurs.append(
            {
                "id": result["id_real"],
                "nom": result["nom_real"],
                "nb_etudiants": result["nb_etudiants"],
            }
        )
    return top_realisateurs


def top5Decennies():
    mycursor.execute(
        """
        SELECT CONCAT(FLOOR(film.annee / 10) * 10, 's') AS decennie, COUNT(etudiant.id) AS nb_etudiants
        FROM film
        JOIN etudiant ON film.id = etudiant.id_film
        GROUP BY decennie
        ORDER BY nb_etudiants DESC
        LIMIT 5
    """
    )
    results = mycursor.fetchall()

    top_decennies = []
    for result in results:
        top_decennies.append(
            {"decennie": result["decennie"], "nb_etudiants": result["nb_etudiants"]}
        )
    return top_decennies

def getTotalFilmRanking():
    mycursor.execute("""
        SELECT 
            film.id AS film_id,
            film.nom AS nom_film,
            film.annee AS annee_film,
            COUNT(etudiant.id) AS nb_etudiants
        FROM film
        LEFT JOIN etudiant ON film.id = etudiant.id_film
        GROUP BY film.id
        ORDER BY nb_etudiants DESC
    """)
    return mycursor.fetchall()

def getTotalGenreRanking():
    mycursor.execute(
        """
        SELECT genre.id AS id_genre, genre.nom AS nom_genre, COUNT(etudiant.id) AS nb_etudiants
        FROM genre
        LEFT JOIN etudiant ON genre.id = etudiant.id_genre
        GROUP BY genre.id, genre.nom
        ORDER BY nb_etudiants DESC
    """
    )
    return mycursor.fetchall()


# -----------------------------------------------------------------------------------------
# ------------------------------------ SEARCH QUERY ---------------------------------------
# -----------------------------------------------------------------------------------------


def search_query(q):
    film_query = """
        SELECT * FROM film WHERE nom LIKE %s
    """
    mycursor.execute(film_query, (f"%{q}%",))
    films = mycursor.fetchall()

    director_query = """
        SELECT * FROM realisateur WHERE nom LIKE %s
    """
    mycursor.execute(director_query, (f"%{q}%",))
    directors = mycursor.fetchall()

    student_query = """
        SELECT * FROM etudiant WHERE prenom LIKE %s OR nom LIKE %s OR CONCAT(prenom, ' ', nom) LIKE %s
    """
    mycursor.execute(student_query, (f"%{q}%", f"%{q}%",f"%{q}%"))
    students = mycursor.fetchall()

    return films, directors, students


# -----------------------------------------------------------------------------------------
# ----------------------------------- USER MANAGEMENT -------------------------------------
# -----------------------------------------------------------------------------------------


def is_strong_password(password):
    has_lower = re.search(r"[a-z]", password)
    has_upper = re.search(r"[A-Z]", password)
    has_digit = re.search(r"\d", password)
    has_symbol = re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    has_eight_chars = len(password) >= 8
    return all([has_lower, has_upper, has_digit, has_symbol, has_eight_chars])


def create_user(username, password, confirm_password):
    username = username.strip()
    password = password.strip()
    confirm_password = confirm_password.strip()

    if not username or not password or not confirm_password:
        return False, "Username and password cannot be empty."

    if password != confirm_password:
        return False, "Passwords do not match."

    if not is_strong_password(password):
        return (False, 
            "Le mot de passe doit contenir au moins 8 caractères, "
            "une majuscule, une minuscule, un chiffre et un symbole."
        )

    try:
        # Check if username already exists
        mycursor.execute("SELECT 1 FROM utilisateur WHERE username = %s", (username,))
        if mycursor.fetchone():
            return False, "Username already exists."

        # Create user
        hashed_pw = generate_password_hash(password)
        mycursor.execute(
            "INSERT INTO utilisateur (username, password) VALUES (%s, %s)",
            (username, hashed_pw),
        )
        mydb.commit()
        return True, "success"

    except Exception:
        return False, "An error occurred. Please try again later."
    

def verify_user(username, password):
    mycursor.execute(
        "SELECT password FROM utilisateur WHERE username = %s", (username,)
    )
    result = mycursor.fetchone()
    if result:
        hashed_pw = result["password"]
        return check_password_hash(hashed_pw, password)
    else:
        return False


def getUserInfo(username):
    mycursor.execute(
        """
        SELECT 
            u.username AS username,
            e.prenom AS etu_prenom,
            e.nom AS etu_nom, 
            f.nom AS film_nom,
            f.id AS film_id, 
            g.nom AS genre_nom,
            g.id AS genre_id
        FROM etudiant e 
        JOIN film f ON e.id_film = f.id 
        JOIN genre g ON e.id_genre = g.id 
        JOIN utilisateur u ON e.id = u.id_etudiant
        WHERE u.username = %s
    """,
        (username,),
    )
    result = mycursor.fetchone()
    if result:
        return {
            "username": result["username"],
            "prenom": result["etu_prenom"],
            "nom": result["etu_nom"],
            "film": {"nom": result["film_nom"], "id": result["film_id"]},
            "genre": {"nom": result["genre_nom"], "id": result["genre_id"]},
        }
    return None


def getUpdateInfo():
    mycursor.execute("""SELECT id, nom FROM film ORDER BY nom ASC""")
    films = mycursor.fetchall()
    mycursor.execute("""SELECT id, nom FROM genre ORDER BY nom ASC""")
    genres = mycursor.fetchall()
    return {
        "films": [{"id": film["id"], "nom": film["nom"]} for film in films],
        "genres": [{"id": genre["id"], "nom": genre["nom"]} for genre in genres],
    }


def saveUpdateInfo(username, prenom, nom, id_film, id_genre):
    mycursor.execute(
        """SELECT id_etudiant FROM utilisateur WHERE username = %s""", (username,)
    )
    user = mycursor.fetchone()
    if not user or user["id_etudiant"] is None:
        mycursor.execute(
            """INSERT INTO etudiant (prenom, nom, id_film, id_genre) VALUES (%s, %s, %s, %s)""",
            (prenom, nom, id_film, id_genre),
        )
        mydb.commit()
        mycursor.execute("""SELECT LAST_INSERT_ID()""")
        etudiant_id = mycursor.fetchone()["LAST_INSERT_ID()"]
        mycursor.execute(
            """UPDATE utilisateur SET id_etudiant = %s WHERE username = %s""",
            (etudiant_id, username),
        )      
    else:
        etudiant_id = user["id_etudiant"]
        mycursor.execute(
            """UPDATE etudiant SET prenom = %s, nom = %s, id_film = %s, id_genre = %s WHERE id = %s""",
            (prenom, nom, id_film, id_genre, etudiant_id),
        )
    mydb.commit()


# -----------------------------------------------------------------------------------------
# ---------------------------------------- ADMIN ------------------------------------------
# -----------------------------------------------------------------------------------------


def getAllUsers():
    mycursor.execute("""
        SELECT u.id, u.username, u.id_etudiant, e.prenom, e.nom
        FROM utilisateur u
        LEFT JOIN etudiant e ON u.id_etudiant = e.id
        ORDER BY u.username
    """)
    return mycursor.fetchall()


def getUserById(id):
    mycursor.execute("""
        SELECT u.id, u.username, u.id_etudiant, e.prenom, e.nom
        FROM utilisateur u
        LEFT JOIN etudiant e ON u.id_etudiant = e.id
        WHERE u.id = %s
    """, (id,))
    return mycursor.fetchone()


def addUser(username, password, confirm_password, id_etudiant):
    # Vérifier que le nom d'utilsateur n'existe pas déjà
    mycursor.execute("SELECT COUNT(*) AS nb FROM utilisateur WHERE username=%s", (username,))
    if mycursor.fetchone()["nb"] > 0:
        flash("Ce nom d'utilisateur existe déjà !", "error")
        return redirect(url_for("admin", action="add_user", page=request.args.get("page", 1)))

    # Vérifier la force du mot de passe
    if not is_strong_password(password):
        flash("Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un symbole.", "error")
        return redirect(url_for("admin", action="add_user", page=request.args.get("page", 1)))

    # Vérifier la confirmation du mot de passe
    if password != confirm_password:
        flash("Les mots de passe ne correspondent pas.", "error")
        return redirect(url_for("admin", action="add_user", page=request.args.get("page", 1)))

    # Vérifier qu'aucun utilisateur n'est déjà lié à cet étudiant
    if id_etudiant:
        mycursor.execute("SELECT COUNT(*) AS nb FROM utilisateur WHERE id_etudiant=%s", (id_etudiant,))
        if mycursor.fetchone()["nb"] > 0:
            flash("Cet étudiant a déjà un compte utilisateur !", "error")
            return redirect(url_for("admin", action="add_user", page=request.args.get("page", 1)))

    hashed_pw = generate_password_hash(password)
    mycursor.execute(
        "INSERT INTO utilisateur (username, password, id_etudiant) VALUES (%s, %s, %s)",
        (username, hashed_pw, id_etudiant if id_etudiant else None)
    )
    mydb.commit()
    flash("Utilisateur ajouté !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def editUser(id, username, password, confirm_password, id_etudiant):
    mycursor.execute("SELECT COUNT(*) AS nb FROM utilisateur WHERE username=%s AND id!=%s", (username, id))
    if mycursor.fetchone()["nb"] > 0:
        flash("Ce nom d'utilisateur existe déjà !", "error")
        return redirect(url_for("admin", action="edit_user", page=request.args.get("page", 1)))
    # Vérifier qu'aucun autre utilisateur n'est déjà lié à cet étudiant
    if id_etudiant:
        mycursor.execute("SELECT COUNT(*) AS nb FROM utilisateur WHERE id_etudiant=%s AND id!=%s", (id_etudiant, id))
        if mycursor.fetchone()["nb"] > 0:
            flash("Cet étudiant a déjà un compte utilisateur !", "error")
            return redirect(url_for("admin", action="edit_user", id=id, page=request.args.get("page", 1)))
    # Si mot de passe fourni, vérifier la force et la confirmation
    if password:
        if not is_strong_password(password):
            flash("Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un symbole.", "error")
            return redirect(url_for("admin", action="edit_user", id=id, page=request.args.get("page", 1)))
        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "error")
            return redirect(url_for("admin", action="edit_user", id=id, page=request.args.get("page", 1)))
        hashed_pw = generate_password_hash(password)
        mycursor.execute(
            "UPDATE utilisateur SET username=%s, password=%s, id_etudiant=%s WHERE id=%s",
            (username, hashed_pw, id_etudiant if id_etudiant else None, id)
        )
    else:
        mycursor.execute(
            "UPDATE utilisateur SET username=%s, id_etudiant=%s WHERE id=%s",
            (username, id_etudiant if id_etudiant else None, id)
        )
    mydb.commit()
    flash("Utilisateur modifié !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def deleteUser(id):
    mycursor.execute("DELETE FROM utilisateur WHERE id=%s", (id,))
    mydb.commit()
    flash("Utilisateur supprimé !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def addStudent(prenom, nom, id_film, id_genre):
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM etudiant WHERE prenom=%s AND nom=%s AND id_film=%s AND id_genre=%s",
        (prenom, nom, id_film, id_genre),
    )
    result = mycursor.fetchone()
    if result["nb"] > 0:
        flash(
            "Un étudiant avec ce prénom, ce nom, ce film préféré et ce genre préféré existe déjà !",
            "error",
        )
        return redirect(url_for("admin", action="add_student", page=request.args.get("page", 1)))

    mycursor.execute(
        "INSERT INTO etudiant (prenom, nom, id_film, id_genre) VALUES (%s ,%s, %s, %s)",
        (prenom, nom, id_film, id_genre),
    )
    mydb.commit()
    flash("Étudiant ajouté !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def editStudent(id, prenom, nom, id_film, id_genre):
    # Vérifier qu'il n'existe pas déjà un étudiant avec ce prénom, nom, film et genre (autre que celui qu'on modifie)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM etudiant WHERE prenom=%s AND nom=%s AND id_film=%s AND id_genre=%s AND id!=%s",
        (prenom, nom, id_film, id_genre, id),
    )
    result = mycursor.fetchone()
    if result["nb"] > 0:
        flash(
            "Un étudiant avec ce prénom, ce nom, ce film préféré et ce genre préféré existe déjà !",
            "error",
        )
        return redirect(url_for("admin", action="edit_student", id=id, page=request.args.get("page", 1)))

    mycursor.execute(
        "UPDATE etudiant SET prenom=%s, nom=%s, id_film=%s, id_genre=%s WHERE id=%s",
        (prenom, nom, id_film, id_genre, id),
    )
    mydb.commit()
    flash("Étudiant modifié !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def deleteStudent(id):
    mycursor.execute("DELETE FROM utilisateur WHERE id_etudiant=%s", (id,))
    mydb.commit()
    mycursor.execute("DELETE FROM etudiant WHERE id=%s", (id,))
    mydb.commit()
    flash("Étudiant supprimé !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def addFilm(nom, annee):
    # Vérifier si le film existe déjà (même nom et année)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM film WHERE LOWER(nom)=LOWER(%s) AND annee=%s",
        (nom, annee),
    )
    result = mycursor.fetchone()
    if result["nb"] > 0:
        flash("Ce film existe déjà !", "error")
        return redirect(url_for("admin", action="add_film", page=request.args.get("page", 1)))

    # Insérer le film
    mycursor.execute(
        "INSERT INTO film (nom, annee) VALUES (%s, %s)", (nom, annee)
    )
    film_id = mycursor.lastrowid

    # Récupérer les genres et réalisateurs sélectionnés
    genres_ids = request.form.getlist("genres")
    directors_ids = request.form.getlist("directors")

    # Insérer dans appartenance (film-genre)
    for genre_id in genres_ids:
        mycursor.execute(
            "INSERT INTO appartenance (id_film, id_genre) VALUES (%s, %s)",
            (film_id, genre_id),
        )
    # Insérer dans direction (film-réalisateur)
    for director_id in directors_ids:
        mycursor.execute(
            "INSERT INTO direction (id_film, id_realisateur) VALUES (%s, %s)",
            (film_id, director_id),
        )
    mydb.commit()
    flash("Film ajouté !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def editFilm(id, nom, annee, genres_ids, directors_ids):
    # Vérifier qu'il n'existe pas déjà un film avec ce titre ET cette année (autre que celui qu'on modifie)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM film WHERE LOWER(nom)=LOWER(%s) AND annee=%s AND id!=%s",
        (nom, annee, id),
    )
    result = mycursor.fetchone()
    if result["nb"] > 0:
        flash("Ce film existe déjà !", "error")
        return redirect(url_for("admin", action="edit_film", id=id, page=request.args.get("page", 1)))

    mycursor.execute(
        "UPDATE film SET nom=%s, annee=%s WHERE id=%s", (nom, annee, id)
    )

    # Mettre à jour les genres associés
    mycursor.execute("DELETE FROM appartenance WHERE id_film=%s", (id,))
    for genre_id in genres_ids:
        mycursor.execute(
            "INSERT INTO appartenance (id_film, id_genre) VALUES (%s, %s)",
            (id, genre_id),
        )

    # Mettre à jour les réalisateurs associés
    mycursor.execute("DELETE FROM direction WHERE id_film=%s", (id,))
    for director_id in directors_ids:
        mycursor.execute(
            "INSERT INTO direction (id_film, id_realisateur) VALUES (%s, %s)",
            (id, director_id),
        )

    mydb.commit()
    flash("Film modifié !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def deleteFilm(id):
    # Vérifier si le film est utilisé par un étudiant
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM etudiant WHERE id_film=%s", (id,)
    )
    used_by_student = mycursor.fetchone()["nb"]
    if used_by_student > 0:
        flash(
            "Impossible de supprimer ce film : il est utilisé par un étudiant.",
            "error",
        )
        return redirect(url_for("admin", page=request.args.get("page", 1)))
    # Supprimer les liens avec les genres (appartenance)
    mycursor.execute("DELETE FROM appartenance WHERE id_film=%s", (id,))
    # Supprimer les liens avec les réalisateurs (direction)
    mycursor.execute("DELETE FROM direction WHERE id_film=%s", (id,))
    # Supprimer le film
    mycursor.execute("DELETE FROM film WHERE id=%s", (id,))
    mydb.commit()
    flash("Film supprimé !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def addGenre(nom):
    # Vérifier si le genre existe déjà (même nom)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM genre WHERE LOWER(nom)=LOWER(%s)", (nom,)
    )
    result = mycursor.fetchone()
    if result["nb"] > 0:
        flash("Ce genre existe déjà !", "error")
        return redirect(url_for("admin", action="add_genre", page=request.args.get("page", 1)))

    mycursor.execute("INSERT INTO genre (nom) VALUES (%s)", (nom,))
    mydb.commit()
    flash("Genre ajouté !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def editGenre(id, nom):
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM genre WHERE LOWER(nom)=LOWER(%s) AND id!=%s",
        (nom, id),
    )
    result = mycursor.fetchone()
    if result["nb"] > 0:
        flash("Ce genre existe déjà !", "error")
        return redirect(url_for("admin", action="edit_genre", id=id, page=request.args.get("page", 1)))
    mycursor.execute("UPDATE genre SET nom=%s WHERE id=%s", (nom, id))
    mydb.commit()
    flash("Genre modifié !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def deleteGenre(id):
    # Vérifier si le genre est utilisé par un film (table appartenance)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM appartenance WHERE id_genre=%s", (id,)
    )
    used_by_film = mycursor.fetchone()["nb"]
    # Vérifier si le genre est utilisé par un étudiant
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM etudiant WHERE id_genre=%s", (id,)
    )
    used_by_student = mycursor.fetchone()["nb"]
    if used_by_film > 0 or used_by_student > 0:
        flash(
            "Impossible de supprimer ce genre : il est utilisé par un film ou un étudiant.",
            "error",
        )
        return redirect(url_for("admin", page=request.args.get("page", 1)))
    mycursor.execute("DELETE FROM genre WHERE id=%s", (id,))
    mydb.commit()
    flash("Genre supprimé !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def addDirector(nom):
    # Vérifier si le réalisateur existe déjà (même nom)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM realisateur WHERE LOWER(nom)=LOWER(%s)",
        (nom,),
    )
    result = mycursor.fetchone()
    if result["nb"] > 0:
        flash("Ce réalisateur existe déjà !", "error")
        return redirect(url_for("admin", action="add_director", page=request.args.get("page", 1)))

    mycursor.execute("INSERT INTO realisateur (nom) VALUES (%s)", (nom,))
    mydb.commit()
    flash("Réalisateur ajouté !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def editDirector(id, nom):
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM realisateur WHERE LOWER(nom)=LOWER(%s) AND id!=%s",
        (nom, id),
    )
    result = mycursor.fetchone()
    if result["nb"] > 0:
        flash("Ce réalisateur existe déjà !", "error")
        return redirect(url_for("admin", action="edit_director", id=id, page=request.args.get("page", 1)))
    mycursor.execute("UPDATE realisateur SET nom=%s WHERE id=%s", (nom, id))
    mydb.commit()
    flash("Réalisateur modifié !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def deleteDirector(id):
    # Vérifier si le réalisateur est utilisé par un film (table direction)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM direction WHERE id_realisateur=%s", (id,)
    )
    used_by_film = mycursor.fetchone()["nb"]
    if used_by_film > 0:
        flash(
            "Impossible de supprimer ce réalisateur : il est utilisé par un film.",
            "error",
        )
        return redirect(url_for("admin", page=request.args.get("page", 1)))
    mycursor.execute("DELETE FROM realisateur WHERE id=%s", (id,))
    mydb.commit()
    flash("Réalisateur supprimé !")
    return redirect(url_for("admin", page=request.args.get("page", 1)))


def getStudentByIdFull(id):
    mycursor.execute("SELECT * FROM etudiant WHERE id=%s", (id,))
    return mycursor.fetchone()


def getFilmByIdWithLinks(id):
    mycursor.execute("SELECT * FROM film WHERE id=%s", (id,))
    film = mycursor.fetchone()
    if film:
        # Récupérer les genres associés
        mycursor.execute("SELECT id_genre FROM appartenance WHERE id_film=%s", (id,))
        film["genres_ids"] = [row["id_genre"] for row in mycursor.fetchall()]
        # Récupérer les réalisateurs associés
        mycursor.execute("SELECT id_realisateur FROM direction WHERE id_film=%s", (id,))
        film["directors_ids"] = [row["id_realisateur"] for row in mycursor.fetchall()]
    return film


def getGenreById(id):
    mycursor.execute("SELECT * FROM genre WHERE id=%s", (id,))
    return mycursor.fetchone()


def getDirectorById(id):
    mycursor.execute("SELECT * FROM realisateur WHERE id=%s", (id,))
    return mycursor.fetchone()


def getAllFilms():
    mycursor.execute("SELECT id, nom, annee FROM film ORDER BY nom")
    return mycursor.fetchall()


def getAllGenres():
    mycursor.execute("SELECT id, nom FROM genre ORDER BY nom")
    return mycursor.fetchall()


def getAllDirectors():
    mycursor.execute("SELECT id, nom FROM realisateur ORDER BY SUBSTRING_INDEX(nom, ' ', -1), nom")
    return mycursor.fetchall()


def getAllStudentsShort():
    mycursor.execute("SELECT id, prenom, nom FROM etudiant ORDER BY nom, prenom")
    return mycursor.fetchall()


def getStudentsPaginated(offset=0, limit=10):
    mycursor.execute(
        """
        SELECT e.id, e.prenom, e.nom, u.username AS username, f.nom AS film_nom, g.nom AS genre_nom
        FROM etudiant e
        JOIN film f ON e.id_film = f.id
        JOIN genre g ON e.id_genre = g.id
        LEFT JOIN utilisateur u ON e.id = u.id_etudiant
        ORDER BY e.id
        LIMIT %s OFFSET %s
    """,
        (limit, offset),
    )
    return mycursor.fetchall()


def countStudents():
    mycursor.execute("SELECT COUNT(*) AS total FROM etudiant")
    return mycursor.fetchone()["total"]
