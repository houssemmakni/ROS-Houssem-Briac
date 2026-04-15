"""
Classe FreeDirectionStrategy - Évitement directionnel.
Détecte de quel côté l'espace est le plus libre et tourne vers ce côté.
"""

from robot.controllers.strategy import Strategy


class FreeDirectionStrategy(Strategy):
    """Stratégie d'évitement directionnel : tourne vers le côté le plus libre."""

    def __init__(self, seuil_distance=1.5, vitesse=1.0, vitesse_rotation=2.0):
        self.__seuil = seuil_distance
        self.__vitesse = vitesse
        self.__vitesse_rotation = vitesse_rotation

    def compute_command(self, observation):
        distances = observation.get("lidar_distances", [])
        if not distances:
            return {"v": self.__vitesse, "omega": 0.0}

        nb = len(distances)
        moitie = nb // 2

        # Comparer moyenne des distances gauche / droite
        gauche = distances[:moitie]
        droite = distances[moitie:]

        moyenne_gauche = sum(gauche) / len(gauche) if gauche else 0
        moyenne_droite = sum(droite) / len(droite) if droite else 0

        # Rayons devant
        front_start = nb // 4
        front_end = 3 * nb // 4
        front_distances = distances[front_start:front_end]

        # Si obstacle proche devant, tourner vers le côté le plus libre
        if front_distances and min(front_distances) < self.__seuil:
            if moyenne_gauche > moyenne_droite:
                return {"v": 0.2, "omega": self.__vitesse_rotation}
            else:
                return {"v": 0.2, "omega": -self.__vitesse_rotation}

        return {"v": self.__vitesse, "omega": 0.0}
