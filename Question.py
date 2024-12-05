import json
import sqlite3

class Question():
    IDQuestion = ""
    title = ""
    text = ""
    image = ""
    position = 1
    reponsePossible = [{}]
    
    def __init__(self, title: str, text:str, image:str, position:int, reponsePossible):
        self.title = title
        self.text = text
        self.image = image
        self.position = position
        self.reponsePossible = reponsePossible
    
    def fromJsonToPython(Json):
        title = Json['title']
        text = Json['text']
        image = Json['image']
        position = Json['position']
        reponsePossible = Json['possibleAnswers']
        return Question(title=title, text=text, image=image, position= position, reponsePossible= reponsePossible)
    
    
    def fromPythonToJson(IDQuestion, title: str, text:str, image:str, position:int, reponsePossible):
        question = {
            'id' : IDQuestion,
            'title': title,
            'text': text,
            'image': image,
            'position': position,
            'possibleAnswers': reponsePossible
        }
        data = json.dumps(question, indent=2)
        return data
    
def fromObjectToSql(question:Question):
    db_connection = sqlite3.connect('databaseQuiz.db')
    db_connection.isolation_level = None
    cur = db_connection.cursor()
    cur.execute("begin")
    textString = json.dumps(question.reponsePossible)
    textString = textString.replace("'","''")
    cur.execute(f"select Position from questions where Position={question.position}")
    row=cur.fetchall()
    if(len(row)!=0):
        db_connection.close()
        moveDown(question.position)
        db_connection = sqlite3.connect('databaseQuiz.db')
        db_connection.isolation_level = None
        cur = db_connection.cursor()
        cur.execute("begin")
    try: 
        cur.execute(f"insert into questions(Text, Titre, Position, Image, possibleAnswer) values ('{question.text}','{question.title}','{question.position}','{question.image}','{textString}')")    
        id = cur.execute(f"SELECT IDQuestion from questions where Position={question.position}")
        row = cur.fetchall()
        id = row[0][0]
        # send the request
        cur.execute("commit")
        db_connection.close()
        return {"id": id},200
    except:
        #in case of exception, rollback the transaction
       cur.execute('rollback')
       return {},500

def fromSqlToObject(SQlRow):    
    return Question(SQlRow[0][2], SQlRow[0][1], SQlRow[0][4], SQlRow[0][3], SQlRow[0][5]),SQlRow[0][0]

def deleteAll():
    db_connection=sqlite3.connect("databaseQuiz.db")
    db_connection.isolation_level = None
    db_connection.execute("begin")
    cur=db_connection.cursor()
    try:
        cur.execute(f"delete from questions") 
        cur.execute("commit")
        return True 
    except:
        cur.execute('rollback')
        return False
    
def searchByPosition(position:int):
    db_connection=sqlite3.connect("databaseQuiz.db")
    db_connection.isolation_level = None
    db_connection.execute("begin")
    cursor=db_connection.cursor()
    cursor.execute(f"select * from questions where Position ={position}")
    row=cursor.fetchall()
    db_connection.close()
    if len(row ) == 0:
        return "Request respond Not Found",404
    else:
        question = fromSqlToObject(row)
        data = Question.fromPythonToJson(question[1],question[0].title, question[0].text, question[0].image, question[0].position, json.loads(question[0].reponsePossible))
        return data,200

def searchById(id:int):
    db_connection=sqlite3.connect("databaseQuiz.db")
    db_connection.isolation_level = None
    db_connection.execute("begin")
    cursor=db_connection.cursor()
    cursor.execute(f"select * from questions where IDQuestion ={id}")
    row=cursor.fetchall()
    db_connection.close()
    if len(row) == 0:
        return "Request respond Not Found",404
    else:
        question = fromSqlToObject(row)
        data = Question.fromPythonToJson(question[1], question[0].title, question[0].text, question[0].image, question[0].position, json.loads(question[0].reponsePossible))
        return data,200

    
def UpdateSQL(question:Question , id:int):
    db_connection = sqlite3.connect('databaseQuiz.db')
    db_connection.isolation_level = None
    textString = json.dumps(question.reponsePossible)
    textString = textString.replace("'","''")
    cur = db_connection.cursor()
    cur.execute("begin")
    cur.execute(f"select Position from questions where IDQUestion={id}")
    row=cur.fetchall()
    if(row==[]):
        return 404
    position=row[0][0]
    
    if(position!=question.position):
        db_connection.close()
        changePostion(position,question.position)
        db_connection = sqlite3.connect('databaseQuiz.db')
        cur = db_connection.cursor()
        cur.execute("begin")

    try: 
        
        cur.execute(f"Update  questions Set (Text, Titre, Image,possibleAnswer)=('{question.text}','{question.title}','{question.image}','{textString}') where IDQuestion={id}")

        # send the request
        cur.execute("commit")
        db_connection.close()
        return 204
    except:
        #in case of exception, rollback the transaction
       cur.execute('rollback')
       return {},500
   
