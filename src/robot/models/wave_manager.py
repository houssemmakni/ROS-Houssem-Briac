"""
Classe WaveManager - Gère les vagues de zombies.
Chaque vague apporte plus de zombies avec des armes plus dangereuses.
"""

import random
import math
import time
import logging

from robot.models.zombie import Zombie

logger = logging.getLogger(__name__)


class WaveManager:
    """Gère la progression des vagues de zombies."""

    def __init__(self, intervalle_vague=15.0):
        self.__vague_actuelle = 0
        self.__intervalle_vague = intervalle_vague
        self.__timer = 0.0
        self.__zombies_restants = 0
        self.__en_cours = False
        self.__score = 0
        self.__temps_debut_vague = 0.0

    @property
    def vague_actuelle(self):
        return self.__vague_actuelle

    @property
    def score(self):
        return self.__score

    @property
    def en_cours(self):
        return self.__en_cours

    @property
    def timer(self):
        return max(0, self.__intervalle_vague - self.__timer)

    @property
    def zombies_restants(self):
        return self.__zombies_restants

    def demarrer(self):
        self.__en_cours = True
        self.__timer = self.__intervalle_vague - 3  # première vague après 3s
        self.__temps_debut_vague = time.time()

    def mettre_a_jour(self, env, dt):
        """Met à jour le timer et lance de nouvelles vagues."""
        if not self.__en_cours:
            return

        # Compter les zombies vivants
        self.__zombies_restants = len(env.zombies)

        # Mettre à jour le score (zombies tués)
        self.__score = self.__vague_actuelle * 100 + (self._nb_zombies_vague(self.__vague_actuelle) - self.__zombies_restants) * 10

        # Timer pour la prochaine vague
        self.__timer += dt
        if self.__timer >= self.__intervalle_vague:
            self.__timer = 0.0
            self.__vague_actuelle += 1
            self._lancer_vague(env)
            logger.info(f"Vague {self.__vague_actuelle} lancée!")

    def _nb_zombies_vague(self, vague):
        """Nombre de zombies pour une vague donnée."""
        return min(3 + vague * 2, 25)

    def _lancer_vague(self, env):
        """Crée les zombies pour la vague actuelle."""
        nb = self._nb_zombies_vague(self.__vague_actuelle)
        robot = env.robot

        for i in range(nb):
            # Spawn sur les bords de la map, loin du robot
            for _ in range(20):
                bord = random.randint(0, 3)
                if bord == 0:  # haut
                    x = random.uniform(0.5, env.largeur - 0.5)
                    y = env.hauteur - 0.5
                elif bord == 1:  # bas
                    x = random.uniform(0.5, env.largeur - 0.5)
                    y = 0.5
                elif bord == 2:  # gauche
                    x = 0.5
                    y = random.uniform(0.5, env.hauteur - 0.5)
                else:  # droite
                    x = env.largeur - 0.5
                    y = random.uniform(0.5, env.hauteur - 0.5)

                # Vérifier distance au robot (spawn pas trop proche)
                if robot:
                    dx = x - robot.x
                    dy = y - robot.y
                    if math.sqrt(dx * dx + dy * dy) > 3.0:
                        break

            # Difficulté progressive
            vitesse = 0.8 + self.__vague_actuelle * 0.1 + random.uniform(-0.2, 0.2)
            vitesse = min(vitesse, 3.0)
            pv = 30 + self.__vague_actuelle * 10

            # Arme pour les zombies (à partir de la vague 5)
            arme = None
            if self.__vague_actuelle >= 5 and random.random() < 0.4:
                arme = "lance_flamme"

            zombie = Zombie(x, y, vitesse=vitesse, pv=pv, arme=arme)
            env.ajouter_zombie(zombie)

        logger.info(f"Vague {self.__vague_actuelle}: {nb} zombies (PV: {30 + self.__vague_actuelle * 10})")
