"""
Classe Zombie - Ennemi intelligent qui poursuit le robot.
Utilise un vrai Lidar (Capteur) pour detecter les obstacles,
A* pour le pathfinding et le Strategy Pattern pour le comportement.
"""

import math
import random
import time
import logging

from robot.models.armes.projectile import Projectile
from robot.models.capteurs.lidar import Lidar
from robot.controllers.navigator import Navigator
from robot.controllers.goal_strategy import GoalStrategy

logger = logging.getLogger(__name__)


class _ZombieLidarProxy:
    """Proxy minimal pour que le Lidar puisse lire la position du zombie.
    Le Lidar attend un objet avec x, y, orientation."""

    def __init__(self, zombie):
        self._zombie = zombie

    @property
    def x(self):
        return self._zombie.x

    @property
    def y(self):
        return self._zombie.y

    @property
    def orientation(self):
        return self._zombie.orientation


class Zombie:
    """Un zombie avec IA intelligente : Lidar + A* + Strategy pattern."""

    def __init__(self, x, y, vitesse=1.0, pv=50, rayon=0.3, arme=None, rl_agent=None):
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
        self.__rl_agent = rl_agent

        # Vrai capteur Lidar (herite de Capteur ABC)
        self.__lidar_proxy = _ZombieLidarProxy(self)
        self.__lidar = Lidar(self.__lidar_proxy, nb_rayons=12, max_range=4.0)

        # Navigation : RLStrategy (mode Impossible) ou GoalStrategy (normal)
        if rl_agent is not None:
            from robot.controllers.rl_strategy import RLStrategy
            self.__strategy = RLStrategy(rl_agent, vitesse=vitesse)
        else:
            self.__strategy = GoalStrategy(goal=(x, y), seuil_obstacle=1.0,
                                           k_attraction=1.0, k_repulsion=1.5)
        self.__navigator = Navigator(self.__strategy)

        # A* pathfinding
        self.__chemin = []
        self.__chemin_index = 0
        self.__timer_recalcul = 0.0
        self.__intervalle_recalcul = 0.5

        # Detection de blocage
        self.__derniere_pos = (x, y)
        self.__timer_blocage = 0.0

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
        return self.__chemin

    @property
    def lidar(self):
        """Acces au capteur Lidar du zombie."""
        return self.__lidar

    def subir_degat(self, degats):
        self.__pv -= degats
        if self.__pv <= 0:
            self.__pv = 0
            logger.debug(f"Zombie elimine a ({self.__x:.2f}, {self.__y:.2f})")

    def mettre_a_jour(self, env, dt, grille=None, planificateur=None):
        """Met a jour le zombie : Lidar scan + A* + navigation reactive + tir."""
        robot = env.robot
        if not robot or not robot.est_vivant:
            return

        dx = robot.x - self.__x
        dy = robot.y - self.__y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0.01:
            self.__orientation = math.atan2(dy, dx)

        # --- Scanner avec le vrai Lidar ---
        lidar_distances = self.__lidar.lire(env)

        # --- Detection de blocage ---
        dx_pos = self.__x - self.__derniere_pos[0]
        dy_pos = self.__y - self.__derniere_pos[1]
        deplacement = math.sqrt(dx_pos * dx_pos + dy_pos * dy_pos)
        self.__derniere_pos = (self.__x, self.__y)

        if deplacement < 0.005:
            self.__timer_blocage += dt
        else:
            self.__timer_blocage = 0.0

        est_bloque = self.__timer_blocage > 0.3

        # --- Pathfinding A* (si grille disponible) ---
        self.__timer_recalcul += dt
        cible_x, cible_y = robot.x, robot.y

        # Recalcul A* normal ou force si bloque
        besoin_recalcul = self.__timer_recalcul >= self.__intervalle_recalcul or est_bloque
        if planificateur and grille and besoin_recalcul:
            self.__timer_recalcul = 0.0
            self.__timer_blocage = 0.0
            chemin = planificateur.trouver_chemin(
                (self.__x, self.__y), (robot.x, robot.y)
            )
            if chemin and len(chemin) > 1:
                self.__chemin = chemin
                self.__chemin_index = 1

        # Suivre le chemin A* : look-ahead reduit pres des obstacles
        if self.__chemin and self.__chemin_index < len(self.__chemin):
            # Lidar detecte un obstacle proche ? look-ahead = 1 (suivi precis)
            # Sinon look-ahead = 3 (mouvement fluide)
            min_lidar = min(lidar_distances) if lidar_distances else 99
            look_dist = 1 if min_lidar < 2.0 else 3
            look_ahead = min(self.__chemin_index + look_dist, len(self.__chemin) - 1)
            cible_x, cible_y = self.__chemin[look_ahead]

            wx, wy = self.__chemin[self.__chemin_index]
            d_wp = math.sqrt((self.__x - wx) ** 2 + (self.__y - wy) ** 2)
            if d_wp < 0.5:
                self.__chemin_index += 1

        # --- Calcul de la direction de deplacement ---
        has_astar_path = self.__chemin and self.__chemin_index < len(self.__chemin)

        if has_astar_path:
            # MODE A* : suivre directement le waypoint (pas de GoalStrategy qui lutte)
            angle_deplacement = math.atan2(cible_y - self.__y, cible_x - self.__x)
            v = self.__vitesse
        else:
            # PAS DE CHEMIN : utiliser la Strategy (GoalStrategy / RLStrategy)
            if hasattr(self.__strategy, 'goal'):
                self.__strategy.goal = (cible_x, cible_y)

            observation = {
                "x": self.__x,
                "y": self.__y,
                "orientation": self.__orientation,
                "lidar_distances": lidar_distances,
                "robot_x": robot.x,
                "robot_y": robot.y,
            }
            cmd = self.__navigator.step(observation)
            v = min(cmd.get("v", 0), self.__vitesse)
            omega = cmd.get("omega", 0)
            angle_deplacement = self.__orientation + omega * dt

        # --- Lidar : repulsion des murs proches ---
        # Si un rayon Lidar est tres court, pousser le zombie dans la direction opposee
        repulsion_x, repulsion_y = 0.0, 0.0
        if lidar_distances:
            nb = len(lidar_distances)
            for i in range(nb):
                d = lidar_distances[i]
                if d < 1.0:  # mur detecte a moins de 1m
                    angle_rayon = self.__orientation + (i / nb) * 2 * math.pi - math.pi
                    force = (1.0 - d) * 2.0  # plus c'est proche, plus la repulsion est forte
                    repulsion_x -= math.cos(angle_rayon) * force
                    repulsion_y -= math.sin(angle_rayon) * force

        # Si PAS de chemin A*, utiliser aussi le Lidar pour rediriger
        if not has_astar_path and lidar_distances and dist > self.__rayon + robot.rayon + 0.1:
            nb = len(lidar_distances)
            bloque = False
            for i in range(nb):
                angle_rayon = self.__orientation + (i / nb) * 2 * math.pi - math.pi
                diff_angle = abs(angle_rayon - angle_deplacement)
                if diff_angle > math.pi:
                    diff_angle = 2 * math.pi - diff_angle
                if diff_angle < math.pi / 4 and lidar_distances[i] < 0.8:
                    bloque = True
                    break
            if bloque:
                max_dist = max(lidar_distances)
                idx_libre = lidar_distances.index(max_dist)
                angle_deplacement = self.__orientation + (idx_libre / nb) * 2 * math.pi - math.pi

        # --- Deplacement (direction A*/Strategy + repulsion murs Lidar) ---
        if dist > self.__rayon + robot.rayon + 0.1:
            move_x = v * math.cos(angle_deplacement) * dt + repulsion_x * dt
            move_y = v * math.sin(angle_deplacement) * dt + repulsion_y * dt

            new_x = self.__x + move_x
            new_y = self.__y + move_y

            if not env.collision_obstacles(new_x, new_y, self.__rayon):
                self.__x = new_x
                self.__y = new_y
            else:
                # Fallback : utiliser le Lidar pour trouver une direction libre
                if lidar_distances:
                    nb = len(lidar_distances)
                    # Trier les directions par distance (plus libre en premier)
                    indices = sorted(range(nb), key=lambda i: lidar_distances[i], reverse=True)
                    for idx in indices[:4]:
                        alt_angle = self.__orientation + (idx / nb) * 2 * math.pi - math.pi
                        alt_x = self.__x + math.cos(alt_angle) * self.__vitesse * dt * 0.5
                        alt_y = self.__y + math.sin(alt_angle) * self.__vitesse * dt * 0.5
                        if not env.collision_obstacles(alt_x, alt_y, self.__rayon):
                            self.__x = alt_x
                            self.__y = alt_y
                            break

        # --- Tir si arme ---
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

    def __str__(self):
        return f"Zombie({self.__x:.2f}, {self.__y:.2f}, pv={self.__pv})"
