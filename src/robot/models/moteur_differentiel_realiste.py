"""
Classe MoteurDifferentielRealiste - Moteur avec inertie, frottements, saturation et bruit.
"""

import math
import random

from robot.models.moteur import Moteur


class MoteurDifferentielRealiste(Moteur):
    """Moteur différentiel réaliste avec inertie, frottements, saturation et bruit."""

    def __init__(self, a_max=3.0, alpha_max=4.0, v_max=3.0, omega_max=4.0,
                 friction=0.5, bruit_sigma=0.02):
        self.__v_cmd = 0.0
        self.__omega_cmd = 0.0
        self.__v_reel = 0.0
        self.__omega_reel = 0.0
        self.__a_max = a_max
        self.__alpha_max = alpha_max
        self.__v_max = v_max
        self.__omega_max = omega_max
        self.__friction = friction
        self.__bruit_sigma = bruit_sigma

    def commander(self, v=0.0, omega=0.0, **kwargs):
        self.__v_cmd = v
        self.__omega_cmd = omega

    def mettre_a_jour(self, robot, dt):
        # 1. Limitation d'accélération
        dv = self.__v_cmd - self.__v_reel
        dv = max(-self.__a_max * dt, min(dv, self.__a_max * dt))
        self.__v_reel += dv

        domega = self.__omega_cmd - self.__omega_reel
        domega = max(-self.__alpha_max * dt, min(domega, self.__alpha_max * dt))
        self.__omega_reel += domega

        # 2. Frottements
        self.__v_reel *= (1 - self.__friction * dt)
        self.__omega_reel *= (1 - self.__friction * dt)

        # 3. Saturation
        self.__v_reel = max(-self.__v_max, min(self.__v_reel, self.__v_max))
        self.__omega_reel = max(-self.__omega_max, min(self.__omega_reel, self.__omega_max))

        # 4. Bruit
        v = self.__v_reel + random.uniform(-self.__bruit_sigma, self.__bruit_sigma)
        omega = self.__omega_reel + random.uniform(-self.__bruit_sigma, self.__bruit_sigma)

        # 5. Cinématique
        robot.orientation = robot.orientation + omega * dt
        robot.x = robot.x + v * math.cos(robot.orientation) * dt
        robot.y = robot.y + v * math.sin(robot.orientation) * dt
