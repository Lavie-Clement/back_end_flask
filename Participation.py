import json
import sqlite3

class Participation():
    PlayerName = ""
    Score = 0
    Answer = {}
    
    def __init__(self,pPlayerName:str, pScore=0, pAnswer={}):
        self.PlayerName = pPlayerName
        self.Score = pScore
        self.Answer = pAnswer
	
    def fromPythonToJSON(pPlayerName:str, pScore:int, pAnswer):
        participant = {
            'PlayerName' : pPlayerName,
            'Score' : pScore,
            'Answer' : pAnswer
        }
        data = json.dumps(participant, indent=2)
        return data
            
    def fromJSONTOPython(JSON):
        PlayerName = JSON['PlayerName']
        Score = JSON['Score']
        Answer = JSON['Answer']
        return Participation(PlayerName, Score, Answer)

def addBDDParticipation(Participant:Participation):
    db_connection = sqlite3.connect('databaseQuiz.db')
    db_connection.isolation_level = None
    cur = db_connection.cursor()
    cur.execute("begin")
    try: 
        cur.execute(f"insert into participant(PlayerName, Score, Answer) values ('{Participant.PlayerName}','{Participant.Score}','{Participant.Answer}')")
        # print(f"SELECT PlayerName, Score from participant where PlayerName = {Participant.PlayerName} AND Score = {Participant.Score} AND Answer = {Participant.Answer}")
        cur.execute(f"SELECT PlayerName, Score from participant where PlayerName = '{Participant.PlayerName}' AND Score = '{Participant.Score}' AND Answer = '{Participant.Answer}'")
        row = cur.fetchall()
        # send the request
        cur.execute("commit")
        db_connection.close()
        data = {
            "playerName" : row[0][0],
            "score" : row[0][1]
        }
        JSONreturn = json.dumps(data)
        return JSONreturn,200
    except:
        #in case of exception, rollback the transaction
       cur.execute('rollback')
       return {},500

def deleteParticipationsAll():
    db_connection=sqlite3.connect("databaseQuiz.db")
    db_connection.isolation_level = None
    db_connection.execute("begin")
    cur=db_connection.cursor()
    try:
        cur.execute(f"delete from Participant")
        cur.execute("commit")
        return True
    except:
        cur.execute('rollback')
        return False
    
def getQuizzInfo():
    db_connection=sqlite3.connect("databaseQuiz.db")
    db_connection.isolation_level = None
    db_connection.execute("begin")
    cur=db_connection.cursor()
    try:
        cur.execute(f"SELECT PlayerName, Score from Participant ORDER BY Score DESC")
        row = cur.fetchall()
        cur.execute("commit")
    except:
        cur.execute('rollback')
        return {"database empty"}, 404
    cur.execute(f"SELECT count(Position) FROM questions")
    nbQuestion=cur.fetchall()[0][0]
    data='{"size":'+ str(nbQuestion)+','
    scores='"scores":['
    if len(row) == 0:
        data=data+scores+"]}"
        JSONReturn = json.loads(data)
        return JSONReturn,200
   
    for lign in row:
        scores = scores + '{"playerName":' +'"'+ str(lign[0])+'"'+',"score":'+str(lign[1])+'},'
    data=data+scores.rstrip(',')+"]}"

    JSONReturn = json.loads(data)
    return JSONReturn,200
