"""
Classe ControleurPID - Contrôle local proportionnel pour le suivi de chemin.
Calcule v (vitesse linéaire) et omega (vitesse angulaire) à partir de
l'erreur de position et d'orientation vers un point cible.
"""

import math

from robot.controllers.controleur import Controleur


class ControleurPID(Controleur):
    """Contrôleur proportionnel pour le suivi de chemin A*."""

    def __init__(self, kp_lin=1.5, kp_ang=4.0, tolerance=0.3):
        self.__kp_lin = kp_lin    # Gain proportionnel linéaire
        self.__kp_ang = kp_ang    # Gain proportionnel angulaire
        self.__tolerance = tolerance  # Distance min pour considérer un point atteint
        self.__chemin = []
        self.__index = 0

    @property
    def chemin(self):
        return self.__chemin

    @property
    def index(self):
        return self.__index

    @property
    def a_fini(self):
        """Retourne True si le chemin est terminé."""
        return self.__index >= len(self.__chemin)

    def set_chemin(self, chemin):
        """Définit un nouveau chemin à suivre."""
        self.__chemin = chemin
        self.__index = 0

    def lire_commande(self, **kwargs):
        """Interface Controleur (non utilisée directement, voir calculer_commande)."""
        return {"v": 0.0, "omega": 0.0}

    def calculer_commande(self, obs):
        """Calcule la commande (v, omega) pour suivre le chemin.

        Paramètres:
            obs: dict avec 'x', 'y', 'orientation' du robot

        Retourne:
            dict avec 'v' et 'omega'
        """
        # 1. Si le chemin est terminé, arrêter
        if self.__index >= len(self.__chemin):
            return {"v": 0.0, "omega": 0.0}

        x = obs["x"]
        y = obs["y"]
        theta = obs["orientation"]

        # 2. Extraire le waypoint courant
        x_c, y_c = self.__chemin[self.__index]

        # 3. Calculer l'erreur de position
        dx = x_c - x
        dy = y_c - y
        distance = math.sqrt(dx * dx + dy * dy)

        # 4. Si le point est atteint, passer au suivant
        if distance < self.__tolerance:
            self.__index += 1
            return {"v": 0.0, "omega": 0.0}

        # 5. Calculer l'angle désiré
        theta_des = math.atan2(dy, dx)

        # 6. Calculer l'erreur angulaire, normalisée dans [-pi, pi]
        e_theta = theta_des - theta
        while e_theta > math.pi:
            e_theta -= 2 * math.pi
        while e_theta < -math.pi:
            e_theta += 2 * math.pi

        # 7. Calculer les commandes proportionnelles
        v = self.__kp_lin * distance
        omega = self.__kp_ang * e_theta

        # 8. Retourner la commande
        return {"v": v, "omega": omega}
