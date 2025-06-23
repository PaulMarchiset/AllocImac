import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='admin',
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
            g.nom AS genre_nom 
        FROM ETUDIANT e 
        JOIN FILM f ON e.id_film = f.id 
        JOIN GENRE g ON e.id_genre = g.id 
        WHERE e.id = %s
    """, (id,))
    result = mycursor.fetchone()
    if result:
        return {
            'nom': result['etu_nom'],
            'film': {'nom': result['film_nom']},
            'genre': {'nom': result['genre_nom']}
        }
    return None


import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='admin',
    database='AllocImac'
)

mycursor = mydb.cursor(dictionary=True)

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