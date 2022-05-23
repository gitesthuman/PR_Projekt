import random

width = 640
height = 480


class Asteroid:
    def __init__(self):
        self.__size = 64
        self.__dx = 1
        self.__dy = 1

        rand = random.randint(0, 4)
        if rand < 2:
            self.__x = random.randint(0, 1) * width
            self.__y = random.randint(0, height)
            if self.__x == 0:
                self.__x -= self.__size // 2
            else:
                self.__x += self.__size // 2
        elif rand < 4:
            self.__x = random.randint(0, width)
            self.__y = random.randint(0, 1) * height
            if self.__y == 0:
                self.__y -= self.__size // 2
            else:
                self.__y += self.__size // 2
        else:
            self.__x = random.randint(self.__size//2, width - self.__size//2)
            self.__y = random.randint(self.__size//2, height - self.__size//2)
            self.__dx = 0
            self.__dy = 0

        self.__dx *= random.random() * 10
        self.__dy *= random.random() * 10

        if self.__x >= width / 2:
            self.__dx *= -1
        if self.__y >= height / 2:
            self.__dy *= -1

    def hitbox(self, pos):
        if self.__x - self.__size/2 <= pos[0] < self.__x + self.__size/2 \
                and self.__y - self.__size/2 <= pos[1] < self.__y + self.__size/2:
            return True
        return False

    def out(self):
        if self.__x < -self.__size*2 or self.__x > width + self.__size*2 or self.__y < -self.__size*2 or self.__y > height + self.__size*2:
            return True
        return False

    def cords(self):
        return self.__x, self.__y

    def move(self):
        self.__x += self.__dx
        self.__y += self.__dy
