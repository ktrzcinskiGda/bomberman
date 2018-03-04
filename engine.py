import random
import numpy as np


class Map:
    def __init__(self):
        print("konstruktor mapy")
        self.w, self.h = 15, 15
        self.tile = np.array([[ '#' if (x % 2 == 0 and y % 2 == 0) or x == 0 or y == 0 or x+1 == self.w or y+1 == self.h else
                       'o' if random.random() < 0.3 else
                       ' ' for x in range(self.w)] for y in range(self.h)])
        self.bombs = []
        self.agents = [Agent(9, 7), Agent(3, 5)]
        self.collidable_cells = ('#', 'o', 'b')

    def destroy(self, x, y):
        self.tile[x, y] = '@'
        for a in self.agents:
            if a.x == x and a.y == y:
                a.alive = False
        for b in self.bombs:
            if b.x == x and b.y == y:
                b.time = 0
        if player.x == x and player.y == y:
            player.alive = False

    def addbomb(self, x=-1, y=-1, t=5):
        if x < 0:
            x = player.x
        if y < 0:
            y = player.y
        self.bombs.append(Bomb(x, y, t))

    def __str__(self):
        s = ''
        for l in self.tile:
            s += ' '

    def getraw(self):
        return np.array(self.tile)

    def get(self):
        res = np.array(self.tile)
        for b in self.bombs: res[b.x, b.y] = 'b'
        for a in self.agents: res[a.x, a.y] = 'a' if a.alive else 'x'
        res[player.x, player.y] = 'p' if player.alive else 'x'
        return res

    def update(self):
        self.tile[self.tile == '@'] = ' '
        m = self.get()
        for b in self.bombs:
            if b.update(m):
                self.bombs.remove(b)
        for a in self.agents:
            if a.alive:
                a.update()
            else:
                self.tile[a.x, a.y] = 'x'
                self.agents.remove(a)


class Agent:
    def __init__(self, x, y):
        print("konstruktor Agenta")
        self.x, self.y = x, y
        self.vx, self.vy = 1, 0
        self.alive = True
        self.spriteCounter = 0

    def getmoves(self):
        m = []
        if world.map.tile[self.x+1, self.y] not in world.map.collidable_cells:
            m.append((1, 0))
        if world.map.tile[self.x-1, self.y] not in world.map.collidable_cells:
            m.append((-1, 0))
        if world.map.tile[self.x, self.y+1] not in world.map.collidable_cells:
            m.append((0, 1))
        if world.map.tile[self.x, self.y-1] not in world.map.collidable_cells:
            m.append((0, -1))
        return m

    def move(self, dx, dy):
        m = world.map.get()
        if m[self.x+dx, self.y+dy] not in world.map.collidable_cells:
            self.x += dx
            self.y += dy

    def makemove(self, tile):
        m = self.getmoves()
        if (self.vx, self.vy) in m and random.random() < 0.7:  # losowana jest zmiana kierunku ruchu
            self.move(self.vx, self.vy)
        elif len(m) > 0 and random.random() > 0.2:  # losowany jest postuj
            mm = m[random.randint(0, len(m)-1)]
            self.vx, self.vy = mm
            self.move(self.vx, self.vy)

    def update(self):
        if not self.alive:
            return
        self.makemove(world.map.tile)
        # bomba
        if world.map.tile[self.x, self.y] == '@':
            world.map.tile[self.x, self.y] = 'x'
            self.alive = False
        # kolizja z graczem
        if (player.x, player.y) == (self.x, self.y):
            player.alive = False
            world.map.tile[self.x, self.y] = 'x'


class Bomb:
    def __init__(self, x, y, t=5):
        self.x, self.y = x, y
        self.time = t

    def update(self, map):
        if self.time > 0:
            self.time -= 1
        else:
            self.boom(random.randint(2, 4))
            return True  # usun bombe
        return False  # nie niszcz bomby

    @staticmethod
    def _boom_part(x0, xl, y0, yl):
        xx = list(range(x0, xl, 1 if xl > x0 else -1)) if xl != x0 else [x0] * np.abs(yl-y0)
        yy = list(range(y0, yl, 1 if yl > y0 else -1)) if yl != y0 else [y0] * np.abs(xl-x0)
        for n in range(len(xx)):
            x, y = xx[n], yy[n]
            t = world.map.tile[x, y]
            if x < 0 or x+1 >= world.map.w: return
            elif y < 0 or y+1 >= world.map.h: return
            elif t == '#': return
            elif t in world.map.collidable_cells and random.random() < 0.4:
                world.map.destroy(x, y)
                return
            else:
                world.map.destroy(x, y)

    def boom(self, r=3):
        self._boom_part(self.x, self.x+r, self.y, self.y)
        self._boom_part(self.x, self.x-r, self.y, self.y)
        self._boom_part(self.x, self.x, self.y, self.y+r)
        self._boom_part(self.x, self.x, self.y, self.y-r)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

class Player(Agent):
    def __init__(self, x=2, y=3):
        super(Player, self).__init__(x, y)
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.alive = True
        for x in range(clamp(x-2, 0, world.map.w), clamp(x+2, 0, world.map.w)):
            for y in range(clamp(y-2, 0, world.map.h), clamp(y+2, 0, world.map.h)):
                if world.map.tile[x, y] == 'o':
                    world.map.tile[x, y] = ' '
        print("konstruktor Player")

    def update(self):
        self.move(self.vx, self.vy)
        self.vx, self.vy = 0, 0


class World:
    def __init__(self):
        self.map = Map()

    def draw(self):
        print('')
        print('')
        g = self.map.get()
        for line in g:
            print(' '.join(line))
        print('')

    def update(self):
        player.update()
        self.map.update()


world = World()
player = Player()


if __name__ == '__main__':
    ruch = ' '
    ruchy = {'w': (-1, 0), 'a': (0, -1), 'd': (0, 1), 's': (1, 0)}
    while ruch != 'q' and player.alive:
        world.draw()
        ruch = input('Gdzie sie ruszyc [wsad]')
        if ruch in ruchy:
            dx, dy = ruchy[ruch]
            player.vx, player.vy = dx, dy
        elif ruch == 'b':
            world.map.addbomb()
        world.update()

    world.draw()
    print('Game Over')
