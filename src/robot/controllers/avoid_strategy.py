"""
Classe AvoidStrategy - Évitement simple d'obstacles.
Si obstacle proche devant : tourner. Sinon : avancer.
"""

from robot.controllers.strategy import Strategy


class AvoidStrategy(Strategy):
    """Stratégie d'évitement simple : tourne si obstacle devant, avance sinon."""

    def __init__(self, seuil_distance=1.5, vitesse=1.0, vitesse_rotation=2.0):
        self.__seuil = seuil_distance
        self.__vitesse = vitesse
        self.__vitesse_rotation = vitesse_rotation

    def compute_command(self, observation):
        distances = observation.get("lidar_distances", [])
        if not distances:
            return {"v": self.__vitesse, "omega": 0.0}

        nb = len(distances)
        # Rayons devant le robot (centre du tableau)
        front_start = nb // 4
        front_end = 3 * nb // 4
        front_distances = distances[front_start:front_end]

        # Si obstacle proche devant
        if front_distances and min(front_distances) < self.__seuil:
            return {"v": 0.0, "omega": self.__vitesse_rotation}

        return {"v": self.__vitesse, "omega": 0.0}
