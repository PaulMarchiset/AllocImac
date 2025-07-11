# -----------------------------------------------------------------------------------------
# ----------------------------------- SETUP MYSQL -----------------------------------------
# -----------------------------------------------------------------------------------------

from werkzeug.security import generate_password_hash, check_password_hash

import mysql.connector

import re

mydb = mysql.connector.connect(
    host="localhost", user="root", password="admin", database="allocimac"
)

mycursor = mydb.cursor(dictionary=True)


# -----------------------------------------------------------------------------------------
# -------------------------------------- STUDENTS -----------------------------------------
# -----------------------------------------------------------------------------------------


def getAllStudents():
    mycursor.execute("SELECT * FROM ETUDIANT ORDER BY nom, prenom ASC")
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
        FROM ETUDIANT e 
        JOIN FILM f ON e.id_film = f.id 
        JOIN GENRE g ON e.id_genre = g.id 
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
# ------------------------------------- GET FILM ------------------------------------------
# -----------------------------------------------------------------------------------------


def oneFilm(id):
    # Main film info
    mycursor.execute(
        """
        SELECT 
            f.nom AS film_nom, 
            f.annee AS film_annee,
            COUNT(DISTINCT e.id) AS nb_etudiants
        FROM FILM f
        LEFT JOIN ETUDIANT e ON f.id = e.id_film
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
        FROM REALISATEUR r
        JOIN DIRECTION d ON r.id = d.id_realisateur
        WHERE d.id_film = %s
    """,
        (id,),
    )
    realisateurs = [{"id": row["id"], "nom": row["nom"]} for row in mycursor.fetchall()]

    mycursor.execute(
        """
        SELECT g.id, g.nom
        FROM genre g
        JOIN APPARTENANCE a ON g.id = a.id_genre
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
        FROM REALISATEUR r
        JOIN DIRECTION d ON r.id = d.id_realisateur
        JOIN APPARTENANCE a ON d.id_film = a.id_film
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
        FROM GENRE g 
        LEFT JOIN APPARTENANCE a ON g.id = a.id_genre 
        LEFT JOIN FILM f ON a.id_film = f.id
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
            FILM.id AS film_id,
            FILM.nom AS nom_film, 
            FILM.annee AS annee_film,
            COUNT(ETUDIANT.id) AS nb_etudiants
        FROM FILM
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        GROUP BY FILM.id
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
            FROM REALISATEUR r
            JOIN DIRECTION d ON r.id = d.id_realisateur
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
        SELECT GENRE.id AS id_genre, GENRE.nom AS nom_genre, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM GENRE
        LEFT JOIN ETUDIANT ON GENRE.id = ETUDIANT.id_genre
        GROUP BY GENRE.id, GENRE.nom
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
        SELECT REALISATEUR.id AS id_real, REALISATEUR.nom AS nom_real, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM REALISATEUR
        JOIN DIRECTION ON REALISATEUR.id = DIRECTION.id_realisateur
        JOIN FILM ON DIRECTION.id_film = FILM.id
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        GROUP BY REALISATEUR.nom, REALISATEUR.id
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
        SELECT CONCAT(FLOOR(FILM.annee / 10) * 10, 's') AS decennie, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM FILM
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
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
            FILM.id AS film_id,
            FILM.nom AS nom_film,
            FILM.annee AS annee_film,
            COUNT(ETUDIANT.id) AS nb_etudiants
        FROM FILM
        LEFT JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        GROUP BY FILM.id
        ORDER BY nb_etudiants DESC
    """)
    return mycursor.fetchall()

def getTotalGenreRanking():
    mycursor.execute(
        """
        SELECT GENRE.id AS id_genre, GENRE.nom AS nom_genre, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM GENRE
        LEFT JOIN ETUDIANT ON GENRE.id = ETUDIANT.id_genre
        GROUP BY GENRE.id, GENRE.nom
        ORDER BY nb_etudiants DESC
    """
    )
    return mycursor.fetchall()


# -----------------------------------------------------------------------------------------
# ------------------------------------ SEARCH QUERY ---------------------------------------
# -----------------------------------------------------------------------------------------


