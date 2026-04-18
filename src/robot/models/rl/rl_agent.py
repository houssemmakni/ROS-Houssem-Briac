"""
Classe RLAgent - Agent d'apprentissage par renforcement (Q-learning).
Les zombies apprennent en temps reel a traquer le robot.

Principe (cours slide 11) :
  1. Observer l'etat (distances lidar, position relative)
  2. Choisir une action (direction) via la politique (Q-table)
  3. Recevoir une recompense (+proche du robot, -collision obstacle)
  4. Mettre a jour le modele (equation de Bellman)
  Repete a chaque frame -> comportement de plus en plus optimal.

Etat discretise :
  - Angle relatif vers le robot : 8 bins (N, NE, E, SE, S, SW, W, NW)
  - Distance au robot : 4 bins (contact, proche, moyen, loin)
  - Obstacle devant : 2 bins (bloque / libre)
  Total : 8 x 4 x 2 = 64 etats

Actions : 8 directions de deplacement

Q-table : matrice 64 x 8 partagee entre tous les zombies.
"""

import math
import random
import numpy as np


class RLAgent:
    """Agent Q-learning partage entre tous les zombies du mode Impossible."""

    NB_ANGLE_BINS = 8
    NB_DIST_BINS = 4
    NB_OBSTACLE_BINS = 2
    NB_ETATS = NB_ANGLE_BINS * NB_DIST_BINS * NB_OBSTACLE_BINS  # 64
    NB_ACTIONS = 8  # 8 directions

    # Directions d'action (angles en radians)
    DIRECTIONS = [i * (2 * math.pi / 8) for i in range(8)]

    def __init__(self, alpha=0.15, gamma=0.9, epsilon_start=0.5, epsilon_min=0.05, epsilon_decay=0.9995):
        # Q-table initialisee a zero
        self.__q_table = np.zeros((self.NB_ETATS, self.NB_ACTIONS))
        self.__alpha = alpha           # taux d'apprentissage
        self.__gamma = gamma           # facteur de discount
        self.__epsilon = epsilon_start # exploration (decroit avec le temps)
        self.__epsilon_min = epsilon_min
        self.__epsilon_decay = epsilon_decay
        self.__total_updates = 0

    @property
    def epsilon(self):
        return self.__epsilon

    @property
    def total_updates(self):
        return self.__total_updates

    @property
    def q_table(self):
        return self.__q_table.copy()

    def discretiser_etat(self, angle_rel, distance, obstacle_devant):
        """Convertit les observations continues en un index d'etat discret."""
        # 1. Angle relatif -> 8 bins
        angle_norm = angle_rel % (2 * math.pi)
        bin_angle = int(angle_norm / (2 * math.pi / self.NB_ANGLE_BINS))
        bin_angle = min(bin_angle, self.NB_ANGLE_BINS - 1)

        # 2. Distance -> 4 bins
        if distance < 1.0:
            bin_dist = 0    # contact
        elif distance < 3.0:
            bin_dist = 1    # proche
        elif distance < 7.0:
            bin_dist = 2    # moyen
        else:
            bin_dist = 3    # loin

        # 3. Obstacle devant -> 2 bins
        bin_obs = 1 if obstacle_devant else 0

        # Index lineaire
        etat = (bin_angle * self.NB_DIST_BINS + bin_dist) * self.NB_OBSTACLE_BINS + bin_obs
        return min(etat, self.NB_ETATS - 1)

    def choisir_action(self, etat):
        """Choisit une action avec epsilon-greedy (exploration vs exploitation)."""
        if random.random() < self.__epsilon:
            return random.randint(0, self.NB_ACTIONS - 1)
        else:
            return int(np.argmax(self.__q_table[etat]))

    def mettre_a_jour(self, etat, action, recompense, etat_suivant):
        """Met a jour la Q-table avec l'equation de Bellman.

        Q(s,a) = Q(s,a) + alpha * [recompense + gamma * max(Q(s',a')) - Q(s,a)]
        """
        q_actuel = self.__q_table[etat, action]
        q_max_suivant = np.max(self.__q_table[etat_suivant])

        # Equation de Bellman
        self.__q_table[etat, action] = q_actuel + self.__alpha * (
            recompense + self.__gamma * q_max_suivant - q_actuel
        )

        # Decroissance de l'exploration
        self.__total_updates += 1
        if self.__epsilon > self.__epsilon_min:
            self.__epsilon *= self.__epsilon_decay

    def calculer_recompense(self, ancienne_dist, nouvelle_dist, collision_obstacle, touche_robot):
        """Calcule la recompense pour la transition.

        Recompenses :
          +10  : touche le robot (objectif principal)
          +1   : se rapproche du robot
          -1   : s'eloigne du robot
          -5   : collision avec un obstacle
          -0.1 : penalite par pas de temps (encourage l'efficacite)
        """
        recompense = -0.1  # penalite de base

        if touche_robot:
            recompense += 10.0
        elif collision_obstacle:
            recompense -= 5.0
        else:
            # Recompense proportionnelle au rapprochement
            delta = ancienne_dist - nouvelle_dist
            if delta > 0:
                recompense += 1.0
            else:
                recompense -= 1.0

        return recompense

    def get_direction_angle(self, action):
        """Retourne l'angle de deplacement pour une action donnee."""
        return self.DIRECTIONS[action]

    def sauvegarder(self, chemin):
        """Sauvegarde la Q-table et les parametres sur disque."""
        np.savez(chemin,
                 q_table=self.__q_table,
                 epsilon=np.array([self.__epsilon]),
                 total_updates=np.array([self.__total_updates]))

    def charger(self, chemin):
        """Charge la Q-table et les parametres depuis le disque."""
        data = np.load(chemin)
        self.__q_table = data["q_table"]
        self.__epsilon = float(data["epsilon"][0])
        self.__total_updates = int(data["total_updates"][0])

    def __str__(self):
        return (f"RLAgent(updates={self.__total_updates}, "
                f"epsilon={self.__epsilon:.3f}, "
                f"q_mean={np.mean(np.abs(self.__q_table)):.3f})")
