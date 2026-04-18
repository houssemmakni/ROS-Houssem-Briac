"""
Classe Lidar - Capteur de distance simulé.
Envoie des rayons autour du robot pour mesurer les distances aux obstacles.
"""

import math
from robot.models.capteurs.capteur import Capteur


class Lidar(Capteur):
    """Capteur Lidar simulé : mesure les distances par lancer de rayons."""

    def __init__(self, robot, nb_rayons=36, max_range=8.0, fov=2 * math.pi):
        super().__init__(robot)
        self.__nb_rayons = nb_rayons
        self.__max_range = max_range
        self.__fov = fov
        self.__distances = [max_range] * nb_rayons
        self.__rays_world = []

    @property
    def nb_rayons(self):
        return self.__nb_rayons

    @property
    def max_range(self):
        return self.__max_range

    @property
    def distances(self):
        return list(self.__distances)

    def lire(self, env):
        """Lance les rayons et mesure les distances aux obstacles."""
        self.__distances = []
        self.__rays_world = []
        rx, ry = self._robot.x, self._robot.y
        theta = self._robot.orientation
        start_angle = theta - self.__fov / 2

        for i in range(self.__nb_rayons):
            angle = start_angle + i * self.__fov / self.__nb_rayons
            dx = math.cos(angle)
            dy = math.sin(angle)

            dist_min = self.__max_range
            for obs in env.obstacles:
                t = obs.intersection_rayon(rx, ry, dx, dy, self.__max_range)
                if t is not None and t < dist_min:
                    dist_min = t

            self.__distances.append(dist_min)

            # Points du rayon dans le monde
            x2 = rx + dx * dist_min
            y2 = ry + dy * dist_min
            self.__rays_world.append((rx, ry, x2, y2, dist_min))

        return self.__distances

    def get_rays_world(self, env=None):
        """Retourne les rayons dans le repère monde."""
        if env is not None:
            self.lire(env)
        return self.__rays_world

    def dessiner(self, screen, convertir):
        """Dessine les rayons du lidar."""
        import pygame
        for rx, ry, x2, y2, dist in self.__rays_world:
            p1 = convertir(rx, ry)
            p2 = convertir(x2, y2)
            ratio = dist / self.__max_range
            color = (0, int(255 * (1 - ratio)), int(255 * ratio))
            pygame.draw.line(screen, color, p1, p2, 1)
