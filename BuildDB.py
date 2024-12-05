import sqlite3

def buildDB():
    db_connection = sqlite3.connect('databaseQuiz.db')
    db_connection.isolation_level = None
    cur = db_connection.cursor()
    cur.execute("begin")
    cur.execute(f"CREATE TABLE 'Participant' ('IDParticipant' INTEGER NOT NULL UNIQUE, 'PlayerName' TEXT, 'Score' INTEGER, 'Answer' TEXT, PRIMARY KEY('IDParticipant' AUTOINCREMENT));")
    cur.execute(f"CREATE TABLE 'questions' ('IDQuestion' INTEGER NOT NULL UNIQUE, 'Text' TEXT, 'Titre' TEXT NOT NULL, 'Position' INTEGER NOT NULL UNIQUE, 'Image' TEXT, 'possibleAnswer' TEXT,	PRIMARY KEY('IDQuestion' AUTOINCREMENT));")
    cur.execute("commit")
    db_connection.close()
    return "Ok",200
    

    