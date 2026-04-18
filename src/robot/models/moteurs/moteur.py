"""
Classe abstraite Moteur - Interface commune pour tous les moteurs.
"""

from abc import ABC, abstractmethod


class Moteur(ABC):
    """Classe abstraite pour tous les moteurs."""

    @abstractmethod
    def commander(self, *args, **kwargs):
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        pass
