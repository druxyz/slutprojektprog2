from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from game import *
import uuid


GameMaxPlayers = 8
CurrentGames = []
queue = []
app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/game/<game_id>")
def game(game_id):
    return render_template("game.html", game_id=game_id)


@socketio.on("queue")
def handle_queue(data):
    sid = request.sid
#Måste komma ihåg att ta bort sid från queuen när spelaren disconnectas annars kan spelaren tekniskt sätt öppna 10 fönster och vara på nytt sid varje gång
    if sid in queue:
        return
    else:
        queue.append(sid)

    if CurrentGames:
        for i in range(len(CurrentGames)):
            if CurrentGames[i][2] < GameMaxPlayers:  #[0][1] = currentgames.players
                player = queue.pop(0)
                CurrentGames[i][2] += 1
                emit("start_game", {"game_id": CurrentGames[i][0]}, to=player)
    
        


    if len(queue) >= 2:
        p1 = queue.pop(0)
        p2 = queue.pop(0)
        game_id = str(uuid.uuid4())
        room_id = f"game{uuid.uuid4().hex}"


        # Använder room för att emitta data till alla samtidigt, alla klienter får samma data, men klienten vet sin egen id och använder sin spelares position för att välja vad 
        #som ska renderas

        game = Game(socketio, room_id)
        CurrentGames.append([game_id, game, 2]) # 2 currentplayers

        


        emit("start_game", {"game_id": game_id}, to=p1)
        emit("start_game", {"game_id": game_id}, to=p2)

        time.sleep(0.5)
        socketio.start_background_task(game.game_loop)


@socketio.on("leave")
def disconnectFromGame(data):
    game_id = data["game_id"]
    for i in range(len(CurrentGames)):
        if CurrentGames[i][0] == game_id:
            CurrentGames[i][2] -= 1

            print(f"Player has left {CurrentGames[i][1]} lobby now has {CurrentGames[i][2]} players left")

@socketio.on("add_player")
def add_player(data):
    game_id = data["game_id"]
    for i in range(len(CurrentGames)):
        if CurrentGames[i][0] == game_id:
            CurrentGames[i][1].add_player(request.sid)
            join_room(CurrentGames[i][1].room, request.sid)




if __name__ == "__main__":
    socketio.run(app, debug=False, use_reloader=False)