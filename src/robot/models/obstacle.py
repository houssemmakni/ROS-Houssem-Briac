"""
Classe abstraite Obstacle - Interface commune pour tous les obstacles.
"""

from abc import ABC, abstractmethod


class Obstacle(ABC):
    """Classe abstraite pour tous les obstacles."""

    @abstractmethod
    def collision(self, x, y, rayon) -> bool:
        """Retourne True si un cercle (x, y, rayon) entre en collision."""
        pass

    @abstractmethod
    def intersection_rayon(self, ox, oy, dx, dy, max_range) -> float | None:
        """Retourne la distance d'intersection avec un rayon, ou None."""
        pass

    @abstractmethod
    def get_rect(self) -> tuple:
        """Retourne (x, y, largeur, hauteur) du bounding box."""
        pass
