"""
Classe ObstacleRectangle - Obstacle rectangulaire.
"""

from robot.models.obstacles.obstacle import Obstacle


class ObstacleRectangle(Obstacle):
    """Obstacle rectangulaire défini par position (x, y) coin bas-gauche et dimensions."""

    def __init__(self, x, y, largeur, hauteur):
        self.__x = x
        self.__y = y
        self.__largeur = largeur
        self.__hauteur = hauteur

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def largeur(self):
        return self.__largeur

    @property
    def hauteur(self):
        return self.__hauteur

    def collision(self, x, y, rayon) -> bool:
        closest_x = max(self.__x, min(x, self.__x + self.__largeur))
        closest_y = max(self.__y, min(y, self.__y + self.__hauteur))
        dx = x - closest_x
        dy = y - closest_y
        return (dx * dx + dy * dy) <= rayon * rayon

    def intersection_rayon(self, ox, oy, dx, dy, max_range) -> float | None:
        t_min = 0.0
        t_max = max_range

        x_min = self.__x
        x_max = self.__x + self.__largeur
        y_min = self.__y
        y_max = self.__y + self.__hauteur

        for o, d, mn, mx in ((ox, dx, x_min, x_max), (oy, dy, y_min, y_max)):
            if abs(d) < 1e-8:
                if o < mn or o > mx:
                    return None
            else:
                t1 = (mn - o) / d
                t2 = (mx - o) / d
                t1, t2 = min(t1, t2), max(t1, t2)
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return None

        if 0 < t_min <= max_range:
            return t_min
        return None

    def get_rect(self) -> tuple:
        return (self.__x, self.__y, self.__largeur, self.__hauteur)

    def __str__(self):
        return f"Rectangle({self.__x}, {self.__y}, {self.__largeur}x{self.__hauteur})"
