def cords(text):
    ret = text.split(",")
    return int(ret[1]), int(ret[2])


def action(text):
    ret = text.split(",")
    return ret[0]


def asteroids(text):
    ret = text.split(".")
    ret.pop(0)
    return ret


def hitbox(x, y, x2, y2):
    if x2 - 10 <= x < x2 + 10 and y2 - 10 <= y < y2 + 10:
        return True
    return False
