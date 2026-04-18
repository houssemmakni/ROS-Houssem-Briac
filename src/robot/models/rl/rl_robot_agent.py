"""
Classe RLRobotAgent - Agent Q-learning pour le robot joueur en mode auto-play.
Le robot apprend TOUT par lui-meme : deplacement, choix d'arme, et utilise le LIDAR.

Etat discretise (integre les donnees Lidar) :
  - Angle vers le zombie le plus proche : 8 bins
  - Distance au zombie le plus proche : 4 bins (contact, proche, moyen, loin)
  - Nombre de zombies proches (<3m) : 3 bins (0, 1-2, 3+)
  - Niveau de PV : 3 bins (haut >66%, moyen 33-66%, bas <33%)
  - Obstacle devant (Lidar, direction du mouvement) : 2 bins (libre, bloque)
  - Espace libre moyen (Lidar) : 2 bins (confine, ouvert)
  Total : 8 x 4 x 3 x 3 x 2 x 2 = 1152 etats

Actions : (9 mouvements) x (4 armes) = 36 actions

Le Lidar permet au robot d'apprendre a :
  - Eviter les murs et obstacles
  - Se refugier pres des couvertures quand il a peu de PV
  - Fuir dans les espaces ouverts quand il est encercle
"""

import math
import random
import numpy as np


