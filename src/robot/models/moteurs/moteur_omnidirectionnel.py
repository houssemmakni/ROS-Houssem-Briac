"""
Classe MoteurOmnidirectionnel - Moteur commandé par vx, vy et omega.
"""

import math
import logging

from robot.models.moteurs.moteur import Moteur

logger = logging.getLogger(__name__)


class MoteurOmnidirectionnel(Moteur):
    """Moteur omnidirectionnel : commandé par vx, vy et omega."""

    def __init__(self, vx=0.0, vy=0.0, omega=0.0):
        self.vx = vx
        self.vy = vy
        self.omega = omega

    def commander(self, vx=0.0, vy=0.0, omega=0.0, **kwargs):
        self.vx = vx
        self.vy = vy
        self.omega = omega
        logger.debug(f"Commande omni: vx={vx:.2f}, vy={vy:.2f}, omega={omega:.2f}")

    def mettre_a_jour(self, robot, dt):
        robot.orientation = robot.orientation + self.omega * dt
        theta = robot.orientation
        robot.x = robot.x + (self.vx * math.cos(theta) - self.vy * math.sin(theta)) * dt
        robot.y = robot.y + (self.vx * math.sin(theta) + self.vy * math.cos(theta)) * dt
