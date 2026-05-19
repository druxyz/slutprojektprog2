import random
import time
import math


class Game:
    def __init__(self, socketio, room):
        self.socketio = socketio
        self.room = room
        self.PlayerMap = {}
        self.FoodMap = []
        self.MapSize = 3000
        self.FoodColors = ["ff0000", "ff9900", "0000ff"]
        self.MaxFood = 1000

    def add_player(self, sid):
        spawn_x = random.randint(50, self.MapSize - 50)
        spawn_y = random.randint(50, self.MapSize - 50)

        self.PlayerMap[sid] = {
            "x": spawn_x,
            "y": spawn_y,
            "mass": 20,
            "radius": 20,
            "color": "lime",
            "mouseX": 0,
            "mouseY": 0
        }

    def remove_player(self, sid):
        if sid in self.PlayerMap:
            del self.PlayerMap[sid]

    def set_mouse_pos(self, sid, mouse_x, mouse_y):
        if sid in self.PlayerMap:
            self.PlayerMap[sid]["mouseX"] = mouse_x
            self.PlayerMap[sid]["mouseY"] = mouse_y

    def spawnFood(self):
        spawnPosX = random.randint(0, self.MapSize)
        spawnPosY = random.randint(0, self.MapSize)

        FoodColorInt = random.randint(0, len(self.FoodColors) - 1)
        FoodColor = self.FoodColors[FoodColorInt]
        self.FoodMap.append({
            "x": spawnPosX,
            "y": spawnPosY,
            "color": FoodColor,
            "radius": 8
        })

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def update_radius(self, player):
        player["radius"] = math.sqrt(player["mass"]) * 4.5

    def update_movement(self):
        for sid in self.PlayerMap:

            player = self.PlayerMap[sid]

            speed = 5

            if player["mouseX"] > player["x"]:
                player["x"] += speed

            if player["mouseX"] < player["x"]:
                player["x"] -= speed

            if player["mouseY"] > player["y"]:
                player["y"] += speed

            if player["mouseY"] < player["y"]:
                player["y"] -= speed

            # håll spelare i mappen
            if player["x"] < player["radius"]:
                player["x"] = player["radius"]

            if player["x"] > self.MapSize - player["radius"]:
                player["x"] = self.MapSize - player["radius"]

            if player["y"] < player["radius"]:
                player["y"] = player["radius"]

            if player["y"] > self.MapSize - player["radius"]:
                player["y"] = self.MapSize - player["radius"]

    def handle_food_eating(self):
        for sid in self.PlayerMap:

            player = self.PlayerMap[sid]

            eaten_food = []

            for food in self.FoodMap:

                dist = self.distance(
                    player["x"],
                    player["y"],
                    food["x"],
                    food["y"]
                )

                if dist < player["radius"]:
                    player["mass"] += 1
                    eaten_food.append(food)

            for food in eaten_food:
                if food in self.FoodMap:
                    self.FoodMap.remove(food)

            self.update_radius(player)

    def handle_player_eating(self):
        eaten_players = []

        player_items = list(self.PlayerMap.items())

        for sid1, player1 in player_items:
            for sid2, player2 in player_items:
                if sid1 == sid2:
                    continue

                if sid1 in eaten_players or sid2 in eaten_players:
                    continue

                if player1["mass"] > player2["mass"] * 1.15:
                    dist = self.distance(player1["x"], player1["y"], player2["x"], player2["y"])

                    if dist < player1["radius"]:
                        player1["mass"] += player2["mass"]
                        self.update_radius(player1)
                        eaten_players.append(sid2)

        for sid in eaten_players:
            self.remove_player(sid)

    def emit_game_state(self):
        self.socketio.emit(
            "game_state",
            {
                "players": self.PlayerMap,
                "food": self.FoodMap,
                "mapSize": self.MapSize
            },
            to=self.room
        )

    def game_loop(self):
        while True:
            self.update_movement()
            self.handle_food_eating()
            self.handle_player_eating()

            while len(self.FoodMap) < self.MaxFood:
                self.spawnFood()

            self.emit_game_state()

            self.socketio.sleep(1 / 60)