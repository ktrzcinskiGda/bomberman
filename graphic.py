import sys
import os
import subprocess
from PyQt5 import QtGui, QtWidgets, QtCore, QtMultimedia
import random
import engine
import history
#aimport si

sys._excepthook = sys.excepthook

class Example(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.size, self.padding = 32, 2
        self.mapx0, self.mapy0 = 0, 0
        self.addbomb = False
        self.control = 'k'
        self.images = {'b': QtGui.QPixmap('img/bomb1.png'),
                       'a': QtGui.QPixmap('img/agent.png'),
                       'p': QtGui.QPixmap('img/hero.png'),
                       '@': QtGui.QPixmap('img/boom.png'),
                       'x': QtGui.QPixmap('img/dead.png')}
        self.boomSound = (QtMultimedia.QSound('sounds/boom.wav'),
                          QtMultimedia.QSound('sounds/boom1.wav'),
                          QtMultimedia.QSound('sounds/boom2.wav'),
                          QtMultimedia.QSound('sounds/boom3.wav'))
        self.deadSound = QtMultimedia.QSound('sounds/dead.wav')

    def initUI(self):
        self.setGeometry(100, 100, 520, 520)
        self.setWindowTitle('Okno')
        self.timerEngine = QtCore.QBasicTimer()
        self.timerPeriod = 150
        #self.btnload = QtWidgets.QPushButton("load", self)
        #self.btnload.clicked.connect(self.startlaod)
        self.restart()
        self.show()

    def restart(self):
        engine.world = engine.World()
        engine.player = engine.Player()
        self.soundtrack = QtMultimedia.QSound('sounds/soundtrack.wav')
        self.soundtrack.setLoops(self.soundtrack.Infinite)
        self.soundtrack.play()
        #os.startfile('soundtrack.mp3')
        #s = subprocess.Popen(r'start soundtrack.mp3', stdin=subprocess.PIPE)
        self.timerEngine.start(self.timerPeriod, self)
        self.timerCounter = 0

    def closeEvent(self, QCloseEvent):
        history.save()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() in (QtCore.Qt.Key_D, QtCore.Qt.Key_Right):
            engine.player.vx = 0
            engine.player.vy = 1
        elif QKeyEvent.key() in (QtCore.Qt.Key_A, QtCore.Qt.Key_Left):
            engine.player.vx = 0
            engine.player.vy = -1
        elif QKeyEvent.key() in (QtCore.Qt.Key_W, QtCore.Qt.Key_Up):
            engine.player.vx = -1
            engine.player.vy = 0
        elif QKeyEvent.key() in (QtCore.Qt.Key_S, QtCore.Qt.Key_Down):
            engine.player.vx = 1
            engine.player.vy = 0
        elif QKeyEvent.key() in [QtCore.Qt.Key_Space, QtCore.Qt.Key_B]:
            self.addbomb = True

    def timerEvent(self, *args, **kwargs):
        # dodawanie bomb
        if self.addbomb:
            engine.world.map.addbomb()
            self.addbomb = False
        elif self.control == 'l':
            history.restore()
        # update swiata
        if self.timerCounter*self.timerPeriod >= 450:
            self.timerCounter = 0
            agent_counter = len(engine.world.map.agents)
            engine.world.update()
            history.addTimestamp()
            # dzwiek smierci
            if agent_counter != len(engine.world.map.agents):
                self.deadSound.play()
            # dzwiek bomby
            if '@' in engine.world.map.tile:
                print('boom')
                self.boomSound[random.randint(0, len(self.boomSound)-1)].play()
            # koniec gry
            if engine.player.alive == False:
                self.timerEngine.stop()
                self.gameend('Game over')
            elif len(engine.world.map.agents) == 0:
                self.timerEngine.stop()
                self.gameend('Win')
        else:
            self.timerCounter += 1
        self.repaint()

    def startlaod(self):
        self.control = 'l'

    def gameend(self, text):
        msb = QtWidgets.QMessageBox()
        msb.setWindowTitle(text)
        msb.setInformativeText('Do you wanna play again?')
        msb.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        #b = QtWidgets.QPushButton('naswa', self)
        #b.show()
        ret = msb.exec_()
        if ret == QtWidgets.QMessageBox.Yes:
            self.restart()
        else:
            self.close()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawmap(qp)
        self.drawobjects(qp)
        qp.end()


    def drawmap(self, qp):
        m = engine.world.map.getraw()
        x, y = self.mapx0, self.mapy0
        colors = {' ': QtGui.QColor(200, 200, 150),
                  '#': QtGui.QColor(0, 0, 0),
                  'o': QtGui.QColor(50, 150, 0),
                  'x': QtGui.QColor(250, 0, 50),
                  '@': QtGui.QColor(250, 50, 50),
                  'e': QtGui.QColor(100, 100, 100)}
        for line in m:
            for tile in line:
                if tile in colors:
                    qp.setBrush(colors[tile])
                    qp.drawRect(x, y, self.size, self.size)
                else:
                    qp.setBrush(colors['e'])
                    qp.drawRect(x, y, self.size, self.size)
                if tile in self.images:
                    qp.setBrush(colors[' '])
                    qp.drawRect(x, y, self.size, self.size)
                    qp.drawTiledPixmap(x, y, self.size, self.size, self.images[tile], 0, 0)
                x += self.size + self.padding
            x = self.mapx0
            y += self.size + self.padding

    def get_tile_xy(self, x, y):
        x = self.mapy0+x*(self.size+self.padding) # tak ma byc - python
        y = self.mapx0+y*(self.size+self.padding)
        return y, x

    def drawObjectsList(self, qp, objects, img):
        for a in objects:
            x, y = self.get_tile_xy(a.x, a.y)
            a.spriteCounter = (a.spriteCounter+1) % 4
            if a.vx == 0 and a.vy == 0:
                r, c = 2, 0
                qp.drawTiledPixmap(x, y, self.size, self.size, img, c *self.size, r*self.size)
            else:
                r = 2 if a.vx == 1 else 1 if a.vx == -1 else 0
                c = a.spriteCounter
                qp.drawTiledPixmap(x, y, self.size, self.size, img, c *self.size, r*self.size)
                if r == 0 and a.vy > 0:
                    p = img.copy(c*self.size, r*self.size, self.size, self.size)
                    p = p.transformed(QtGui.QTransform().scale(-1, 1))
                    qp.drawPixmap(x, y, p)
                else:
                    qp.drawTiledPixmap(x, y, self.size, self.size, img, c*self.size, r*self.size)

    def drawobjects(self, qp):
        for b in engine.world.map.bombs:
            wx, wy = self.get_tile_xy(b.x, b.y)
            qp.drawTiledPixmap(wx, wy, self.size, self.size, self.images['b'], 0, 0)
        self.drawObjectsList(qp, engine.world.map.agents, self.images['a'])
        self.drawObjectsList(qp, [engine.player], self.images['p'])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    res = 0
    try:
        res = app.exec_()
    except Exception as e:
        print("wyjatek")
        print(e)
    sys.exit(res)


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
