"""
Classe abstraite Controleur - Interface commune pour tous les contrôleurs.
"""

from abc import ABC, abstractmethod


class Controleur(ABC):
    """Classe abstraite pour tous les contrôleurs."""

    @abstractmethod
    def lire_commande(self):
        """Retourne une commande pour le robot."""
        pass
