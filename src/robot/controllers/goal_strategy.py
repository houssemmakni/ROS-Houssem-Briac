"""
Classe GoalStrategy - Navigation vers un objectif avec évitement d'obstacles.
Combine attraction vers la cible et répulsion des obstacles.
"""

import math

from robot.controllers.strategy import Strategy


class GoalStrategy(Strategy):
    """Stratégie de navigation vers un objectif avec évitement réactif."""

    def __init__(self, goal, seuil_obstacle=1.5, k_attraction=1.5, k_repulsion=2.0):
        self.__goal = goal  # (x, y) cible
        self.__seuil = seuil_obstacle
        self.__k_attraction = k_attraction
        self.__k_repulsion = k_repulsion

    @property
    def goal(self):
        return self.__goal

    @goal.setter
    def goal(self, value):
        self.__goal = value

    def compute_command(self, observation):
        x = observation["x"]
        y = observation["y"]
        theta = observation["orientation"]
        distances = observation.get("lidar_distances", [])

        # --- Attraction vers la cible ---
        dx = self.__goal[0] - x
        dy = self.__goal[1] - y
        dist_goal = math.sqrt(dx * dx + dy * dy)

        if dist_goal < 0.3:
            return {"v": 0.0, "omega": 0.0}

        theta_goal = math.atan2(dy, dx)
        e_theta = theta_goal - theta
        while e_theta > math.pi:
            e_theta -= 2 * math.pi
        while e_theta < -math.pi:
            e_theta += 2 * math.pi

        v_attraction = self.__k_attraction * min(dist_goal, 2.0)
        omega_attraction = self.__k_attraction * e_theta

        # --- Répulsion des obstacles ---
        omega_repulsion = 0.0
        v_repulsion = 0.0

        if distances:
            nb = len(distances)
            for i, d in enumerate(distances):
                if d < self.__seuil:
                    # Angle du rayon par rapport au robot
                    angle_rayon = (i / nb) * 2 * math.pi - math.pi
                    force = (self.__seuil - d) / self.__seuil
                    # Répulsion : tourner dans le sens opposé au rayon
                    omega_repulsion -= self.__k_repulsion * force * math.sin(angle_rayon)
                    v_repulsion -= self.__k_repulsion * force * 0.3 * max(0, math.cos(angle_rayon))

        v = max(0.0, v_attraction + v_repulsion)
        omega = omega_attraction + omega_repulsion

        return {"v": v, "omega": omega}
