import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='allocimac'
)

mycursor = mydb.cursor(dictionary=True)

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

def oneFilm(id):
    mycursor.execute("""
        SELECT 
            f.nom AS film_nom, 
            f.annee AS film_annee, 
            GROUP_CONCAT(DISTINCT r.nom SEPARATOR ', ') AS realisateurs,
            GROUP_CONCAT(DISTINCT g.nom SEPARATOR ', ') AS genres,
            COUNT(e.id) AS nb_etudiants
        FROM FILM f 
        JOIN DIRECTION d ON f.id = d.id_film 
        JOIN REALISATEUR r ON d.id_realisateur = r.id 
        JOIN APPARTENANCE a ON f.id = a.id_film
        JOIN GENRE g ON a.id_genre = g.id
        LEFT JOIN ETUDIANT e ON f.id = e.id_film
        WHERE f.id = %s
        GROUP BY f.nom, f.annee
    """, (id,))
    result = mycursor.fetchone()
    if result:
        return {
            'nom': result['film_nom'],
            'annee': result['film_annee'],
            'realisateurs': [name.strip() for name in result['realisateurs'].split(',')],
            'genre': {'nom': result['genres']},
            'nb_etudiants': result['nb_etudiants']
        }
    return None

def top5Film():
    mycursor.execute('''
        SELECT FILM.nom, FILM.annee, REALISATEUR.nom AS realisateur, COUNT(ETUDIANT.id) AS nb_etudiants
        FROM FILM
        JOIN ETUDIANT ON FILM.id = ETUDIANT.id_film
        JOIN DIRECTION ON FILM.id = DIRECTION.id_film
        JOIN REALISATEUR ON DIRECTION.id_realisateur = REALISATEUR.id
        GROUP BY FILM.nom, FILM.annee, REALISATEUR.nom
        ORDER BY nb_etudiants DESC
        LIMIT 5
    ''')
    return mycursor.fetchall()

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