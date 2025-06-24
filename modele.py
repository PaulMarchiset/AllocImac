#-----------------------------------------------------------------------------------------
#----------------------------------- SETUP MYSQL -----------------------------------------
#-----------------------------------------------------------------------------------------


import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='admin',
    database='allocimac'
)

mycursor = mydb.cursor(dictionary=True)


#-----------------------------------------------------------------------------------------
#-------------------------------------- STUDENTS -----------------------------------------
#-----------------------------------------------------------------------------------------

def getAllStudents():
    mycursor.execute("SELECT * FROM ETUDIANT")
    students = mycursor.fetchall()
    return students

def getStudentById(id):
    mycursor.execute("""
        SELECT 
            e.nom AS etu_nom, 
            f.nom AS film_nom,
            f.id AS film_id, 
            g.nom AS genre_nom,
            g.id AS genre_id
        FROM ETUDIANT e 
        JOIN FILM f ON e.id_film = f.id 
        JOIN GENRE g ON e.id_genre = g.id 
        WHERE e.id = %s
    """, (id,))
    result = mycursor.fetchone()
    if result:
        return {
            'nom': result['etu_nom'],
            'film': {'nom': result['film_nom'],
                     'id': result['film_id']},
            'genre': {'nom': result['genre_nom'],
                      'id': result['genre_id']}
        }
    return None

#-----------------------------------------------------------------------------------------
#------------------------------------- GET FILM ------------------------------------------
#-----------------------------------------------------------------------------------------

def oneFilm(id):
    # Main film info
    mycursor.execute("""
        SELECT 
            f.nom AS film_nom, 
            f.annee AS film_annee,
            COUNT(DISTINCT e.id) AS nb_etudiants
        FROM FILM f
        LEFT JOIN ETUDIANT e ON f.id = e.id_film
        WHERE f.id = %s
        GROUP BY f.nom, f.annee
    """, (id,))
    film_info = mycursor.fetchone()

    # List of directors
    mycursor.execute("""
        SELECT r.id, r.nom
        FROM REALISATEUR r
        JOIN DIRECTION d ON r.id = d.id_realisateur
        WHERE d.id_film = %s
    """, (id,))
    realisateurs = [{'id': row['id'], 'nom': row['nom']} for row in mycursor.fetchall()]

    mycursor.execute("""
        SELECT g.id, g.nom
        FROM genre g
        JOIN APPARTENANCE a ON g.id = a.id_genre
        WHERE a.id_film = %s
    """, (id,))
    genres = [{'id': row['id'], 'nom': row['nom']} for row in mycursor.fetchall()]

    if film_info:
        return {
            'nom': film_info['film_nom'],
            'annee': film_info['film_annee'],
            'realisateurs': realisateurs,
            'genres': genres,
            'nb_etudiants': film_info['nb_etudiants']
        }
    return None


#-----------------------------------------------------------------------------------------
#----------------------------------- GET DIRECTOR ----------------------------------------
#-----------------------------------------------------------------------------------------

def oneDirector(id):
    mycursor.execute("""
        SELECT
            r.nom AS realisateur_nom,
            COUNT(DISTINCT d.id_film) AS nb_films,
            COUNT(DISTINCT a.id_genre) AS nb_genres
        FROM REALISATEUR r
        JOIN DIRECTION d ON r.id = d.id_realisateur
        JOIN APPARTENANCE a ON d.id_film = a.id_film
        WHERE r.id = %s
        GROUP BY r.nom
    """, (id,))
    director_info = mycursor.fetchone()
    if director_info:
        return {
            'nom': director_info['realisateur_nom'],
            'nb_films': director_info['nb_films'],
            'nb_genres': director_info['nb_genres']
        }
    return None

#-----------------------------------------------------------------------------------------
#------------------------------------- GET GENRES ----------------------------------------
#-----------------------------------------------------------------------------------------

def allGenres():
    mycursor.execute("""
        SELECT 
            g.id AS genre_id,
            g.nom AS nom_genre, 
            f.id AS film_id, 
            f.nom AS nom_film
        FROM GENRE g 
        LEFT JOIN APPARTENANCE a ON g.id = a.id_genre 
        LEFT JOIN FILM f ON a.id_film = f.id
        ORDER BY g.nom
    """)
    rows = mycursor.fetchall()

    genres_dict = {}
    for row in rows:
        genre_id = row['genre_id']
        if genre_id not in genres_dict:
            genres_dict[genre_id] = {
                'id': genre_id,
                'nom': row['nom_genre'],
                'nom_films': []
            }
        genres_dict[genre_id]['nom_films'].append({
            'id': row['film_id'],
            'nom': row['nom_film']
        })

    return list(genres_dict.values())


#-----------------------------------------------------------------------------------------
#---------------------------------------- TOP 5 ------------------------------------------
#-----------------------------------------------------------------------------------------

def top5Film():
    mycursor.execute('''
        SELECT FILM.nom AS nom_film, FILM.annee AS annee_film, REALISATEUR.nom AS realisateur, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM FILM
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        JOIN DIRECTION ON FILM.id = DIRECTION.id_film
        JOIN REALISATEUR ON DIRECTION.id_realisateur = REALISATEUR.id
        GROUP BY FILM.nom, FILM.annee, REALISATEUR.nom
        ORDER BY nb_etudiants DESC
        LIMIT 5
    ''')
    result = mycursor.fetchone()
    if result:
        return {
            'nom': result['nom_film'],
            'annee': result['annee_film'],
            'realisateur': result['realisateur'],
            'nb_etudiants': result['nb_etudiants']
        }
    return None

def top5Genre():
    mycursor.execute('''
        SELECT GENRE.nom, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM GENRE
        JOIN ETUDIANT ON GENRE.id = ETUDIANT.id_genre
        GROUP BY GENRE.nom
        ORDER BY nb_etudiants DESC
        LIMIT 5
    ''')
    return mycursor.fetchall()

def top5Realisateur():
    mycursor.execute('''
        SELECT REALISATEUR.nom, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM REALISATEUR
        JOIN DIRECTION ON REALISATEUR.id = DIRECTION.id_realisateur
        JOIN FILM ON DIRECTION.id_film = FILM.id
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        GROUP BY REALISATEUR.nom
        ORDER BY nb_etudiants DESC
        LIMIT 5
    ''')
    return mycursor.fetchall()

def top5Decennies():
    mycursor.execute('''
        SELECT CONCAT(FLOOR(FILM.annee / 10) * 10, 's') AS decennie, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM FILM
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        GROUP BY decennie
        ORDER BY nb_etudiants DESC
        LIMIT 5
    ''')
    return mycursor.fetchall()