import socket
import pygame


HOST, PORT = "localhost", 666

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Connected to the server")
pygame.init()
pygame.display.set_caption("Shooter")
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont('Arial black', 18)
clock = pygame.time.Clock()
points = [0, 0]
timer = 0
isDraw = False
win = False
crosshair_img = pygame.image.load("assets/crosshair.png")
crosshair2_img = pygame.image.load("assets/crosshair2.png")
asteroid_img = pygame.image.load("assets/asteroid.png")
space_img = pygame.transform.scale(pygame.image.load("assets/space.png"), (640, 480))
game_state = "lobby"


# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().

clicked = False
point_font = pygame.font.SysFont('Arial black', 24)
finalFont = pygame.font.SysFont('Arial', 25)

# game loop
while True:
    # lobby
    if game_state == "lobby":
        pygame.mouse.set_visible(True)
        screen.fill((0, 0, 0))
        mouse = pygame.mouse.get_pos()
        msg = "l"
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not clicked:
                if SCREEN_WIDTH / 2 - 70 <= mouse[0] <= SCREEN_WIDTH / 2 + 70 and SCREEN_HEIGHT / 2 - 20 <= mouse[1] <= SCREEN_HEIGHT / 2 + 20:
                    msg = "s"
                    clicked = True
                    buttonText = font.render('WAITING...', True, (255, 255, 255))

        sock.sendto(bytes(msg, "utf-8"), (HOST, PORT))
        received = str(sock.recv(1024), "utf-8")
        if received == "s":
            game_state = "play"
            clicked = False

        if clicked:
            pygame.draw.rect(screen, (3, 161, 11), (SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT / 2 - 20, 140, 40))
        else:
            buttonText = font.render('START', True, (255, 255, 255))
            if SCREEN_WIDTH / 2 - 70 <= mouse[0] <= SCREEN_WIDTH / 2 + 70 and SCREEN_HEIGHT / 2 - 20 <= mouse[1] <= SCREEN_HEIGHT / 2 + 20:
                pygame.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT / 2 - 20, 140, 40))
            else:
                pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT / 2 - 20, 140, 40))

        screen.blit(buttonText, (SCREEN_WIDTH / 2 - buttonText.get_width() / 2, SCREEN_HEIGHT / 2 - buttonText.get_height() / 2))

        # updates the frames of the game
        pygame.display.update()
    # actual game
    elif game_state == "play":
        pygame.mouse.set_visible(False)
        timer += 1
        screen.blit(space_img, (0, 0))
        mouse = pygame.mouse.get_pos()
        clock.tick(64)
        msg = ""

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                gameRunning = False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                msg = "c" + str(timer) + ","

        sock.sendto(bytes(msg + str(mouse[0]) + "," + str(mouse[1]), "utf-8"), (HOST, PORT))
        received = str(sock.recv(1024), "utf-8")

        if received[0] == "o":
            points = received[1:].split(',')
            if points[0] > max(points[1:]):
                win = True
            elif points[0] == max(points[1:]):
                isDraw = True
            game_state = "final"

        if game_state == "final":
            continue

        parts = received.split(".")
        points = [int(i) for i in parts[0].split(",")]
        op = [int(i) for i in parts[1].split(",")]

        # asteroids
        for pol in parts[2:]:
            cor = [int(i) for i in pol.split(",")]
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(cor[0] - 15, cor[1] - 15, 30, 30))
            screen.blit(asteroid_img, (cor[0] - asteroid_img.get_width() / 2, cor[1] - asteroid_img.get_height() / 2))

        # crosshairs
        screen.blit(crosshair_img,
                    (mouse[0] - crosshair_img.get_width() / 2, mouse[1] - crosshair_img.get_height() / 2))
        screen.blit(crosshair2_img, (op[0] - crosshair2_img.get_width() / 2, op[1] - crosshair2_img.get_height() / 2))

        # scores
        my_score = point_font.render(str(points[0]), True, (4, 219, 15))
        screen.blit(my_score, (SCREEN_WIDTH - my_score.get_width() - 5, SCREEN_HEIGHT - my_score.get_height() - 5))

        pygame.display.update()
    # scoreboard and play again
    else:
        pygame.mouse.set_visible(True)
        mouse = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        msg = "e"
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if SCREEN_WIDTH / 2 - 70 <= mouse[0] <= SCREEN_WIDTH / 2 + 70 and SCREEN_HEIGHT * 0.75 - 20 <= mouse[1] <= SCREEN_HEIGHT * 0.75 + 20:
                    game_state = "lobby"
                    msg = "p"
                    isDraw = False
                    win = False

        sock.sendto(bytes(msg, "utf-8"), (HOST, PORT))
        received = str(sock.recv(1024), "utf-8")

        if isDraw:
            text = finalFont.render("DRAW!", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, SCREEN_HEIGHT / 2 - text.get_height() / 2))
        elif win:
            text = finalFont.render("YOU WON!", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, SCREEN_HEIGHT / 2 - text.get_height() / 2))
        else:
            text = finalFont.render("YOU LOSE!", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, SCREEN_HEIGHT / 2 - text.get_height() / 2))

        # render button "PLAY AGAIN"
        if SCREEN_WIDTH / 2 - 70 <= mouse[0] <= SCREEN_WIDTH / 2 + 70 and SCREEN_HEIGHT * 0.75 - 20 <= mouse[
            1] <= SCREEN_HEIGHT * 0.75 + 20:
            pygame.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT * 0.75 - 20, 140, 40))
        else:
            pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT * 0.75 - 20, 140, 40))
        playAgainButton = font.render('PLAY AGAIN', True, (255, 255, 255))

        screen.blit(playAgainButton, (SCREEN_WIDTH / 2 - playAgainButton.get_width() / 2, SCREEN_HEIGHT * 0.75 - playAgainButton.get_height() / 2))

        # updates the frames of the game
        pygame.display.update()


# sock.sendto(bytes("q", "utf-8"), (HOST, PORT))
# received = str(sock.recv(1024), "utf-8")
sock.close()
print("Disconnected")