def deleteQuestion(id:int):
    db_connection=sqlite3.connect("databaseQuiz.db")
    db_connection.isolation_level = None
    db_connection.execute("begin")
    cursor=db_connection.cursor()
    cursor.execute(f"select Position from questions where IDQUestion={id}")
    row=cursor.fetchall()
    if(row==[]):
        return 404
    try:
        cursor.execute(f"DELETE from questions where IDQuestion={id}")
    except:
        cursor.execute("rollback")
    cursor.execute("commit")
    db_connection.close()
    moveUp(row[0][0])
    return 204

def changePostion(start:int,end:int):
    db_connection = sqlite3.connect('databaseQuiz.db')
    db_connection.isolation_level = None
    cur = db_connection.cursor()
    cur.execute("begin")
    cur.execute(f"select IDQuestion from questions where Position={start}")
    row=cur.fetchall()
    if(row==[]):
        return 404   
    try: 
        cur.execute(f"Update  questions Set ( Position)=('{0}') where Position={start}")
    except:
        cur.execute('rollback')
    nb=start-end
    if(nb<0):
        for i in range (1,abs(nb)+1):
            cur.execute(f"select IDQuestion from questions where Position={start+i}")
            row=cur.fetchall()
            if(row!=[]):
                cur.execute(f"Update questions set Position =Position-1 where Position={start+i}")
       
        cur.execute(f"Update questions set Position ={end} where Position={0}")
        
    elif(nb==0):
        cur.execute(f"Update questions set Position ={end} where Position={0}")
    else:
        for i in range (1,abs(nb)+1):
            cur.execute(f"select IDQuestion from questions where Position={start-i}")
            row=cur.fetchall()
            if(row!=[]):
                cur.execute(f"Update questions set Position =Position+1 where Position={start-i}")
        cur.execute(f"Update questions set Position ={end} where Position={0}")
    cur.execute("commit")  
    db_connection.close()
    
def calculeScore(tab):
    score=0
    db_connection = sqlite3.connect('databaseQuiz.db')
    db_connection.isolation_level = None
    cur = db_connection.cursor()
    cur.execute("begin")
    cur.execute(f"SELECT count(Position) from questions")
    row=cur.fetchall()
    if(len(tab)<row[0][0]):
        return "incomplet"
    elif(len(tab)>row[0][0]):
        return "overcomplet"
    for i in range (len(tab)):
        cur.execute(f"select possibleAnswer from questions where Position={i+1}")
        Answers=cur.fetchall()[0][0]
        print(Answers)
        data=json.loads(Answers)
        print(data)
        k=1
        for Answers in data:
            if(Answers["isCorrect"]):
                if(tab[i]==k):
                    score+=1
                break
            k+=1
    db_connection.close()
    return score
def moveDown(position):
    db_connection = sqlite3.connect('databaseQuiz.db')
    db_connection.isolation_level = None
    cur = db_connection.cursor()
    cur.execute("begin")
    cur.execute(f"select Position from questions order by position desc")
    row=cur.fetchall()
    last=row[0][0]
    for i in range (0,(last-position)+1):
        cur.execute(f"select IDQuestion from questions where Position={last-i}")
        row=cur.fetchall()
        if(row!=[]):
            cur.execute(f"Update questions set Position =Position+1 where Position={last-i}")
    cur.execute("commit")
    db_connection.close()
def moveUp(position):
    db_connection = sqlite3.connect('databaseQuiz.db')
    db_connection.isolation_level = None
    cur = db_connection.cursor()
    cur.execute("begin")
    cur.execute(f"select Position from questions order by position desc")
    row=cur.fetchall()
    if(len(row)!=0):
        last=row[0][0]
        for i in range (position,last+1):
            cur.execute(f"select IDQuestion from questions where Position={i}")
            row=cur.fetchall()
            if(row!=[]):
                cur.execute(f"Update questions set Position =Position-1 where Position={i}")
        cur.execute("commit")
    db_connection.close()

