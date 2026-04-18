"""
Classe ObstacleCirculaire - Obstacle circulaire.
"""

import math

from robot.models.obstacles.obstacle import Obstacle


class ObstacleCirculaire(Obstacle):
    """Obstacle circulaire défini par un centre (x, y) et un rayon."""

    def __init__(self, x, y, rayon):
        self.__x = x
        self.__y = y
        self.__rayon = rayon

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def rayon(self):
        return self.__rayon

    def collision(self, x, y, rayon) -> bool:
        dx = x - self.__x
        dy = y - self.__y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist <= (self.__rayon + rayon)

    def intersection_rayon(self, ox, oy, dx, dy, max_range) -> float | None:
        fx = ox - self.__x
        fy = oy - self.__y
        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - self.__rayon * self.__rayon

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None

        discriminant = math.sqrt(discriminant)
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        for t in (t1, t2):
            if 0 < t <= max_range:
                return t
        return None

    def get_rect(self) -> tuple:
        return (self.__x - self.__rayon, self.__y - self.__rayon,
                self.__rayon * 2, self.__rayon * 2)

    def __str__(self):
        return f"Cercle({self.__x}, {self.__y}, r={self.__rayon})"
