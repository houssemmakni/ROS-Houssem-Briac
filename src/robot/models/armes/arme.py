"""
Classe abstraite Arme - Interface commune pour toutes les armes.
"""

import time
from abc import ABC, abstractmethod


class Arme(ABC):
    """Classe abstraite pour toutes les armes."""

    def __init__(self, nom, degats, cadence, munitions_max, portee, vitesse_projectile):
        self._nom = nom
        self._degats = degats
        self._cadence = cadence  # tirs par seconde
        self._munitions = munitions_max
        self._munitions_max = munitions_max
        self._portee = portee
        self._vitesse_projectile = vitesse_projectile
        self._dernier_tir = 0.0
        self._temps_regen = 0.0

    @property
    def nom(self):
        return self._nom

    @property
    def degats(self):
        return self._degats

    @property
    def munitions(self):
        return self._munitions

    @property
    def munitions_max(self):
        return self._munitions_max

    @property
    def portee(self):
        return self._portee

    @property
    def vitesse_projectile(self):
        return self._vitesse_projectile

    def peut_tirer(self) -> bool:
        if self._munitions <= 0:
            return False
        now = time.time()
        return (now - self._dernier_tir) >= (1.0 / self._cadence)

    def regenerer(self, dt):
        """Régénère les munitions automatiquement."""
        self._temps_regen += dt
        if self._temps_regen >= 0.8:
            self._temps_regen = 0.0
            if self._munitions < self._munitions_max:
                self._munitions += 1

    @abstractmethod
    def tirer(self, x, y, angle) -> list:
        """Retourne une liste de projectiles créés."""
        pass
