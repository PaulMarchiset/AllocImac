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
    mycursor.execute("SELECT e.nom, g.nom, f.nom FROM ETUDIANT e JOIN GENRE g ON e.id_genre = g.id JOIN FILM f ON e.id_film=f.id WHERE id = %s", (id,))
    student = mycursor.fetchone()
    return student

# import database