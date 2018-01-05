import pyglet
import numpy as np

class window(pyglet.window.Window):
    def __init__(self, nbBoule=12, periode=3, sensTrigo=False, width=600, height=600, fps=60):

        self.nbBoule = nbBoule
        self.part = self.nbBoule * 2

        self.periode = periode  # periode de l'animation

        self.sensTrigo = sensTrigo

        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()

        screen_width = screen.width
        screen_height = screen.height

        # on init la fenetre
        super(window, self).__init__(screen=screen,
                                     width=width,
                                     height=height,
                                     vsync=False)

        # on le met la window au centre de l'ecran
        # x_win, y_win = self.get_location()
        self.set_location((screen_width - self.width) // 2,
                          (screen_height - self.height) // 2)
        pyglet.gl.glClearColor(1, 1, 1, 1)

        self.fps = fps
        ##############
        self.batch = pyglet.graphics.Batch()

        self.background = pyglet.graphics.OrderedGroup(0)
        self.midleground = pyglet.graphics.OrderedGroup(1)
        self.foreground = pyglet.graphics.OrderedGroup(2)

        for i in range(self.nbBoule):
            setattr(self, 'b' + str(i), pyglet.graphics.OrderedGroup(3 + i))

        ##############

        self.middle = np.array([self.width / 2, self.height / 2])
        self.radius = 280

        ###############################################################
        self.circle = self.makeCircle(self.middle, self.radius, (0, 0, 0), self.background)
        self.coupeCircle()

        ### mtn on fait les boules
        self.rad = 10

        # on initialize ce qui va nous permettre de faire l'animation des boules
        self.count = [i * (self.periode / (2 * self.nbBoule)) for i in range(self.nbBoule)]

        self.pStart, self.pointeur = self.prepareAnim()
        self.boules = []

        # on dessine toutes les boules à leurs pos de debut
        for b in range(self.nbBoule):
            p = self.givePosBoule(b)
            boule = self.makeCircle(np.array([p]), self.rad, (255, 255, 255), getattr(self, 'b' + str(b)))
            self.boules.append(boule)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def makeCircleVertice(self, center, radius, fill=True):

        '''Génere une liste des coordonées d'un cercle de centre'''
        nbPoints = round(2 * np.pi * radius) + 1

        s = np.sin(2 * np.pi / (nbPoints - 1))
        c = np.cos(2 * np.pi / (nbPoints - 1))

        dx, dy = radius, 0

        if fill:
            circleArray = np.zeros(((nbPoints * 2) + 2,))
            circleArray[0:2] = center
            nbPoints += 1
        else:
            circleArray = np.zeros((nbPoints * 2,))

        start = 2 if fill else 0
        # on parcours toutes les abscices

        for x in range(start, nbPoints * 2, 2):
            circleArray[x:x + 2] = center + np.array([dx, dy])
            dx, dy = (dx * c - dy * s), (dy * c + dx * s)

        return nbPoints, circleArray

    def makeCircle(self,
                   center,
                   radius,
                   color,
                   grp,
                   fill=True,
                   static=True):

        nbPoints, circleArray = self.makeCircleVertice(center, radius, fill)

        type = pyglet.gl.GL_TRIANGLE_FAN if fill else pyglet.gl.GL_LINE_STRIP
        mvt = 'static' if static else 'stream'

        return self.batch.add(nbPoints,
                              type,
                              grp,
                              ('v2f', circleArray),
                              ('c3B/static', color * nbPoints))

    def coupeCircle(self):

        lignes = np.array([])

        dTheta = (2 * np.pi) / self.part

        for i in range(self.part // 2):
            x0, y0 = self.radius * np.cos(dTheta * i), self.radius * np.sin(dTheta * i)
            x1, y1 = self.radius * np.cos(np.pi + (dTheta * i)), self.radius * np.sin(np.pi + (dTheta * i))

            p0 = self.middle + np.array([x0, y0])
            p1 = self.middle + np.array([x1, y1])

            lignes = np.append(lignes, [p0, p1])

        self.batch.add(self.part,
                       pyglet.gl.GL_LINES,
                       self.midleground,
                       ('v2f\static', lignes),
                       ('c3B\static', (125, 125, 125) * self.part))

    def prepareAnim(self):

        pStart = []
        pointeurs = []

        lignes = np.array([])

        dTheta = (2 * np.pi) / self.part

        for i in range(self.part // 2):
            x0, y0 = (self.radius - self.rad) * np.cos(dTheta * i), (self.radius - self.rad) * np.sin(dTheta * i)
            x1, y1 = (self.radius - self.rad) * np.cos(np.pi + (dTheta * i)), (self.radius - self.rad) * np.sin(
                np.pi + (dTheta * i))

            p0 = self.middle + np.array([x0, y0])
            p1 = self.middle + np.array([x1, y1])

            pStart.append(p0)
            pointeurs.append(p1 - p0)

        return pStart, pointeurs

    def givePosBoule(self, n):
        return self.pStart[n] + (f(self.count[n], self.periode) * self.pointeur[n])

    def update(self, dt):

        for i in range(self.nbBoule):
            self.count[i] += dt * (-1) ** self.sensTrigo

            p = self.givePosBoule(i)  # on recup les nouvelles coords
            self.boules[i].vertices = self.makeCircleVertice(np.array([p]), self.rad)[1]  # on les updates


def f(x, periode):
    return 0.5 * np.cos((x * 2 * np.pi / periode) + np.pi) + 0.5


if __name__ == '__main__':
    main = window()
    pyglet.clock.schedule_interval(main.update, 1 / main.fps)
    pyglet.app.run()
