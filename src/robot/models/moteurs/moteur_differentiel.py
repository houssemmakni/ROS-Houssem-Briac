"""
Classe MoteurDifferentiel - Moteur commandé par v (linéaire) et omega (angulaire).
"""

import math
import logging

from robot.models.moteurs.moteur import Moteur

logger = logging.getLogger(__name__)


class MoteurDifferentiel(Moteur):
    """Moteur différentiel : commandé par v (linéaire) et omega (angulaire)."""

    def __init__(self, v=0.0, omega=0.0):
        self.v = v
        self.omega = omega

    def commander(self, v=0.0, omega=0.0, **kwargs):
        self.v = v
        self.omega = omega
        logger.debug(f"Commande diff: v={v:.2f}, omega={omega:.2f}")

    def mettre_a_jour(self, robot, dt):
        robot.orientation = robot.orientation + self.omega * dt
        robot.x = robot.x + self.v * math.cos(robot.orientation) * dt
        robot.y = robot.y + self.v * math.sin(robot.orientation) * dt
