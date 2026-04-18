"""
Classe Laser - Tir précis, très rapide, longue portée.
"""

import time

from robot.models.armes.arme import Arme
from robot.models.armes.projectile import Projectile


class Laser(Arme):
    """Laser - tir précis, très rapide, longue portée."""

    def __init__(self):
        super().__init__(
            nom="Laser",
            degats=35,
            cadence=2.5,
            munitions_max=20,
            portee=15.0,
            vitesse_projectile=25.0,
        )

    def tirer(self, x, y, angle) -> list:
        if not self.peut_tirer():
            return []
        self._munitions -= 1
        self._dernier_tir = time.time()
        return [Projectile(x, y, angle, self._vitesse_projectile, self._degats,
                           self._portee, est_joueur=True, couleur=(255, 0, 0), taille=3)]