def search_query(q):
    film_query = """
        SELECT * FROM FILM WHERE nom LIKE %s
    """
    mycursor.execute(film_query, (f"%{q}%",))
    films = mycursor.fetchall()

    director_query = """
        SELECT * FROM REALISATEUR WHERE nom LIKE %s
    """
    mycursor.execute(director_query, (f"%{q}%",))
    directors = mycursor.fetchall()

    student_query = """
        SELECT * FROM ETUDIANT WHERE prenom LIKE %s OR nom LIKE %s OR CONCAT(prenom, ' ', nom) LIKE %s
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
        mycursor.execute("SELECT 1 FROM UTILISATEUR WHERE username = %s", (username,))
        if mycursor.fetchone():
            return False, "Username already exists."

        # Create user
        hashed_pw = generate_password_hash(password)
        mycursor.execute(
            "INSERT INTO UTILISATEUR (username, password) VALUES (%s, %s)",
            (username, hashed_pw),
        )
        mydb.commit()
        return True, "success"

    except Exception:
        return False, "An error occurred. Please try again later."
    

def verify_user(username, password):
    mycursor.execute(
        "SELECT password FROM UTILISATEUR WHERE username = %s", (username,)
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
        FROM ETUDIANT e 
        JOIN FILM f ON e.id_film = f.id 
        JOIN GENRE g ON e.id_genre = g.id 
        JOIN UTILISATEUR u ON e.id = u.id_etudiant
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
    mycursor.execute("""SELECT id, nom FROM FILM ORDER BY nom ASC""")
    films = mycursor.fetchall()
    mycursor.execute("""SELECT id, nom FROM GENRE ORDER BY nom ASC""")
    genres = mycursor.fetchall()
    return {
        "films": [{"id": film["id"], "nom": film["nom"]} for film in films],
        "genres": [{"id": genre["id"], "nom": genre["nom"]} for genre in genres],
    }


def saveUpdateInfo(username, prenom, nom, id_film, id_genre):
    mycursor.execute(
        """SELECT id_etudiant FROM UTILISATEUR WHERE username = %s""", (username,)
    )
    user = mycursor.fetchone()
    if not user or user["id_etudiant"] is None:
        mycursor.execute(
            """INSERT INTO ETUDIANT (prenom, nom, id_film, id_genre) VALUES (%s, %s, %s, %s)""",
            (prenom, nom, id_film, id_genre),
        )
        mydb.commit()
        mycursor.execute("""SELECT LAST_INSERT_ID()""")
        etudiant_id = mycursor.fetchone()["LAST_INSERT_ID()"]
        mycursor.execute(
            """UPDATE UTILISATEUR SET id_etudiant = %s WHERE username = %s""",
            (etudiant_id, username),
        )      
    else:
        etudiant_id = user["id_etudiant"]
        mycursor.execute(
            """UPDATE ETUDIANT SET prenom = %s, nom = %s, id_film = %s, id_genre = %s WHERE id = %s""",
            (prenom, nom, id_film, id_genre, etudiant_id),
        )
    mydb.commit()


# -----------------------------------------------------------------------------------------
# ---------------------------------------- ADMIN ------------------------------------------
# -----------------------------------------------------------------------------------------


def getAllUsers():
    mycursor.execute("""
        SELECT u.id, u.username, u.id_etudiant, e.prenom, e.nom
        FROM UTILISATEUR u
        LEFT JOIN ETUDIANT e ON u.id_etudiant = e.id
        ORDER BY u.username
    """)
    return mycursor.fetchall()


def getUserById(id):
    mycursor.execute("""
        SELECT u.id, u.username, u.id_etudiant, e.prenom, e.nom
        FROM UTILISATEUR u
        LEFT JOIN ETUDIANT e ON u.id_etudiant = e.id
        WHERE u.id = %s
    """, (id,))
    return mycursor.fetchone()


def addUser(username, password, confirm_password, id_etudiant):
    # Vérifier que le nom d'utilsateur n'existe pas déjà
    mycursor.execute("SELECT COUNT(*) AS nb FROM UTILISATEUR WHERE username=%s", (username,))
    if mycursor.fetchone()["nb"] > 0:
        return False, "Ce nom d'utilisateur existe déjà !"

    # Vérifier la force du mot de passe
    if not is_strong_password(password):
        return False, "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un symbole."

    # Vérifier la confirmation du mot de passe
    if password != confirm_password:
        return False, "Les mots de passe ne correspondent pas."

    # Vérifier qu'aucun utilisateur n'est déjà lié à cet étudiant
    if id_etudiant:
        mycursor.execute("SELECT COUNT(*) AS nb FROM UTILISATEUR WHERE id_etudiant=%s", (id_etudiant,))
        if mycursor.fetchone()["nb"] > 0:
            return False, "Cet étudiant a déjà un compte utilisateur !"

    hashed_pw = generate_password_hash(password)
    mycursor.execute(
        "INSERT INTO UTILISATEUR (username, password, id_etudiant) VALUES (%s, %s, %s)",
        (username, hashed_pw, id_etudiant if id_etudiant else None)
    )
    mydb.commit()
    return True, "Utilisateur ajouté !"


def editUser(id, username, password, confirm_password, id_etudiant):
    mycursor.execute("SELECT COUNT(*) AS nb FROM UTILISATEUR WHERE username=%s AND id!=%s", (username, id))
    if mycursor.fetchone()["nb"] > 0:
        return False, "Ce nom d'utilisateur existe déjà !"
    
    # Vérifier qu'aucun autre utilisateur n'est déjà lié à cet étudiant
    if id_etudiant:
        mycursor.execute("SELECT COUNT(*) AS nb FROM UTILISATEUR WHERE id_etudiant=%s AND id!=%s", (id_etudiant, id))
        if mycursor.fetchone()["nb"] > 0:
            return False, "Cet étudiant a déjà un compte utilisateur !"
        
    # Si mot de passe fourni, vérifier la force et la confirmation
    if password:
        if not is_strong_password(password):
            return False, "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un symbole."
        if password != confirm_password:
            return False, "Les mots de passe ne correspondent pas."
        hashed_pw = generate_password_hash(password)
        mycursor.execute(
            "UPDATE UTILISATEUR SET username=%s, password=%s, id_etudiant=%s WHERE id=%s",
            (username, hashed_pw, id_etudiant if id_etudiant else None, id)
        )
    else:
        mycursor.execute(
            "UPDATE UTILISATEUR SET username=%s, id_etudiant=%s WHERE id=%s",
            (username, id_etudiant if id_etudiant else None, id)
        )
    mydb.commit()
    return True, "Utilisateur modifié !"


def deleteUser(id):
    mycursor.execute("DELETE FROM UTILISATEUR WHERE id=%s", (id,))
    mydb.commit()
    return True, "Utilisateur supprimé !"


def addStudent(prenom, nom, id_film, id_genre):
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM ETUDIANT WHERE prenom=%s AND nom=%s AND id_film=%s AND id_genre=%s",
        (prenom, nom, id_film, id_genre),
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Un étudiant avec ce prénom, ce nom, ce film préféré et ce genre préféré existe déjà !"
    mycursor.execute(
        "INSERT INTO ETUDIANT (prenom, nom, id_film, id_genre) VALUES (%s ,%s, %s, %s)",
        (prenom, nom, id_film, id_genre),
    )
    mydb.commit()
    return True, "Étudiant ajouté !"


def editStudent(id, prenom, nom, id_film, id_genre):
    # Vérifier qu'il n'existe pas déjà un étudiant avec ce prénom, nom, film et genre (autre que celui qu'on modifie)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM ETUDIANT WHERE prenom=%s AND nom=%s AND id_film=%s AND id_genre=%s AND id!=%s",
        (prenom, nom, id_film, id_genre, id),
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Un étudiant avec ce prénom, ce nom, ce film préféré et ce genre préféré existe déjà !"
    mycursor.execute(
        "UPDATE ETUDIANT SET prenom=%s, nom=%s, id_film=%s, id_genre=%s WHERE id=%s",
        (prenom, nom, id_film, id_genre, id),
    )
    mydb.commit()
    return True, "Étudiant modifié !"


def deleteStudent(id):
    mycursor.execute("DELETE FROM UTILISATEUR WHERE id_etudiant=%s", (id,))
    mydb.commit()
    mycursor.execute("DELETE FROM ETUDIANT WHERE id=%s", (id,))
    mydb.commit()
    return True, "Étudiant supprimé !"


def addFilm(nom, annee, genres_ids, directors_ids):
    # Vérifier si le film existe déjà (même nom et année)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM FILM WHERE LOWER(nom)=LOWER(%s) AND annee=%s",
        (nom, annee),
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Ce film existe déjà !"
    
    # Insérer le film
    mycursor.execute(
        "INSERT INTO FILM (nom, annee) VALUES (%s, %s)", (nom, annee)
    )
    film_id = mycursor.lastrowid

    # Insérer dans APPARTENANCE (film-genre)
    for genre_id in genres_ids:
        mycursor.execute(
            "INSERT INTO APPARTENANCE (id_film, id_genre) VALUES (%s, %s)",
            (film_id, genre_id),
        )
    # Insérer dans DIRECTION (film-réalisateur)
    for director_id in directors_ids:
        mycursor.execute(
            "INSERT INTO DIRECTION (id_film, id_realisateur) VALUES (%s, %s)",
            (film_id, director_id),
        )
    mydb.commit()
    return True, "Film ajouté !"


def editFilm(id, nom, annee, genres_ids, directors_ids):
    # Vérifier qu'il n'existe pas déjà un film avec ce titre ET cette année (autre que celui qu'on modifie)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM FILM WHERE LOWER(nom)=LOWER(%s) AND annee=%s AND id!=%s",
        (nom, annee, id),
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Ce film existe déjà !"
    mycursor.execute(
        "UPDATE FILM SET nom=%s, annee=%s WHERE id=%s", (nom, annee, id)
    )

    # Mettre à jour les genres associés
    mycursor.execute("DELETE FROM APPARTENANCE WHERE id_film=%s", (id,))
    for genre_id in genres_ids:
        mycursor.execute(
            "INSERT INTO APPARTENANCE (id_film, id_genre) VALUES (%s, %s)",
            (id, genre_id),
        )
    
    # Mettre à jour les réalisateurs associés
    mycursor.execute("DELETE FROM DIRECTION WHERE id_film=%s", (id,))
    for director_id in directors_ids:
        mycursor.execute(
            "INSERT INTO DIRECTION (id_film, id_realisateur) VALUES (%s, %s)",
            (id, director_id),
        )
    mydb.commit()
    return True, "Film modifié !"


def deleteFilm(id):
    # Vérifier si le film est utilisé par un étudiant
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM ETUDIANT WHERE id_film=%s", (id,)
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Impossible de supprimer ce film : il est utilisé par un étudiant."
    # Supprimer les liens avec les genres (APPARTENANCE)
    mycursor.execute("DELETE FROM APPARTENANCE WHERE id_film=%s", (id,))
    # Supprimer les liens avec les réalisateurs (DIRECTION)
    mycursor.execute("DELETE FROM DIRECTION WHERE id_film=%s", (id,))
    # Supprimer le film
    mycursor.execute("DELETE FROM FILM WHERE id=%s", (id,))
    mydb.commit()
    return True, "Film supprimé !"


def addGenre(nom):
    # Vérifier si le genre existe déjà (même nom)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM GENRE WHERE LOWER(nom)=LOWER(%s)", (nom,)
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Ce genre existe déjà !"
    mycursor.execute("INSERT INTO GENRE (nom) VALUES (%s)", (nom,))
    mydb.commit()
    return True, "Genre ajouté !"


def editGenre(id, nom):
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM GENRE WHERE LOWER(nom)=LOWER(%s) AND id!=%s",
        (nom, id),
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Ce genre existe déjà !"
    mycursor.execute("UPDATE GENRE SET nom=%s WHERE id=%s", (nom, id))
    mydb.commit()
    return True, "Genre modifié !"


def deleteGenre(id):
    # Vérifier si le genre est utilisé par un film (table APPARTENANCE)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM APPARTENANCE WHERE id_genre=%s", (id,)
    )
    used_by_film = mycursor.fetchone()["nb"]
    # Vérifier si le genre est utilisé par un étudiant
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM ETUDIANT WHERE id_genre=%s", (id,)
    )
    used_by_student = mycursor.fetchone()["nb"]
    if used_by_film > 0 or used_by_student > 0:
        return False, "Impossible de supprimer ce genre : il est utilisé par un film ou un étudiant."
    mycursor.execute("DELETE FROM GENRE WHERE id=%s", (id,))
    mydb.commit()
    return True, "Genre supprimé !"


def addDirector(nom):
    # Vérifier si le réalisateur existe déjà (même nom)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM REALISATEUR WHERE LOWER(nom)=LOWER(%s)",
        (nom,),
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Ce réalisateur existe déjà !"
    mycursor.execute("INSERT INTO REALISATEUR (nom) VALUES (%s)", (nom,))
    mydb.commit()
    return True, "Réalisateur ajouté !"


def editDirector(id, nom):
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM REALISATEUR WHERE LOWER(nom)=LOWER(%s) AND id!=%s",
        (nom, id),
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Ce réalisateur existe déjà !"
    mycursor.execute("UPDATE REALISATEUR SET nom=%s WHERE id=%s", (nom, id))
    mydb.commit()
    return True, "Réalisateur modifié !"


def deleteDirector(id):
    # Vérifier si le réalisateur est utilisé par un film (table DIRECTION)
    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM DIRECTION WHERE id_realisateur=%s", (id,)
    )
    if mycursor.fetchone()["nb"] > 0:
        return False, "Impossible de supprimer ce réalisateur : il est utilisé par un film."
    mycursor.execute("DELETE FROM REALISATEUR WHERE id=%s", (id,))
    mydb.commit()
    return True, "Réalisateur supprimé !"


def getStudentByIdFull(id):
    mycursor.execute("SELECT * FROM ETUDIANT WHERE id=%s", (id,))
    return mycursor.fetchone()


def getFilmByIdWithLinks(id):
    mycursor.execute("SELECT * FROM FILM WHERE id=%s", (id,))
    film = mycursor.fetchone()
    if film:
        # Récupérer les genres associés
        mycursor.execute("SELECT id_genre FROM APPARTENANCE WHERE id_film=%s", (id,))
        film["genres_ids"] = [row["id_genre"] for row in mycursor.fetchall()]
        # Récupérer les réalisateurs associés
        mycursor.execute("SELECT id_realisateur FROM DIRECTION WHERE id_film=%s", (id,))
        film["directors_ids"] = [row["id_realisateur"] for row in mycursor.fetchall()]
    return film


def getGenreById(id):
    mycursor.execute("SELECT * FROM GENRE WHERE id=%s", (id,))
    return mycursor.fetchone()


def getDirectorById(id):
    mycursor.execute("SELECT * FROM REALISATEUR WHERE id=%s", (id,))
    return mycursor.fetchone()


def getAllFilms():
    mycursor.execute("SELECT id, nom, annee FROM FILM ORDER BY nom")
    return mycursor.fetchall()


def getAllGenres():
    mycursor.execute("SELECT id, nom FROM GENRE ORDER BY nom")
    return mycursor.fetchall()


def getAllDirectors():
    mycursor.execute("SELECT id, nom FROM REALISATEUR ORDER BY SUBSTRING_INDEX(nom, ' ', -1), nom")
    return mycursor.fetchall()


def getAllStudentsShort():
    mycursor.execute("SELECT id, prenom, nom FROM ETUDIANT ORDER BY nom, prenom")
    return mycursor.fetchall()


def getStudentsPaginated(offset=0, limit=10):
    mycursor.execute(
        """
        SELECT e.id, e.prenom, e.nom, u.username AS username, f.nom AS film_nom, g.nom AS genre_nom
        FROM ETUDIANT e
        JOIN FILM f ON e.id_film = f.id
        JOIN GENRE g ON e.id_genre = g.id
        LEFT JOIN UTILISATEUR u ON e.id = u.id_etudiant
        ORDER BY e.id
        LIMIT %s OFFSET %s
    """,
        (limit, offset),
    )
    return mycursor.fetchall()


def countStudents():
    mycursor.execute("SELECT COUNT(*) AS total FROM ETUDIANT")
    return mycursor.fetchone()["total"]
