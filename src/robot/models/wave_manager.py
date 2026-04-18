"""
Classe WaveManager - Gere les vagues de zombies.
Chaque vague apporte plus de zombies avec des armes plus dangereuses.
Adapte la difficulte selon la configuration choisie.
"""

import random
import math
import time
import logging

from robot.models.zombie import Zombie
from robot.models.difficulte import Difficulte

logger = logging.getLogger(__name__)


class WaveManager:
    """Gere la progression des vagues de zombies."""

    def __init__(self, config=None):
        self.__config = config or Difficulte.get_config(Difficulte.FACILE)
        self.__intervalle_vague = self.__config["intervalle_vague"]
        self.__vague_actuelle = 0
        self.__timer = 0.0
        self.__zombies_restants = 0
        self.__en_cours = False
        self.__score = 0
        self.__rl_agent = None  # agent RL partage (mode Impossible)

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

    @property
    def rl_agent(self):
        return self.__rl_agent

    def set_rl_agent(self, agent):
        """Definit l'agent RL partage (mode Impossible)."""
        self.__rl_agent = agent

    def demarrer(self):
        self.__en_cours = True
        self.__timer = self.__intervalle_vague - 3  # premiere vague apres 3s

    def mettre_a_jour(self, env, dt):
        """Met a jour le timer et lance de nouvelles vagues."""
        if not self.__en_cours:
            return

        self.__zombies_restants = len(env.zombies)
        self.__score = (self.__vague_actuelle * 100
                        + (self._nb_zombies_vague(self.__vague_actuelle) - self.__zombies_restants) * 10)

        self.__timer += dt
        if self.__timer >= self.__intervalle_vague:
            self.__timer = 0.0
            self.__vague_actuelle += 1
            self._lancer_vague(env)
            logger.info(f"Vague {self.__vague_actuelle} lancee!")

    def _nb_zombies_vague(self, vague):
        """Nombre de zombies pour une vague donnee."""
        return min(3 + vague * 2, self.__config["max_zombies_par_vague"])

    def _lancer_vague(self, env):
        """Cree les zombies pour la vague actuelle."""
        nb = self._nb_zombies_vague(self.__vague_actuelle)
        robot = env.robot
        cfg = self.__config

        for i in range(nb):
            # Spawn sur les bords de la map, loin du robot
            for _ in range(20):
                bord = random.randint(0, 3)
                if bord == 0:
                    x = random.uniform(0.5, env.largeur - 0.5)
                    y = env.hauteur - 0.5
                elif bord == 1:
                    x = random.uniform(0.5, env.largeur - 0.5)
                    y = 0.5
                elif bord == 2:
                    x = 0.5
                    y = random.uniform(0.5, env.hauteur - 0.5)
                else:
                    x = env.largeur - 0.5
                    y = random.uniform(0.5, env.hauteur - 0.5)

                if robot:
                    dx = x - robot.x
                    dy = y - robot.y
                    if math.sqrt(dx * dx + dy * dy) > 3.0:
                        break

            # Stats selon la difficulte
            base_vitesse = 0.8 + self.__vague_actuelle * 0.1 + random.uniform(-0.2, 0.2)
            vitesse = min(base_vitesse * cfg["zombie_vitesse_mult"], 4.0)
            pv = int((30 + self.__vague_actuelle * 10) * cfg["zombie_pv_mult"])

            # Arme
            arme = None
            if (self.__vague_actuelle >= cfg["vague_arme_zombie"]
                    and random.random() < cfg["prob_arme_zombie"]):
                arme = "lance_flamme"

            zombie = Zombie(x, y, vitesse=vitesse, pv=pv, arme=arme,
                            rl_agent=self.__rl_agent if cfg["use_rl"] else None)
            env.ajouter_zombie(zombie)

        logger.info(f"Vague {self.__vague_actuelle}: {nb} zombies "
                     f"(PV: {int((30 + self.__vague_actuelle * 10) * cfg['zombie_pv_mult'])})")
