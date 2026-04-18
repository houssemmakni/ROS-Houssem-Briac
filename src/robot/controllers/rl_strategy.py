"""
Classe RLStrategy - Strategie de navigation par apprentissage par renforcement.
Utilise un RLAgent (Q-learning) partage pour decider des actions.
Chaque zombie qui utilise cette strategie contribue a l'apprentissage collectif.
"""

import math

from robot.controllers.strategy import Strategy


class RLStrategy(Strategy):
    """Strategie de navigation basee sur le Q-learning.
    Les zombies apprennent collectivement a traquer le robot."""

    def __init__(self, rl_agent, vitesse=1.5):
        self.__agent = rl_agent
        self.__vitesse = vitesse
        self.__dernier_etat = None
        self.__derniere_action = None
        self.__derniere_dist = None

    @property
    def agent(self):
        return self.__agent

    def compute_command(self, observation):
        """Choisit une action via le Q-learning et met a jour l'agent.

        observation doit contenir :
          - x, y, orientation : pose du zombie
          - robot_x, robot_y : position du robot
          - lidar_distances : distances obstacles (mini-lidar)
        """
        zx = observation["x"]
        zy = observation["y"]
        rx = observation.get("robot_x", zx)
        ry = observation.get("robot_y", zy)
        distances = observation.get("lidar_distances", [])

        # Calcul de l'angle relatif et de la distance au robot
        dx = rx - zx
        dy = ry - zy
        dist_robot = math.sqrt(dx * dx + dy * dy)
        angle_vers_robot = math.atan2(dy, dx)
        if angle_vers_robot < 0:
            angle_vers_robot += 2 * math.pi

        # Obstacle devant (dans la direction du robot)
        obstacle_devant = False
        if distances:
            nb = len(distances)
            # L'index du rayon le plus proche de la direction du robot
            angle_zombie = observation.get("orientation", 0)
            angle_rel_devant = (angle_vers_robot - angle_zombie) % (2 * math.pi)
            idx = int(angle_rel_devant / (2 * math.pi) * nb) % nb
            if distances[idx] < 1.5:
                obstacle_devant = True

        # Discretiser l'etat
        etat = self.__agent.discretiser_etat(angle_vers_robot, dist_robot, obstacle_devant)

        # Apprentissage : mettre a jour la Q-table avec la transition precedente
        if self.__dernier_etat is not None:
            collision_obstacle = obstacle_devant and dist_robot >= self.__derniere_dist
            touche_robot = dist_robot < 0.8

            recompense = self.__agent.calculer_recompense(
                self.__derniere_dist, dist_robot, collision_obstacle, touche_robot
            )
            self.__agent.mettre_a_jour(
                self.__dernier_etat, self.__derniere_action, recompense, etat
            )

        # Choisir une action
        action = self.__agent.choisir_action(etat)

        # Sauvegarder pour la prochaine mise a jour
        self.__dernier_etat = etat
        self.__derniere_action = action
        self.__derniere_dist = dist_robot

        # Convertir l'action en commande (v, omega)
        angle_action = self.__agent.get_direction_angle(action)

        # L'angle d'action est absolu, on calcule omega pour tourner vers cette direction
        angle_zombie = observation.get("orientation", 0)
        e_theta = angle_action - angle_zombie
        while e_theta > math.pi:
            e_theta -= 2 * math.pi
        while e_theta < -math.pi:
            e_theta += 2 * math.pi

        return {"v": self.__vitesse, "omega": e_theta * 3.0}
