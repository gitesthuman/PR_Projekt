import random
import socketserver
import threading
import time

from Asteroid import Asteroid

semaphore = threading.Lock()

asteroids = []
gameDuration = 15  # in seconds
limit = 64 * gameDuration
counter = 0
over = False
scores = dict()
coords = dict()
shotAsteroids = dict()
playersReady = 0
playersLeftScoreboard = 0
gameStarted = False


def spawn():
    global counter
    global over
    global gameStarted
    global shotAsteroids
    global asteroids

    while True:
        if not gameStarted:
            continue

        if counter % 64 == 63:
            print(counter // 64 + 1)
        if counter < limit:
            counter += 1
        if counter == limit and not over:
            print("Game Over")
            over = True

        # add points to players
        for astIndex in shotAsteroids:
            scores[shotAsteroids[astIndex][0]] += 100

        # delete shot asteroids
        asteroids = [asteroids[i] for i in range(len(asteroids)) if i not in shotAsteroids]
        shotAsteroids = dict()

        for ast in asteroids:
            ast.move()

        i = 0
        while i < len(asteroids):
            if asteroids[i].out():
                del asteroids[i]
                i -= 1
            i += 1

        if random.randint(0, 100) == 0 and counter >= 3 * 64:
            asteroids.append(Asteroid())

        time.sleep(0.014)
        # time.sleep(0.015625)


class ThreadedUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global scores
        global over
        global playersReady
        global playersLeftScoreboard
        global counter
        global gameStarted
        data = self.request[0].strip()
        socket = self.request[1]

        if not scores.__contains__(self.client_address[1]):
            scores[self.client_address[1]] = 0

        msg = data.decode("utf-8")

        # check if game is over
        if over and msg != "e" and msg != "p" and msg != "s" and msg != "l":
            points = [str(scores[self.client_address[1]])] \
                     + [str(scores[k]) for k in scores.keys() if k != self.client_address[1]]
            msg = "o" + ','.join(points)
            socket.sendto(bytes(msg, "utf-8"), self.client_address)
            gameStarted = False
            counter = 0
            return

        # player is in lobby
        if msg == "l":
            with semaphore:
                if playersReady >= 2 and playersLeftScoreboard != 1:
                    socket.sendto(bytes("s", "utf-8"), self.client_address)
                    gameStarted = True
                    playersLeftScoreboard = 0
                else:
                    socket.sendto(bytes("l", "utf-8"), self.client_address)
        # player wants to start a game (clicked a button)
        elif msg == "s":
            with semaphore:
                playersReady += 1
                print("Players: ", playersReady)
                if playersReady >= 2 and playersLeftScoreboard != 1:
                    socket.sendto(bytes("s", "utf-8"), self.client_address)
                    gameStarted = True
                    playersLeftScoreboard = 0
                    asteroids.clear()
                else:
                    socket.sendto(bytes("l", "utf-8"), self.client_address)
        # player clicked button play again
        elif msg == "p":
            playersReady -= 1
            playersLeftScoreboard += 1
            print("Players: " + str(playersReady))
            if playersLeftScoreboard == 2:
                over = False
                scores = dict()
            socket.sendto(bytes("p", "utf-8"), self.client_address)
        # player is in main game loop
        else:
            if msg[0] == "c":
                parts = msg[1:].split(",")
                print("Client {}: {}".format(self.client_address[1], parts))
                coords[self.client_address[1]] = [int(parts[1]), int(parts[2])]
                i = 0
                while i < len(asteroids):
                    if asteroids[i].hitbox(coords[self.client_address[1]]):
                        # Decide whether the player was first to shoot this asteroid
                        with semaphore:
                            if i not in shotAsteroids.keys() or shotAsteroids[i][1] > parts[0]:
                                shotAsteroids[i] = (self.client_address[1], parts[0])
                    i += 1
            else:
                parts = msg.split(",")
                coords[self.client_address[1]] = [int(parts[0]), int(parts[1])]

            points = [str(scores[self.client_address[1]])] \
                + [str(scores[k]) for k in scores.keys() if k != self.client_address[1]]
            pos = [[str(x) for x in coords[k]] for k in coords.keys() if k != self.client_address[1]]
            if len(pos) == 0:
                pos = [["-100", "-100"]]

            msg = ",".join(points) + "." + ",".join(pos[0])
            for ast in asteroids:
                msg += "." + str(round(ast.cords()[0])) + "," + str(round(ast.cords()[1]))
            socket.sendto(bytes(msg, "utf-8"), self.client_address)


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


HOST, PORT = "localhost", 666
t = threading.Thread(target=spawn)

with ThreadedUDPServer((HOST, PORT), ThreadedUDPHandler) as server:
    t.start()
    server.serve_forever()
