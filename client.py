import socket
import sys
import pygame

from foo import *

HOST, PORT = "localhost", 666
data = " ".join(sys.argv[1:])

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Connected to the server")
pygame.init()
pygame.display.set_caption("Shooter")
screen = pygame.display.set_mode((600, 400))
font = pygame.font.SysFont('Arial', 18)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
run = True
points = [0, 0]
timer = 0

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
while True:
    timer += 1
    screen.fill((0, 0, 0))
    mouse = pygame.mouse.get_pos()
    clock.tick(64)
    msg = ""

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            run = False
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            msg = "c" + str(timer) + ","

    sock.sendto(bytes(msg + str(mouse[0]) + "," + str(mouse[1]), "utf-8"), (HOST, PORT))
    received = str(sock.recv(1024), "utf-8")

    if not run:
        break

    parts = received.split(".")
    points = [int(i) for i in parts[0].split(",")]
    op = [int(i) for i in parts[1].split(",")]
    for pol in parts[2:]:
        cor = [int(i) for i in pol.split(",")]
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(cor[0] - 15, cor[1] - 15, 30, 30))

    # crosshair
    pygame.draw.circle(screen, (0, 255, 0), (mouse[0], mouse[1]), 15, 1)
    pygame.draw.line(screen, (0, 255, 0), (mouse[0], mouse[1] - 20), (mouse[0], mouse[1] + 20), 1)
    pygame.draw.line(screen, (0, 255, 0), (mouse[0] - 20, mouse[1]), (mouse[0] + 20, mouse[1]), 1)

    pygame.draw.circle(screen, (255, 0, 0), (op[0], op[1]), 15, 1)
    pygame.draw.line(screen, (255, 0, 0), (op[0], op[1] - 20), (op[0], op[1] + 20), 1)
    pygame.draw.line(screen, (255, 0, 0), (op[0] - 20, op[1]), (op[0] + 20, op[1]), 1)

    text = font.render(str(points[0]), True, (255, 255, 255))
    screen.blit(text, (600 - text.get_width() - 5, 400 - text.get_height() - 5))

    pygame.display.update()

# sock.sendto(bytes("q", "utf-8"), (HOST, PORT))
# received = str(sock.recv(1024), "utf-8")
sock.close()
print("Disconnected")
