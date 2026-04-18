"""
Classe RobotMobile - Modèle du robot joueur.
Le robot stocke son état (position, orientation, vies, arme) et délègue
le mouvement à son moteur (polymorphisme par composition).
"""

import math
import logging

logger = logging.getLogger(__name__)


class RobotMobile:
    _nb_robots = 0

    def __init__(self, x=0.0, y=0.0, orientation=0.0, rayon=0.3, moteur=None, pv_max=100):
        RobotMobile._nb_robots += 1
        self.__x = x
        self.__y = y
        self.__orientation = orientation
        self.__rayon = rayon
        self.__moteur = moteur
        self.__pv = pv_max
        self.__pv_max = pv_max
        self.__invincible_timer = 0.0
        self.__capteurs = []
        logger.info(f"Robot créé à ({x:.2f}, {y:.2f}), PV={pv_max}")

    # --- Properties (encapsulation) ---
    @property
    def x(self) -> float:
        return self.__x

    @x.setter
    def x(self, value: float):
        self.__x = value

    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, value: float):
        self.__y = value

    @property
    def orientation(self) -> float:
        return self.__orientation

    @orientation.setter
    def orientation(self, value: float):
        self.__orientation = value % (2 * math.pi)

    @property
    def rayon(self) -> float:
        return self.__rayon

    @property
    def pv(self) -> int:
        return self.__pv

    @property
    def pv_max(self) -> int:
        return self.__pv_max

    @property
    def moteur(self):
        return self.__moteur

    @moteur.setter
    def moteur(self, value):
        self.__moteur = value

    @property
    def invincible_timer(self) -> float:
        return self.__invincible_timer

    @invincible_timer.setter
    def invincible_timer(self, value: float):
        self.__invincible_timer = max(0.0, value)

    @property
    def est_invincible(self) -> bool:
        return self.__invincible_timer > 0

    @property
    def est_vivant(self) -> bool:
        return self.__pv > 0

    @property
    def capteurs(self):
        return self.__capteurs

    # --- Méthodes ---
    def ajouter_capteur(self, capteur):
        self.__capteurs.append(capteur)

    def commander(self, **kwargs):
        if self.__moteur is not None:
            self.__moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        if self.__moteur is not None:
            self.__moteur.mettre_a_jour(self, dt)
        if self.__invincible_timer > 0:
            self.__invincible_timer -= dt
            if self.__invincible_timer < 0:
                self.__invincible_timer = 0
        logger.debug(f"Robot mis à jour: ({self.__x:.2f}, {self.__y:.2f})")

    def subir_degat(self, degats=10):
        """Inflige des dégâts au robot. Retourne True si le coup a été pris."""
        if not self.est_invincible:
            self.__pv = max(0, self.__pv - degats)
            self.__invincible_timer = 0.3  # court cooldown anti-spam
            logger.warning(f"Robot touché ({degats} dégâts) ! PV: {self.__pv}/{self.__pv_max}")
            return True
        return False

    def sauvegarder_etat(self):
        return (self.__x, self.__y, self.__orientation)

    def restaurer_etat(self, etat):
        self.__x, self.__y, self.__orientation = etat

    def get_observation(self):
        return {
            "x": self.__x,
            "y": self.__y,
            "orientation": self.__orientation,
            "rayon": self.__rayon,
            "pv": self.__pv,
            "pv_max": self.__pv_max,
        }

    @classmethod
    def nombre_robots(cls) -> int:
        return cls._nb_robots

    @staticmethod
    def moteur_valide(moteur):
        from robot.models.moteurs.moteur import Moteur
        return isinstance(moteur, Moteur)

    def __str__(self):
        return f"Robot(x={self.__x:.2f}, y={self.__y:.2f}, θ={self.__orientation:.2f}, PV={self.__pv}/{self.__pv_max})"
