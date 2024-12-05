from flask import Flask
from flask import request
from flask_cors import CORS
import hashlib
import jwt_utils
from Question import *
from Participation import *
from BuildDB import *

app = Flask(__name__)
CORS(app)

@app.route('/') 
def hello_world():
	x = 'world ! ^^ '
	return f"Hello, {x}"

@app.route('/quiz-info', methods=['GET'])
def GetQuizInfo():
    return getQuizzInfo()

@app.route('/login', methods=['POST'])
def getLogin():
    payload = request.get_json()
    tried_password = payload['password'].encode('UTF-8')
    pwHashed = hashlib.md5(tried_password).digest()
    if (pwHashed == hashlib.md5(b'flask2023').digest()):
        return {"token": jwt_utils.build_token()}, 200
    else:
        return {"token": 'Unauthorized'}, 401
    
@app.route('/rebuild-db', methods=['POST'])
def BuildDataBase():
    return buildDB()
    
################################################################
########################### Question ###########################
################################################################

@app.route('/questions', methods=['POST'])
def InputQuestion():
    #Récupérer le token envoyé en paramètre
    tokenAuth = request.headers.get('Authorization')
    try: 
        tokenAuth = tokenAuth.removeprefix("Bearer ")
        jwt_utils.decode_token(tokenAuth)
        #récupèrer un l'objet json envoyé dans le body de la requète
    except:
        return {"token": 'Unauthorized'}, 401
    
    Jsonreturn = request.get_json()
    titre = Jsonreturn['title']
    titre = titre.replace("'","''")
    texte = Jsonreturn['text']
    texte = texte.replace("'","''")
    image = Jsonreturn['image']
    position = Jsonreturn['position']
    possibleReponse = Jsonreturn['possibleAnswers']
    inputQuest = Question(titre, texte, image, position, possibleReponse)
    return fromObjectToSql(inputQuest) 

@app.route('/questions/all', methods=['DELETE'])
def DelallQuestion():
    tokenAuth = request.headers.get('Authorization')
    try: 
        tokenAuth = tokenAuth.removeprefix("Bearer ")
        jwt_utils.decode_token(tokenAuth)
    except:
        return {"token": 'Unauthorized'}, 401
    deleteAll()
    return {}, 204
    
@app.route('/questions',methods=['GET']) #/question?position=int
def getQuestionPosition():
    position = request.args.get('position')
    return searchByPosition(position)

@app.route('/questions/<questionId>',methods=['GET']) #/question/questionID
def getQuestionId(questionId):
    return searchById(questionId)

@app.route('/questions/<questionId>', methods=['PUT'])
def UpdateQuestion(questionId):
    #Récupérer le token envoyé en paramètre
    tokenAuth = request.headers.get('Authorization')
    try: 
        tokenAuth = tokenAuth.removeprefix("Bearer ")
        jwt_utils.decode_token(tokenAuth)
    #récupèrer un l'objet json envoyé dans le body de la requète
    except:
        return {"token": 'Unauthorized'}, 401
    Jsonreturn = request.get_json()
    titre = Jsonreturn['title']
    titre = titre.replace("'","''")
    texte = Jsonreturn['text']
    texte = texte.replace("'","''")
    image = Jsonreturn['image']
    position = Jsonreturn['position']
    possibleReponse = Jsonreturn['possibleAnswers']
    inputQuest = Question(titre, texte, image, position, possibleReponse)
    token=UpdateSQL(inputQuest,questionId)
    
    return {},token

@app.route('/questions/<questionId>',methods=['DELETE'])
def DelQuestion(questionId):
    tokenAuth=request.headers.get('Authorization')
    try:
        tokenAuth = tokenAuth.removeprefix("Bearer ")
        jwt_utils.decode_token(tokenAuth)
        return {},deleteQuestion(questionId)
    except:
        return 'Unauthorized', 401
        
        
######################################################################
########################### Participations ###########################
######################################################################
@app.route('/participations/all', methods=['DELETE'])
def DelallParticipations():
    tokenAuth = request.headers.get('Authorization')
    try: 
        tokenAuth = tokenAuth.removeprefix("Bearer ")
        jwt_utils.decode_token(tokenAuth)
        
    except:
        return {"token": 'Unauthorized'}, 401
    if(deleteParticipationsAll()):
        return {}, 204
    else:
        return {"Unable to delete"}, 500

@app.route('/participations', methods=['POST'])
def InputParticipation():
    Jsonreturn = request.get_json()
    PlayerName = Jsonreturn['playerName']
    Answer = Jsonreturn['answers']
    score=calculeScore(Answer)
    if(score=="overcomplet"):
       return {"message": "overcomplet"}, 400
    elif(score=="incomplet"):
        return {"message": "incomplet"}, 400
    inputParticipant = Participation(PlayerName,pScore=score,pAnswer=Answer,)
    return addBDDParticipation(inputParticipant)
    
    
if __name__ == "__main__":
    app.run()