class RLRobotAgent:
    """Agent Q-learning pour le robot joueur.
    Utilise le Lidar pour percevoir les obstacles."""

    NB_ANGLE_BINS = 8
    NB_DIST_BINS = 4
    NB_NEARBY_BINS = 3
    NB_PV_BINS = 3
    NB_OBSTACLE_BINS = 2   # obstacle devant : libre / bloque
    NB_ESPACE_BINS = 2     # espace moyen lidar : confine / ouvert
    NB_ETATS = (NB_ANGLE_BINS * NB_DIST_BINS * NB_NEARBY_BINS
                * NB_PV_BINS * NB_OBSTACLE_BINS * NB_ESPACE_BINS)  # 1152

    NB_MOUVEMENTS = 9   # 8 directions + rester
    NB_ARMES = 4
    NB_ACTIONS = NB_MOUVEMENTS * NB_ARMES  # 36

    DIRECTIONS = [i * (2 * math.pi / 8) for i in range(8)] + [None]

    def __init__(self, alpha=0.12, gamma=0.95, epsilon_start=0.4,
                 epsilon_min=0.03, epsilon_decay=0.9998):
        self.__q_table = np.zeros((self.NB_ETATS, self.NB_ACTIONS))
        self.__alpha = alpha
        self.__gamma = gamma
        self.__epsilon = epsilon_start
        self.__epsilon_min = epsilon_min
        self.__epsilon_decay = epsilon_decay
        self.__total_updates = 0
        self.__kills = 0

    @property
    def epsilon(self):
        return self.__epsilon

    @property
    def total_updates(self):
        return self.__total_updates

    @property
    def kills(self):
        return self.__kills

    def ajouter_kill(self):
        self.__kills += 1

    def discretiser_etat(self, angle_zombie, dist_zombie, nb_proches, ratio_pv,
                         obstacle_devant=False, espace_confine=False):
        """Convertit les observations (dont Lidar) en index d'etat discret."""
        # 1. Angle vers le zombie le plus proche (8 bins)
        if angle_zombie is None:
            bin_angle = 0
        else:
            angle_norm = angle_zombie % (2 * math.pi)
            bin_angle = int(angle_norm / (2 * math.pi / self.NB_ANGLE_BINS))
            bin_angle = min(bin_angle, self.NB_ANGLE_BINS - 1)

        # 2. Distance (4 bins)
        if dist_zombie is None or dist_zombie > 10:
            bin_dist = 3
        elif dist_zombie < 1.5:
            bin_dist = 0
        elif dist_zombie < 4.0:
            bin_dist = 1
        else:
            bin_dist = 2

        # 3. Nombre de zombies proches (3 bins)
        if nb_proches == 0:
            bin_nearby = 0
        elif nb_proches <= 2:
            bin_nearby = 1
        else:
            bin_nearby = 2

        # 4. Niveau de PV (3 bins)
        if ratio_pv > 0.66:
            bin_pv = 0
        elif ratio_pv > 0.33:
            bin_pv = 1
        else:
            bin_pv = 2

        # 5. Obstacle devant - donnee LIDAR (2 bins)
        bin_obs = 1 if obstacle_devant else 0

        # 6. Espace confine - donnee LIDAR (2 bins)
        bin_espace = 1 if espace_confine else 0

        etat = (((((bin_angle * self.NB_DIST_BINS + bin_dist)
                    * self.NB_NEARBY_BINS + bin_nearby)
                   * self.NB_PV_BINS + bin_pv)
                  * self.NB_OBSTACLE_BINS + bin_obs)
                 * self.NB_ESPACE_BINS + bin_espace)
        return min(etat, self.NB_ETATS - 1)

    @staticmethod
    def analyser_lidar(lidar_distances, orientation, angle_mouvement=None):
        """Analyse les distances Lidar pour extraire des features utiles.

        Parametres:
            lidar_distances: liste des distances mesurees par le Lidar
            orientation: orientation actuelle du robot
            angle_mouvement: direction de mouvement prevue (optionnel)

        Retourne:
            obstacle_devant (bool): obstacle a moins de 1.5m devant
            espace_confine (bool): distance moyenne < 3m (coincer entre des murs)
            direction_libre (float): angle de la direction la plus libre
        """
        if not lidar_distances:
            return False, False, 0.0

        nb = len(lidar_distances)

        # Obstacle devant (dans la direction de mouvement ou du robot)
        angle_ref = angle_mouvement if angle_mouvement is not None else orientation
        obstacle_devant = False
        for i in range(nb):
            angle_rayon = (i / nb) * 2 * math.pi + orientation - math.pi
            diff = abs(angle_rayon - angle_ref)
            if diff > math.pi:
                diff = 2 * math.pi - diff
            # Rayons dans un cone de 45 degres devant
            if diff < math.pi / 4:
                if lidar_distances[i] < 1.5:
                    obstacle_devant = True
                    break

        # Espace confine (moyenne des distances < 3m = coincer)
        moyenne = sum(lidar_distances) / nb
        espace_confine = moyenne < 3.0

        # Direction la plus libre (angle du rayon le plus long)
        max_dist = max(lidar_distances)
        idx_libre = lidar_distances.index(max_dist)
        direction_libre = (idx_libre / nb) * 2 * math.pi + orientation - math.pi

        return obstacle_devant, espace_confine, direction_libre

    def choisir_action(self, etat):
        """Epsilon-greedy sur les 36 actions."""
        if random.random() < self.__epsilon:
            return random.randint(0, self.NB_ACTIONS - 1)
        return int(np.argmax(self.__q_table[etat]))

    def decoder_action(self, action):
        """Decode une action en (index_mouvement, index_arme)."""
        mouvement = action // self.NB_ARMES
        arme = action % self.NB_ARMES
        return mouvement, arme

    def get_direction(self, action):
        """Retourne l'angle de deplacement."""
        mouvement, _ = self.decoder_action(action)
        return self.DIRECTIONS[mouvement]

    def get_arme(self, action):
        """Retourne l'index de l'arme."""
        _, arme = self.decoder_action(action)
        return arme

    def mettre_a_jour(self, etat, action, recompense, etat_suivant):
        """Equation de Bellman."""
        q_actuel = self.__q_table[etat, action]
        q_max_suivant = np.max(self.__q_table[etat_suivant])
        self.__q_table[etat, action] = q_actuel + self.__alpha * (
            recompense + self.__gamma * q_max_suivant - q_actuel
        )
        self.__total_updates += 1
        if self.__epsilon > self.__epsilon_min:
            self.__epsilon *= self.__epsilon_decay

    def calculer_recompense(self, ancien_pv, nouveau_pv, ancien_nb_zombies,
                            nouveau_nb_zombies, est_mort, collision_mur=False):
        """Recompense pour le robot.
        +50  : tuer un zombie
        +1   : survivre un pas de temps
        -10  : prendre des degats
        -100 : mourir
        -3   : foncer dans un mur (apprend a utiliser le Lidar)
        """
        recompense = 1.0

        if est_mort:
            return -100.0

        if nouveau_pv < ancien_pv:
            recompense -= 10.0

        if collision_mur:
            recompense -= 3.0

        kills = ancien_nb_zombies - nouveau_nb_zombies
        if kills > 0:
            recompense += kills * 50.0

        return recompense

    def sauvegarder(self, chemin):
        np.savez(chemin,
                 q_table=self.__q_table,
                 epsilon=np.array([self.__epsilon]),
                 total_updates=np.array([self.__total_updates]),
                 kills=np.array([self.__kills]))

    def charger(self, chemin):
        data = np.load(chemin)
        q = data["q_table"]
        # Si l'ancienne sauvegarde a une taille differente, ignorer
        if q.shape == self.__q_table.shape:
            self.__q_table = q
            self.__epsilon = float(data["epsilon"][0])
            self.__total_updates = int(data["total_updates"][0])
            self.__kills = int(data["kills"][0])

    def __str__(self):
        return (f"RLRobotAgent(updates={self.__total_updates}, "
                f"epsilon={self.__epsilon:.3f}, kills={self.__kills}, "
                f"etats={self.NB_ETATS}, actions={self.NB_ACTIONS})")
