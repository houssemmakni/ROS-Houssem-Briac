"""
Classe Zombie - Ennemi intelligent qui poursuit le robot.
Utilise A* pour le pathfinding et le Strategy Pattern pour le comportement.
Peut tirer avec des armes à partir de la vague 5.
"""

import math
import random
import time
import logging

from robot.models.projectile import Projectile
from robot.controllers.navigator import Navigator
from robot.controllers.goal_strategy import GoalStrategy

logger = logging.getLogger(__name__)


class Zombie:
    """Un zombie avec IA intelligente : A* pathfinding + Strategy pattern."""

    def __init__(self, x, y, vitesse=1.0, pv=50, rayon=0.3, arme=None):
        self.__x = x
        self.__y = y
        self.__vitesse = vitesse
        self.__pv = pv
        self.__pv_max = pv
        self.__rayon = rayon
        self.__orientation = 0.0
        self.__arme = arme
        self.__dernier_tir = 0.0
        self.__cadence_tir = 1.0

        # Navigation intelligente avec Strategy Pattern
        self.__strategy = GoalStrategy(goal=(x, y), seuil_obstacle=1.0,
                                       k_attraction=1.0, k_repulsion=1.5)
        self.__navigator = Navigator(self.__strategy)

        # A* pathfinding
        self.__chemin = []
        self.__chemin_index = 0
        self.__timer_recalcul = 0.0
        self.__intervalle_recalcul = 1.0  # recalcul A* toutes les 1s

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value

    @property
    def orientation(self):
        return self.__orientation

    @property
    def rayon(self):
        return self.__rayon

    @property
    def pv(self):
        return self.__pv

    @property
    def pv_max(self):
        return self.__pv_max

    @property
    def est_vivant(self):
        return self.__pv > 0

    @property
    def arme(self):
        return self.__arme

    @property
    def chemin(self):
        """Chemin A* actuel (pour le debug/affichage)."""
        return self.__chemin

    def subir_degat(self, degats):
        self.__pv -= degats
        if self.__pv <= 0:
            self.__pv = 0
            logger.debug(f"Zombie éliminé à ({self.__x:.2f}, {self.__y:.2f})")

    def mettre_a_jour(self, env, dt, grille=None, planificateur=None):
        """Met à jour le zombie : pathfinding A* + navigation réactive + tir."""
        robot = env.robot
        if not robot or not robot.est_vivant:
            return

        dx = robot.x - self.__x
        dy = robot.y - self.__y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0.01:
            self.__orientation = math.atan2(dy, dx)

        # --- Pathfinding A* (si grille disponible) ---
        self.__timer_recalcul += dt
        cible_x, cible_y = robot.x, robot.y

        if planificateur and grille and self.__timer_recalcul >= self.__intervalle_recalcul:
            self.__timer_recalcul = 0.0
            chemin = planificateur.trouver_chemin(
                (self.__x, self.__y), (robot.x, robot.y)
            )
            if chemin and len(chemin) > 1:
                self.__chemin = chemin
                self.__chemin_index = 1  # skip le point de départ

        # Suivre le chemin A* : viser le waypoint look-ahead
        if self.__chemin and self.__chemin_index < len(self.__chemin):
            # Look-ahead : viser un point un peu plus loin dans le chemin
            look_ahead = min(self.__chemin_index + 3, len(self.__chemin) - 1)
            cible_x, cible_y = self.__chemin[look_ahead]

            # Avancer l'index si le waypoint courant est atteint
            wx, wy = self.__chemin[self.__chemin_index]
            d_wp = math.sqrt((self.__x - wx) ** 2 + (self.__y - wy) ** 2)
            if d_wp < 0.5:
                self.__chemin_index += 1

        # --- Navigation réactive (Strategy Pattern) ---
        self.__strategy.goal = (cible_x, cible_y)

        # Construire l'observation pour la Strategy
        observation = {
            "x": self.__x,
            "y": self.__y,
            "orientation": self.__orientation,
            "lidar_distances": self._scan_rapide(env),
        }

        cmd = self.__navigator.step(observation)
        v = min(cmd.get("v", 0), self.__vitesse)
        omega = cmd.get("omega", 0)

        # --- Déplacement ---
        if dist > self.__rayon + robot.rayon + 0.1:
            angle_deplacement = self.__orientation + omega * dt
            move_x = v * math.cos(angle_deplacement) * dt
            move_y = v * math.sin(angle_deplacement) * dt

            new_x = self.__x + move_x
            new_y = self.__y + move_y

            if not env.collision_obstacles(new_x, new_y, self.__rayon):
                self.__x = new_x
                self.__y = new_y
            else:
                # Fallback : essayer de contourner
                for angle_perturb in [0.5, -0.5, 1.0, -1.0, 1.5, -1.5]:
                    alt_angle = angle_deplacement + angle_perturb
                    alt_x = self.__x + math.cos(alt_angle) * self.__vitesse * dt * 0.5
                    alt_y = self.__y + math.sin(alt_angle) * self.__vitesse * dt * 0.5
                    if not env.collision_obstacles(alt_x, alt_y, self.__rayon):
                        self.__x = alt_x
                        self.__y = alt_y
                        break

        # --- Tir si armé ---
        if self.__arme and dist < 8.0:
            now = time.time()
            if now - self.__dernier_tir >= self.__cadence_tir:
                self.__dernier_tir = now
                angle = math.atan2(dy, dx) + random.uniform(-0.15, 0.15)
                proj = Projectile(
                    self.__x, self.__y, angle,
                    vitesse=6.0, degats=1, portee=8.0,
                    est_joueur=False, couleur=(0, 255, 0), taille=3
                )
                env.ajouter_projectile(proj)

    def _scan_rapide(self, env, nb_rayons=8, max_range=2.0):
        """Scan simplifié autour du zombie (mini-lidar pour la stratégie réactive)."""
        distances = []
        for i in range(nb_rayons):
            angle = self.__orientation + (i / nb_rayons) * 2 * math.pi - math.pi
            dx = math.cos(angle)
            dy = math.sin(angle)

            dist_min = max_range
            for obs in env.obstacles:
                t = obs.intersection_rayon(self.__x, self.__y, dx, dy, max_range)
                if t is not None and t < dist_min:
                    dist_min = t
            distances.append(dist_min)
        return distances

    def __str__(self):
        return f"Zombie({self.__x:.2f}, {self.__y:.2f}, pv={self.__pv})"
