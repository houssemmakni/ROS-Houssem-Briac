"""
Classe abstraite Strategy - Interface pour les stratégies de navigation réactive.
Design Pattern Strategy : encapsule des comportements interchangeables.
"""

from abc import ABC, abstractmethod


class Strategy(ABC):
    """Interface commune pour toutes les stratégies de navigation."""

    @abstractmethod
    def compute_command(self, observation):
        """Calcule une commande (v, omega) à partir de l'observation capteurs.

        Paramètres:
            observation: dict contenant 'x', 'y', 'orientation', 'lidar_distances'

        Retourne:
            dict avec 'v' et 'omega'
        """
        pass
