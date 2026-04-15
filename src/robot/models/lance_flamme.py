"""
Classe LanceFlamme - Courte portée, dégâts en zone, cadence élevée.
"""

import time
import random

from robot.models.arme import Arme
from robot.models.projectile import Projectile


class LanceFlamme(Arme):
    """Lance-flamme - courte portée, dégâts en zone, cadence élevée."""

    def __init__(self):
        super().__init__(
            nom="Lance-Flamme",
            degats=8,
            cadence=10.0,
            munitions_max=100,
            portee=3.0,
            vitesse_projectile=6.0,
        )

    def tirer(self, x, y, angle) -> list:
        if not self.peut_tirer():
            return []
        self._munitions -= 1
        self._dernier_tir = time.time()
        projectiles = []
        for _ in range(3):
            spread = random.uniform(-0.25, 0.25)
            a = angle + spread
            speed = self._vitesse_projectile + random.uniform(-1, 1)
            projectiles.append(
                Projectile(x, y, a, speed, self._degats, self._portee,
                           est_joueur=True, couleur=(255, 100, 0), taille=4, est_flamme=True)
            )
        return projectiles
