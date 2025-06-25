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
    mycursor.execute("SELECT * FROM ETUDIANT ORDER BY nom, prenom ASC")
    students = mycursor.fetchall()
    return students

def getStudentById(id):
    mycursor.execute("""
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
    """, (id,))
    result = mycursor.fetchone()
    if result:
        return {
            'prenom': result['etu_prenom'],
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
    ''')
    results = mycursor.fetchall()

    top_films = []
    for result in results:
        film_id = result['film_id']
        mycursor.execute("""
            SELECT r.id, r.nom
            FROM REALISATEUR r
            JOIN DIRECTION d ON r.id = d.id_realisateur
            WHERE d.id_film = %s
        """, (film_id,))
        realisateurs = [{'id': row['id'], 'nom': row['nom']} for row in mycursor.fetchall()]

        top_films.append({
            'id': film_id,
            'nom': result['nom_film'],
            'annee': result['annee_film'],
            'realisateurs': realisateurs,
            'nb_etudiants': result['nb_etudiants']
        })

    return top_films


def top5Genre():
    mycursor.execute('''
        SELECT GENRE.id AS id_genre, GENRE.nom AS nom_genre, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM GENRE
        LEFT JOIN ETUDIANT ON GENRE.id = ETUDIANT.id_genre
        GROUP BY GENRE.id, GENRE.nom
        ORDER BY nb_etudiants DESC
        LIMIT 5
    ''')
    results = mycursor.fetchall()

    top_genres = []
    for result in results:
        genre_name = result['nom_genre']

        top_genres.append({
            'id': result['id_genre'],
            'nom': genre_name,
            'nb_etudiants': result['nb_etudiants']
        })
    return top_genres

def top5Realisateur():
    mycursor.execute('''
        SELECT REALISATEUR.id AS id_real, REALISATEUR.nom AS nom_real, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM REALISATEUR
        JOIN DIRECTION ON REALISATEUR.id = DIRECTION.id_realisateur
        JOIN FILM ON DIRECTION.id_film = FILM.id
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        GROUP BY REALISATEUR.nom, REALISATEUR.id
        ORDER BY nb_etudiants DESC
        LIMIT 5
    ''')
    results = mycursor.fetchall()

    top_realisateurs = []
    for result in results:
        top_realisateurs.append({
            'id': result['id_real'],
            'nom': result['nom_real'],
            'nb_etudiants': result['nb_etudiants']
        })
    return top_realisateurs

def top5Decennies():
    mycursor.execute('''
        SELECT CONCAT(FLOOR(FILM.annee / 10) * 10, 's') AS decennie, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM FILM
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        GROUP BY decennie
        ORDER BY nb_etudiants DESC
        LIMIT 5
    ''')
    results = mycursor.fetchall()

    top_decennies = []
    for result in results:
        top_decennies.append({
            'decennie': result['decennie'],
            'nb_etudiants': result['nb_etudiants']
        })
    return top_decennies

def getStudentsPaginated(offset=0, limit=10):
    mycursor.execute("""
        SELECT e.id, e.nom, f.nom AS film_nom, g.nom AS genre_nom
        FROM ETUDIANT e
        JOIN FILM f ON e.id_film = f.id
        JOIN GENRE g ON e.id_genre = g.id
        ORDER BY e.id
        LIMIT %s OFFSET %s
    """, (limit, offset))
    return mycursor.fetchall()

def countStudents():
    mycursor.execute("SELECT COUNT(*) AS total FROM ETUDIANT")
    return mycursor.fetchone()['total']