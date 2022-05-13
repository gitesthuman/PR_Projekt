import random
import socketserver

from foo import *
from Asteroid import Asteroid

asteroid = []
limit = 64*10
counter = 0
over = False
scores = dict()
coords = dict()
playersReady = 0
gameStarted = False


def serve():
    global counter
    global over
    global gameStarted

    if not gameStarted:
        return

    if counter % 64 == 63:
        print(len(asteroid))
    if counter < limit:
        counter += 1
    if counter == limit and not over:
        print("Game Over")
        over = True

    for ast in asteroid:
        ast.move()

    i = 0
    while i < len(asteroid):
        if asteroid[i].out():
            del asteroid[i]
            i -= 1
        i += 1

    if random.randint(0, 200) == 0:
        asteroid.append(Asteroid())


class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]

        if not scores.__contains__(self.client_address[1]):
            scores[self.client_address[1]] = 0

        msg = data.decode("utf-8")

        # lobby
        global playersReady
        global gameStarted
        if msg == "l":
            if playersReady >= 2:
                socket.sendto(bytes("s", "utf-8"), self.client_address)
                gameStarted = True
            else:
                socket.sendto(bytes("l", "utf-8"), self.client_address)
        elif msg == "s":
            playersReady += 1
            print("Players: ", playersReady)
            if playersReady >= 2:
                socket.sendto(bytes("s", "utf-8"), self.client_address)
                gameStarted = True
            else:
                socket.sendto(bytes("l", "utf-8"), self.client_address)

        else:
            if msg[0] == "c":
                parts = msg[1:].split(",")
                print("Client {}: {}".format(self.client_address[1], parts))
                coords[self.client_address[1]] = [int(parts[1]), int(parts[2])]
                i = 0
                while i < len(asteroid):
                    if asteroid[i].hitbox(coords[self.client_address[1]]):
                        del asteroid[i]
                        i -= 1
                        scores[self.client_address[1]] += 100
                    i += 1
            else:
                parts = msg.split(",")
                coords[self.client_address[1]] = [int(parts[0]), int(parts[1])]
            # if msg == "q":  # TODO
            #     print("Client {} disconnected\n".format(self.client_address[1]))

            points = [str(scores[self.client_address[1]])] \
                + [str(scores[k]) for k in scores.keys() if k != self.client_address[1]]
            pos = [[str(x) for x in coords[k]] for k in coords.keys() if k != self.client_address[1]]
            if len(pos) == 0:
                pos = [["-100", "-100"]]

            print(pos)
            print()

            msg = ",".join(points) + "." + ",".join(pos[0])
            for ast in asteroid:
                msg += "." + str(round(ast.cords()[0])) + "," + str(round(ast.cords()[1]))
            socket.sendto(bytes(msg, "utf-8"), self.client_address)


HOST, PORT = "localhost", 666

with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
    server.service_actions = serve
    server.serve_forever(poll_interval=0.015625)  # 64 times per second
