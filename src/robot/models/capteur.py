"""
Classes Capteur - Abstraction pour les capteurs du robot.
Capteur (abstraite) - interface commune pour tous les capteurs.
"""

from abc import ABC, abstractmethod


class Capteur(ABC):
    """Classe abstraite pour tous les capteurs."""

    def __init__(self, robot):
        self._robot = robot

    @abstractmethod
    def lire(self, env):
        """Retourne une observation depuis l'environnement."""
        pass

    @abstractmethod
    def dessiner(self, screen, convertir):
        """Dessine la représentation du capteur (optionnel)."""
        pass
