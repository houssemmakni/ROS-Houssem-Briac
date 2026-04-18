"""
Classe FusilAPompe - Tirs multiples en éventail, cadence lente, courte portée.
"""

import time

from robot.models.armes.arme import Arme
from robot.models.armes.projectile import Projectile


class FusilAPompe(Arme):
    """Fusil à pompe - tirs multiples en éventail, cadence lente, courte portée."""

    def __init__(self):
        super().__init__(
            nom="Fusil a Pompe",
            degats=15,
            cadence=1.2,
            munitions_max=16,
            portee=5.0,
            vitesse_projectile=10.0,
        )

    def tirer(self, x, y, angle) -> list:
        if not self.peut_tirer():
            return []
        self._munitions -= 1
        self._dernier_tir = time.time()
        projectiles = []
        spread = 0.35
        for i in range(-2, 3):
            a = angle + i * spread * 0.5
            projectiles.append(
                Projectile(x, y, a, self._vitesse_projectile, self._degats,
                           self._portee, est_joueur=True, couleur=(255, 165, 0))
            )
        return projectiles
