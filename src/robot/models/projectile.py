"""
Classe Projectile - Représente un tir (balle, laser, flamme).
"""

import math


class Projectile:
    """Un projectile se déplaçant en ligne droite."""

    def __init__(self, x, y, angle, vitesse, degats, portee,
                 est_joueur=True, couleur=(255, 255, 0), taille=2, est_flamme=False):
        self.__x = x
        self.__y = y
        self.__angle = angle
        self.__vitesse = vitesse
        self.__degats = degats
        self.__portee = portee
        self.__distance_parcourue = 0.0
        self.__est_joueur = est_joueur
        self.__couleur = couleur
        self.__taille = taille
        self.__est_flamme = est_flamme
        self.__vivant = True

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def angle(self):
        return self.__angle

    @property
    def degats(self):
        return self.__degats

    @property
    def est_joueur(self):
        return self.__est_joueur

    @property
    def couleur(self):
        return self.__couleur

    @property
    def taille(self):
        return self.__taille

    @property
    def est_flamme(self):
        return self.__est_flamme

    @property
    def vivant(self):
        return self.__vivant

    def mettre_a_jour(self, dt):
        """Déplace le projectile."""
        dx = self.__vitesse * math.cos(self.__angle) * dt
        dy = self.__vitesse * math.sin(self.__angle) * dt
        self.__x += dx
        self.__y += dy
        self.__distance_parcourue += (dx * dx + dy * dy) ** 0.5
        if self.__distance_parcourue >= self.__portee:
            self.__vivant = False

    def __str__(self):
        return f"Projectile({self.__x:.2f}, {self.__y:.2f})"
