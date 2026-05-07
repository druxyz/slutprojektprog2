from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import time


app = Flask(__name__)
socketio = SocketIO(app)


class Game:
    def __init__(self, socketio, room):
        self.socketio = socketio
        self.room = room
        self.PlayerMap = {}
        self.FoodMap = []
        self.MapSize = 3000
        self.FoodColors = ["ff0000", "ff9900", "0000ff"]
        self.Active = False


    def add_player(self, sid):
        print("ADDING PLAYER", sid)
        spawn_x = random.randint(50, self.MapSize - 50)
        spawn_y = random.randint(50, self.MapSize - 50)

        self.PlayerMap[sid] = {
        "x": spawn_x,
        "y": spawn_y,
        "mass": 20,
        "radius": 20,
        "color": "lime"
    }

    def remove_player(self, sid):
        if sid in self.PlayerMap:
            del self.PlayerMap[sid]

    def get_player_positions(self):
        return self.PlayerMap

  

    def spawnFood(self):
        spawnPosX = random.randint(0,self.MapSize)
        spawnPosY = random.randint(0,self.MapSize)

        selectedColor = random.randint(0, len(self.FoodColors))
        FoodColor = self.FoodColors[selectedColor]
        self.FoodMap.append([[spawnPosX, spawnPosY], FoodColor])


    def render_food(self):
        self.socketio.emit(
            "render_food",
            {
                "foodPositions": self.FoodMap
            },
            to=self.room
        )

    def render_players(self):
        print("rendering players")
        self.socketio.emit(
            "render_players",
            {
                "playerPositions": self.PlayerMap
            },
            to=self.room
        )

    def game_loop(self):
        while True:
            self.render_players()
            time.sleep(1/60)
            
            if len(self.FoodMap) < 1000:
                self.spawnFood()
                




    

