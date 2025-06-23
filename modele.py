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
