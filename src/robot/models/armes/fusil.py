"""
Classe Fusil - Tir unique, cadence moyenne, bonne portée.
"""

import time

from robot.models.armes.arme import Arme
from robot.models.armes.projectile import Projectile


class Fusil(Arme):
    """Fusil standard - tir unique, cadence moyenne, bonne portée."""

    def __init__(self):
        super().__init__(
            nom="Fusil",
            degats=25,
            cadence=4.0,
            munitions_max=30,
            portee=12.0,
            vitesse_projectile=15.0,
        )

    def tirer(self, x, y, angle) -> list:
        if not self.peut_tirer():
            return []
        self._munitions -= 1
        self._dernier_tir = time.time()
        return [Projectile(x, y, angle, self._vitesse_projectile, self._degats,
                           self._portee, est_joueur=True, couleur=(255, 255, 0))]
